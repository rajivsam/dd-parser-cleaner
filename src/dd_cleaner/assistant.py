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
    """Analyzes dataset physics and semantics to suggest cleaning strategies."""

    def __init__(self, config: Dict[str, Any], profile_path: Path, dd_path: Path):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.profile_path = profile_path
        self.dd_path = dd_path
        self.console = Console()
        self.recommendations = []
        self.prompts = self.config.get("cleaner", {}).get("missing_values", {}).get("prompts", {}).get("cleaning_assistant", {})
        self.model_name = self.config.get("model_name", "llama3.2")

    def generate_recommendations(self) -> Dict[str, Any]:
        """Core heuristic engine to map columns to actions."""
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
        
        df_dd = pd.read_csv(self.dd_path)
        # FACTORING: Consolidate all parser-stage metadata (logical types, geo-flags, entity assignments)
        # We resolve the authoritative attribute mapping to link parser metadata with physical stats.
        attr_col = "attribute_name" if "attribute_name" in df_dd.columns else df_dd.columns[0]
        dd_lookup = df_dd.set_index(attr_col).to_dict(orient="index")

        null_threshold = self.config.get('cleaner', {}).get('structural_assessment', {}).get('null_threshold', 0.95)
        
        processed_recs = []
        for col, stats in column_stats.items():
            if not isinstance(stats, dict): continue # Skip non-column metadata entries
            
            # LINKAGE: Fetch the consolidated metadata factoring for this column from the parser stage
            meta = dd_lookup.get(col, {})
            logical_type = str(meta.get("logical_type", "unknown")).lower()
            is_geo = meta.get("is_geographic", False)
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
                # Note: This implies a subsequent drop-attribute in user config

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

    def augment_with_llm(self, profile: Dict[str, Any]) -> None:
        """Augments heuristic recommendations with LLM insights."""
        # Assembly Phase
        prompt = self._assemble_recommendation_prompt(profile)
        
        # Execution Phase
        try:
            response = self._call_llm(prompt)
            llm_recs = self._process_recommendation_result(response)
            self.recommendations.extend(llm_recs)
        except Exception as e:
            self.logger.error(f"❌ LLM Recommendation augmentation failed: {e}")

    def _assemble_recommendation_prompt(self, profile: Dict[str, Any]) -> str:
        """Handles prompt construction using templates from configuration."""
        template = self.prompts.get("recommendation_template")
        system_p = self.prompts.get("system", "You are a data engineering assistant.")
        
        # Safety check: ensure the placeholder exists in the externalized string
        if template and "{profile}" in template:
            return template.format(profile=json.dumps(profile))
        elif template:
            self.logger.warning("⚠️ Externalized prompt template missing '{profile}' placeholder. Appending profile to end.")
            return f"{template}\n\nDATA PROFILE: {json.dumps(profile)}"
            
        return f"{system_p}\n\nAnalyze dataset profile: {json.dumps(profile)}"

    def _process_recommendation_result(self, response: str) -> List[Dict[str, Any]]:
        """Handles cleaning and parsing of the LLM JSON response."""
        data = json.loads(response)
        return data.get("recommendations", [])

    def _call_llm(self, prompt: str) -> str:
        """Standardized HTTP caller for Ollama."""
        response = httpx.post(
            "http://localhost:11434/api/generate",
            json={"model": self.model_name, "prompt": prompt, "stream": False, "format": "json"},
            timeout=60.0
        )
        return response.json().get("response", "{}")

    def write_artifacts(self, output_dir: Path):
        """Generates MD, CSV, and provisional YAML artifacts."""
        if not self.recommendations:
            # Message already printed in generate_recommendations
            return

        output_dir.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(self.recommendations)

        # 1. Markdown Report
        md_path = output_dir / "cleaning_recommendations.md"
        with open(md_path, "w") as f:
            f.write("# 🤖 Cleaning Assistant Report\n\n")
            f.write("This report provides automated recommendations based on data profile physics (nulls, cardinality) and semantic metadata.\n\n")
            
            f.write("## 🛡️ User Responsibilities\n")
            f.write("- **Domain Logic**: User must capture domain-specific row filters (exclusions/inclusions) in `config.yaml` or `domain_logic.py`.\n")
            f.write("- **Domain Deletions**: User must identify and tag columns requiring deletion based on business rules rather than physical stats.\n")
            f.write("- **Strategy Validation**: While we suggest mean/MISSING defaults, the user is responsible for determining the final imputation strategy per attribute.\n\n")

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
                # Human-friendly headers for the usability review
                display_df = filtered_df.rename(columns={
                    "attribute_name": "Attribute",
                    "logical_type": "Type",
                    "entity_context": "Entity",
                    "reason": "What Needs Fixing",
                    "recommended_action": "Recommended Fix"
                })[["Attribute", "Type", "Entity", "What Needs Fixing", "Recommended Fix"]]
                f.write(display_df.to_markdown(index=False))
                f.write("\n")

            # 1. Deletion Section
            df_del = df[df["recommended_action"] == "drop-attribute"]
            write_section("Deletion is recommended for the following attributes", df_del, level=2)

            # 2. Derived Attributes Section
            df_der = df[df["recommended_action"] == "custom:datetime_to_numeric"]
            write_section("Derived attribute definition or deletion is recommended for the following attributes", df_der, level=2)

            # 3. Missing Values Section
            df_impute = df[
                (df["null_ratio"] > 0) & 
                (~df["recommended_action"].isin(["drop-attribute", "custom:datetime_to_numeric"]))
            ]
            
            if not df_impute.empty:
                f.write("\n## Missing value definition is recommended for the following attributes\n")
                # Sub-list: Numeric
                write_section("Numeric Attributes (Standard: Mean Imputation)", df_impute[df_impute["recommended_action"] == "mean-imputation"], level=3)
                # Sub-list: Categorical (Includes Text)
                write_section("Categorical Attributes (Standard: 'MISSING' Category)", df_impute[df_impute["recommended_action"] == "constant:MISSING"], level=3)
                # Sub-list: Manual Review (Any remaining nulls where type was unknown)
                write_section("Other Attributes with Missing Values (Strategy Required)", df_impute[df_impute["recommended_action"] == "user-review"], level=3)

            # 4. Mixed Data / General Review Section (Exclude attributes already listed in missing values)
            df_rev = df[(df["recommended_action"] == "user-review") & (df["null_ratio"] == 0)]
            write_section("Manual review is required for the following attributes (Mixed or Unknown types)", df_rev, level=2)
            
            f.write("\n\n---\n*Generated by CleaningAssistant engine.*")
        
        # 2. CSV Matrix
        csv_path = output_dir / "cleaning_matrix_actions_only.csv"
        df.to_csv(csv_path, index=False)

        # 3. Provisional Config YAML
        # We only generate overrides for columns that actually need changes
        yaml_path = output_dir / "provisional_config.yaml"
        recommendation_map = {
            rec["attribute_name"]: rec["recommended_action"]
            for rec in self.recommendations
        }
        
        # Rule 4: Datetime attributes are mapped to numeric in derivation then physically dropped
        drops = [col for col, action in recommendation_map.items() 
                 if action == "drop-attribute" or action == "custom:datetime_to_numeric"]
        
        # Rule 2: Standardized Imputation (Mean/MISSING)
        imputes = {col: action for col, action in recommendation_map.items() 
                   if action not in ["drop-attribute", "custom:datetime_to_numeric", "user-review"]}
        
        # Rule 4: Datetime numeric offsets are derivations
        derivations = {col: action for col, action in recommendation_map.items() 
                       if action == "custom:datetime_to_numeric"}

        prov_cfg = {
            "cleaner": {
                "column_filters": {"drop_attributes": drops},
                "missing_values": {"attribute_overrides": imputes},
                "derivation": {"attribute_overrides": derivations}
            }
        }

        with open(yaml_path, "w") as f:
            f.write("# 🚧 PROVISIONAL CLEANING CONFIGURATION\n")
            f.write("# Review these settings and apply to your main config.yaml\n\n")
            yaml.safe_dump(prov_cfg, f, sort_keys=False)

        self.console.print(f"\n[bold green]✨ Assistant artifacts generated in:[/bold green] {output_dir}")
        self.console.print(f" - Report: [cyan]cleaning_recommendations.md[/cyan]")
        self.console.print(f" - Config: [cyan]provisional_config.yaml[/cyan]")