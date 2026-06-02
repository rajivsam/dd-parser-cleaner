"""Assistant module for generating cleaning recommendations based on data profile and dictionary."""

import json
import logging
import pandas as pd
import yaml
import httpx
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console

class CleaningAssistant:
    """
    Analyzes dataset physics and semantics to suggest cleaning strategies.

    Attributes:
        config (dict): Project configuration.
        profile_path (Path): Source profile data.
        dd_path (Path): Source dictionary data.
        recommendations (list): Compiled suggested actions.
    """

    def __init__(self, config: Dict[str, Any], profile_path: Path, dd_path: Path):
        """Initializes the Assistant with required data sources."""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.profile_path = profile_path
        self.dd_path = dd_path
        self.console = Console()
        self.recommendations = []
        self.prompts = self.config.get("cleaner", {}).get("missing_values", {}).get("prompts", {}).get("cleaning_assistant", {})
        self.model_name = self.config.get("model_name", "llama3.2")
        self.llm_timeout = float(self.config.get("llm_timeout", 180.0))

    def generate_recommendations(self) -> Dict[str, Any]:
        """
        Core heuristic engine to map columns to actions.

        Returns:
            Dict[str, Any]: Mapping of attributes to recommended strategies.
        """
        if not self.profile_path.exists() or not self.dd_path.exists():
            if not self.profile_path.exists():
                self.console.print(f"[yellow]⚠️ Profile report not found at: {self.profile_path}. Recommendations require a profile.[/yellow]")
            if not self.dd_path.exists():
                self.console.print(f"[yellow]⚠️ Data Dictionary not found at: {self.dd_path}[/yellow]")
            return {}

        with open(self.profile_path, 'r') as f:
            profile = json.load(f)
        
        # Robust Resolution: Handle both nested 'columns' key and flat dictionary structure
        column_stats = profile.get("columns", profile)
        
        try:
            df_dd = pd.read_csv(self.dd_path, engine='c', low_memory=False)
        except Exception:
            df_dd = pd.read_csv(self.dd_path, sep=None, engine='python')

        # FACTORING: Consolidate all parser-stage metadata (logical types, geo-flags, entity assignments)
        # We resolve the authoritative attribute mapping to link parser metadata with physical stats.
        attr_col = "attribute_name" if "attribute_name" in df_dd.columns else df_dd.columns[0]
        
        # 🛡️ DEDUPLICATION: Ensure the dictionary has unique attribute mappings to prevent orient='index' collisions
        df_dd_clean = df_dd.drop_duplicates(subset=[attr_col])
        dd_lookup = df_dd_clean.set_index(attr_col).to_dict(orient="index")

        null_threshold = self.config.get('cleaner', {}).get('structural_assessment', {}).get('null_threshold', 0.95)
        
        for col, stats in column_stats.items():
            if not isinstance(stats, dict): continue # Skip non-column metadata entries
            
            # LINKAGE: Fetch the consolidated metadata factoring for this column from the parser stage
            meta = dd_lookup.get(col, {})
            logical_type = str(meta.get("logical_type", "unknown")).lower()
            entity = meta.get("provisional_entity_assignment", "Unknown")

            null_ratio = stats.get("null_ratio", 0)
            cardinality = stats.get("cardinality", 0)
            is_mixed = stats.get("is_mixed_type", False)
            
            action = "none"
            reason = "Data appears healthy"

            # 1. Structural Deletion (physically empty, zero variance, or extreme sparsity)
            if null_ratio >= 1.0:
                action = "drop-attribute"
                reason = "Column is physically empty (100% null)"
            elif cardinality <= 1:
                action = "drop-attribute"
                reason = "Constant value / Zero variance"
            elif null_ratio >= null_threshold:
                action = "drop-attribute"
                reason = f"Extreme sparsity ({null_ratio:.1%}): Exceeds null threshold of {null_threshold:.1%}"

            # 2. Mixed Data Detection
            elif is_mixed:
                action = "user-review"
                reason = "Mixed data types detected in column"

            # 3. Datetime to Numeric Mapping (Cross-Sectional Rule)
            elif logical_type == "datetime":
                action = "custom:datetime_to_numeric"
                reason = "This is a cross sectional dataset; if you want to use the datetime attributes, you need to derive numeric attributes from them and then delete them."

            # 4. Standardized Imputation
            if action == "none":
                if logical_type in ["categorical", "text"] and null_ratio > 0:
                    action = "constant:MISSING"
                    reason = f"Categorical/Text with {null_ratio:.1%} nulls: Recommendation is creating a 'MISSING' category."
                
                elif logical_type == "numeric" and null_ratio > 0:
                    action = "mean-imputation"
                    reason = f"Numeric with {null_ratio:.1%} nulls: Recommendation is mean imputation."
                
                elif null_ratio > 0:
                    action = "user-review"
                    reason = f"Column contains {null_ratio:.1%} nulls but type is unknown. Strategy required."

            if action != "none":
                self.recommendations.append({
                    "attribute_name": col,
                    "logical_type": logical_type,
                    "entity_context": entity,
                    "null_ratio": null_ratio,
                    "cardinality": cardinality,
                    "recommended_action": action,
                    "reason": reason
                })

        # 🤖 AUGMENTATION: Wire in the externalized LLM prompt logic
        self.augment_with_llm(profile)

        return {"recommendations": self.recommendations}

    def get_attributes_by_tag(self, tag_name: str) -> List[str]:
        """
        Discovery API: Retrieves attributes matching a specific semantic tag.
        
        Queries the Data Dictionary to find all columns where the specified 
        boolean flag (e.g., 'is_geographic') is True. This is primarily used 
        in notebooks to subset cleaned dataframes for specialized featurization.

        Args:
            tag_name (str): The semantic tag to filter by (e.g., 'geographic').

        Returns:
            List[str]: A list of attribute names possessing the requested tag.
        """
        try:
            df_dd = pd.read_csv(self.dd_path, engine='c', low_memory=False)
        except Exception:
            df_dd = pd.read_csv(self.dd_path, sep=None, engine='python')

        attr_col = "attribute_name" if "attribute_name" in df_dd.columns else df_dd.columns[0]
        flag_col = f"is_{tag_name.lower().strip()}"

        if flag_col not in df_dd.columns:
            self.logger.warning(f"⚠️ Semantic tag '{tag_name}' not found in registry (Column '{flag_col}' missing).")
            return []

        subset = df_dd[df_dd[flag_col] == True][attr_col].tolist()
        return [str(a) for a in subset]

    def get_attributes_by_entity(self, entity_name: str) -> List[str]:
        """
        Discovery API: Retrieves attributes assigned to a specific business entity.
        
        Queries the metadata registry to find all attributes mapped to a 
        coarse-grained business concept (e.g., 'Borrower', 'Loan') discovered 
        during the Parser phase.

        Args:
            entity_name (str): The entity concept name to filter by.

        Returns:
            List[str]: A list of attribute names belonging to the specified entity.
        """
        try:
            df_dd = pd.read_csv(self.dd_path, engine='c', low_memory=False)
        except Exception:
            df_dd = pd.read_csv(self.dd_path, sep=None, engine='python')

        attr_col = "attribute_name" if "attribute_name" in df_dd.columns else df_dd.columns[0]
        entity_col = "provisional_entity_assignment"

        if entity_col not in df_dd.columns:
            self.logger.warning(f"⚠️ Entity assignments not found in dictionary at {self.dd_path}")
            return []

        mask = df_dd[entity_col].astype(str).str.lower() == entity_name.lower().strip()
        subset = df_dd[mask][attr_col].tolist()
        return [str(a) for a in subset]

    def augment_with_llm(self, profile: Dict[str, Any]) -> None:
        """
        Augments heuristic recommendations with LLM insights.
        
        Assembles a specialized prompt containing the data quality profile 
        and queries the local LLM to identify edge cases or domain-specific 
        anomalies that rule-based heuristics might miss.

        Args:
            profile (Dict[str, Any]): The physical data quality profile.
        """
        prompt = self._assemble_recommendation_prompt(profile)
        try:
            response = self._call_llm(prompt)
            llm_recs = self._process_recommendation_result(response)
            self.recommendations.extend(llm_recs)
        except Exception as e:
            self.logger.error(f"❌ LLM Recommendation augmentation failed: {e}")

    def _assemble_recommendation_prompt(self, profile: Dict[str, Any]) -> str:
        """
        Handles prompt construction using templates from configuration.

        Args:
            profile (Dict[str, Any]): The data quality stats to inject.

        Returns:
            str: Formatted LLM prompt.
        """
        template = self.prompts.get("recommendation_template")
        system_p = self.prompts.get("system", "You are a data engineering assistant.")
        
        if template and "{profile}" in template:
            return template.format(profile=json.dumps(profile))
        elif template:
            return f"{template}\n\nDATA PROFILE: {json.dumps(profile)}"
            
        return f"{system_p}\n\nAnalyze dataset profile: {json.dumps(profile)}"

    def _process_recommendation_result(self, response: str) -> List[Dict[str, Any]]:
        """
        Handles cleaning and parsing of the LLM JSON response.

        Args:
            response (str): The raw JSON string returned by the model.

        Returns:
            List[Dict[str, Any]]: A list of structured recommendation objects.
        """
        data = json.loads(response)
        recs = data.get("recommendations", [])
        
        # 🛡️ DEFENSIVE SANITIZATION: Ensure 'recommended_action' is a string.
        # LLMs occasionally return lists for single-choice fields, which causes 
        # "unhashable type: 'list'" errors in Pandas value_counts() or groupby calls.
        for r in recs:
            if "recommended_action" in r and isinstance(r["recommended_action"], list):
                r["recommended_action"] = r["recommended_action"][0] if r["recommended_action"] else "user-review"
        return recs

    def _call_llm(self, prompt: str) -> str:
        """
        Standardized HTTP caller for the local Ollama instance.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            str: The raw model response.

        Raises:
            RuntimeError: If the API returns a non-200 status code.
        """
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={"model": self.model_name, "prompt": prompt, "stream": False, "format": "json"},
            timeout=self.llm_timeout
        )
        if response.status_code != 200:
            raise RuntimeError(f"Ollama API error: {response.text}")
        return response.json().get("response", "{}")

    def write_artifacts(self, output_dir: Path):
        """
        Generates Markdown and CSV artifact reports.

        Args:
            output_dir (Path): Destination directory for the generated files.
        """
        if not self.recommendations:
            return

        output_dir.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(self.recommendations)

        # 1. Markdown Report
        md_path = output_dir / "cleaning_recommendations.md"
        with open(md_path, "w") as f:
            f.write("# 🤖 Cleaning Assistant Report\n\n")
            f.write("This report provides automated recommendations based on data profile physics and semantic metadata.\n\n")
            
            f.write("## 🛡️ User Responsibilities\n")
            f.write("- **Domain Logic**: User must capture domain-specific row filters in `config.yaml` or `domain_logic.py`.\n")
            f.write("- **Domain Deletions**: User must identify columns requiring deletion based on business rules.\n")
            f.write("- **Strategy Validation**: While we suggest mean/MISSING defaults, the user determines the final strategy.\n\n")

            f.write("## 📊 Summary of Actions\n")
            if not df.empty:
                summary = df["recommended_action"].value_counts().to_dict()
                for action, count in summary.items():
                    f.write(f"- **{action}**: {count} columns\n")
            else:
                f.write("- No changes recommended. Data appears healthy.\n")

            def write_section(title, filtered_df, level=2):
                if filtered_df.empty:
                    return
                f.write(f"\n{'#' * level} {title}\n\n")
                display_df = filtered_df.rename(columns={
                    "attribute_name": "Attribute",
                    "logical_type": "Type",
                    "entity_context": "Entity",
                    "reason": "What Needs Fixing",
                    "recommended_action": "Recommended Fix"
                })[["Attribute", "Type", "Entity", "What Needs Fixing", "Recommended Fix"]]
                f.write(display_df.to_markdown(index=False))
                f.write("\n")

            df_del = df[df["recommended_action"] == "drop-attribute"]
            write_section("Deletion is recommended for the following attributes", df_del, level=2)

            df_der = df[df["recommended_action"] == "custom:datetime_to_numeric"]
            write_section("Derived attribute definition or deletion is recommended", df_der, level=2)

            df_impute = df[
                (df["null_ratio"] > 0) & 
                (~df["recommended_action"].isin(["drop-attribute", "custom:datetime_to_numeric"]))
            ]
            
            if not df_impute.empty:
                f.write("\n## Missing value definition is recommended for the following attributes\n")
                write_section("Numeric Attributes (Standard: Mean Imputation)", df_impute[df_impute["recommended_action"] == "mean-imputation"], level=3)
                write_section("Categorical Attributes (Standard: 'MISSING' Category)", df_impute[df_impute["recommended_action"] == "constant:MISSING"], level=3)
                write_section("Other Attributes with Missing Values (Strategy Required)", df_impute[df_impute["recommended_action"] == "user-review"], level=3)

            df_rev = df[(df["recommended_action"] == "user-review") & (df["null_ratio"] == 0)]
            write_section("Manual review is required for the following attributes", df_rev, level=2)
            
            f.write("\n\n---\n*Generated by CleaningAssistant engine.*")
        
        # 2. CSV Matrix
        csv_path = output_dir / "cleaning_matrix_actions_only.csv"
        df.to_csv(csv_path, index=False)

        self.console.print(f"\n[bold green]✨ Assistant artifacts generated in:[/bold green] {output_dir}")
        self.console.print(f" - Report: [cyan]cleaning_recommendations.md[/cyan]")