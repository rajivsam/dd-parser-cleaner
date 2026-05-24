"""Applies overrides, dynamic tags, and serializes cryptographic metadata matrix tables."""

import re
import json
import hashlib
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple, List, Set
from path_coordinator import PathCoordinator


class MetadataPostProcessor:
    """Structures extracted entity values and manages hard disk storage rules without hardcoded keywords."""

    def __init__(self, path_coordinator: PathCoordinator, parser_config: Dict[str, Any]) -> None:
        """Initializes the processor layers."""
        self.logger = logging.getLogger(__name__)
        self.update_config(path_coordinator, parser_config)
        # 🧠 ZERO-HARDCODING: Initialized empty. Hydrated dynamically at runtime.
        self.known_prefixes: List[str] = []

    def update_config(self, path_coordinator: PathCoordinator, parser_config: Dict[str, Any]) -> None:
        """Refreshes operational configurations and targets dynamically."""
        self.paths = path_coordinator
        self.parser_config = parser_config if parser_config is not None else {}

    def infer_schema_columns(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Extracts structural parts from messy input columns dynamically using header names or indices."""
        target_col_name = self.paths.data_dictionary_attribute_col_name
        attr_idx = 0

        if target_col_name and target_col_name in df.columns:
            attr_idx = df.columns.get_loc(target_col_name)
        else:
            attr_idx = self.parser_config.get("csv_target_column_index", 0)
            if attr_idx >= len(df.columns):
                attr_idx = 0

        attr_series = df.iloc[:, attr_idx].astype(str).str.strip()

        remaining_cols = [i for i in range(len(df.columns)) if i != attr_idx]
        if not remaining_cols:
            return attr_series, pd.Series([""] * len(df))

        best_desc_idx = remaining_cols
        max_mean_length = -1
        for idx in remaining_cols:
            col_name = str(df.columns[idx]).lower()
            if any(kw in col_name for kw in ['definition', 'desc', 'meaning', 'explanation']):
                best_desc_idx = idx
                break
            mean_len = df.iloc[:, idx].astype(str).str.len().mean()
            if mean_len > max_mean_length:
                max_mean_length = mean_len
                best_desc_idx = idx

        desc_series = df.iloc[:, best_desc_idx].astype(str).str.strip()
        return attr_series, desc_series

    def synchronize_with_raw_headers(self, df_dict: pd.DataFrame, raw_headers: List[str]) -> pd.DataFrame:
        """Replaces data dictionary attributes with authoritative case-sensitive raw headers."""
        raw_headers_lower = [h.lower() for h in raw_headers]
        
        target_col_name = self.paths.data_dictionary_attribute_col_name
        if not target_col_name or target_col_name not in df_dict.columns:
            attr_idx = self.parser_config.get("csv_target_column_index", 0)
            if attr_idx >= len(df_dict.columns):
                attr_idx = 0
            target_col_name = df_dict.columns[attr_idx]

        _, desc_series = self.infer_schema_columns(df_dict)
        desc_col_name = desc_series.name if desc_series.name in df_dict.columns else "Definition"

        matched_raw_headers = set()
        updated_rows = []

        for _, row in df_dict.iterrows():
            row_dict = row.to_dict()
            dict_attr_val = str(row_dict[target_col_name]).strip()
            
            try:
                match_idx = raw_headers_lower.index(dict_attr_val.lower())
                authoritative_val = raw_headers[match_idx]
                row_dict[target_col_name] = authoritative_val
                matched_raw_headers.add(authoritative_val)
            except ValueError:
                pass
                
            updated_rows.append(row_dict)

        for raw_h in raw_headers:
            if raw_h not in matched_raw_headers:
                new_row = {col: "" for col in df_dict.columns}
                new_row[target_col_name] = raw_h
                new_row[desc_col_name] = "No description available."
                updated_rows.append(new_row)

        return pd.DataFrame(updated_rows)

    def _derive_prefix_stems(self, assigned_attributes: List[str]) -> List[str]:
        """Algorithmatically computes common structural token sub-stems from assigned attribute names."""
        stems = set()
        for attr in assigned_attributes:
            clean_attr = str(attr).strip().lower()
            if not clean_attr or len(clean_attr) < 3:
                continue
                
            # Heuristic: Capture the first 3 or 4 characters as potential organizational prefixes
            # e.g., 'borrstreet' -> 'borr', 'bankcity' -> 'bank'
            stems.add(clean_attr[:3])
            if len(clean_attr) >= 4:
                stems.add(clean_attr[:4])
            
            # If the attribute name is a single word token, add it too
            if '_' not in clean_attr and '-' not in clean_attr:
                stems.add(clean_attr)

        return sorted(list(stems), key=len, reverse=True)

    def execute(
        self, 
        df: pd.DataFrame, 
        attributes: pd.Series, 
        descriptions: pd.Series, 
        llm_assignments: Dict[str, Dict[str, Any]],
        discovered_heuristics: Dict[str, List[str]] = None
    ) -> pd.DataFrame:
        """Assembles data matrix, resolves configuration overrides, and saves output data blocks."""
        provisional_df = df.copy()

        # 1. Initialize Columns
        provisional_df["attribute_name"] = attributes
        provisional_df["provisional_entity_assignment"] = "unassigned"

        raw_tags = self.parser_config.get("entity_tagging") or []
        explicit_targets = [str(t).strip().lower() for t in raw_tags if t]

        for target in explicit_targets:
            provisional_df[f"is_{target}"] = False

        llm_assignments = llm_assignments or {}

        # 2. PHASE 1: Apply LLM Assignments
        for idx in range(len(provisional_df)):
            attr_raw = str(attributes.iloc[idx])
            field_metadata = llm_assignments.get(attr_raw, {})

            # Apply LLM Category
            assigned_label = field_metadata.get("entity_assignment", "unassigned")
            provisional_df.at[idx, "provisional_entity_assignment"] = assigned_label

            # Apply LLM Boolean Flags
            for target in explicit_targets:
                provisional_df.at[idx, f"is_{target}"] = field_metadata.get(f"is_{target}", False)

        # 🧠 METADATA RECONCILIATION: Derive prefixes directly from attributes that were assigned to entities
        assigned_attrs = [a for a, m in llm_assignments.items() if m.get("entity_assignment") != "unassigned"]
        self.known_prefixes = self._derive_prefix_stems(assigned_attrs)
        self.logger.info(f"📊 Dynamically extracted operational prefix stems: {self.known_prefixes}")

        # 3. PHASE 2: Hardened Heuristic Sweep (Automated inference enhancement)
        heuristics = discovered_heuristics or {}
        for target in explicit_targets:
            keywords = set(heuristics.get(target, []))

            # 🛡️ HARDENED SUFFIX HEURISTICS: Add baseline safety keywords for geographic tags
            if target == "geographic":
                keywords.update({'street', 'city', 'state', 'zip', 'county', 'district', 'lat', 'long', 'address', 'location'})

            if keywords:
                provisional_df = self._apply_name_heuristics(
                    provisional_df, target, keywords, self.known_prefixes
                )

        # 4. PHASE 3: Authoritative Overrides (The absolute final word)
        user_overrides = self.parser_config.get("overrides")
        if isinstance(user_overrides, dict):
            for idx in range(len(provisional_df)):
                attr_raw = str(attributes.iloc[idx])
                lookup_key = None

                # Case-insensitive match for override keys
                if attr_raw in user_overrides:
                    lookup_key = attr_raw
                else:
                    for k in user_overrides:
                        if k.lower() == attr_raw.lower():
                            lookup_key = k
                            break

                if lookup_key:
                    override_node = user_overrides[lookup_key]
                    if isinstance(override_node, dict):
                        # Assign Category Override (Strict case-insensitive match)
                        for k, v in override_node.items():
                            if k.lower() == "provisional_entity_assignment":
                                provisional_df.at[idx, "provisional_entity_assignment"] = v
                                break
                        
                        # Assign Boolean Flag Overrides (Absolute enforcement, Case-insensitive match)
                        for target in explicit_targets:
                            flag_key = f"is_{target}".lower()
                            for k, v in override_node.items():
                                if k.lower() == flag_key:
                                    provisional_df.at[idx, f"is_{target}"] = (str(v).lower() == 'true') if isinstance(v, str) else bool(v)
                                    break
                    else:
                        provisional_df.at[idx, "provisional_entity_assignment"] = str(override_node)

        self._write_pipeline_artifacts(provisional_df)
        self._write_provisional_report(provisional_df)
        return provisional_df

    def _apply_name_heuristics(self, df: pd.DataFrame, target: str, keywords: Set[str], prefixes: List[str]) -> pd.DataFrame:
        """Applies name-based suffix heuristics using dynamic prefix-stripping logic."""
        col_name = f"is_{target}"
        keywords_lower = {str(k).lower().strip() for k in keywords}
        if col_name not in df.columns:
            return df
            
        for idx in range(len(df)):
            if df.at[idx, col_name]:
                continue
                
            attr_clean = str(df.at[idx, "attribute_name"]).lower().strip()
            
            # Pass 1: Direct keyword or standard suffix match
            if any(attr_clean.endswith(kw) or attr_clean == kw for kw in keywords_lower):
                df.at[idx, col_name] = True
                continue
            
            # Pass 2: Prefix-stripped match using dynamic entity prefixes (e.g., borrstreet -> street)
            for prefix in prefixes:
                p_lower = prefix.lower()
                if attr_clean.startswith(p_lower):
                    stripped = attr_clean[len(p_lower):].lstrip('_').lstrip('-')
                    if any(stripped == kw or stripped.startswith(kw) for kw in keywords_lower):
                        df.at[idx, col_name] = True
                        break
        return df

    def _write_pipeline_artifacts(self, df: pd.DataFrame) -> None:
        """Writes matrix result tables and cryptographic metadata signatures to the output targets."""
        output_csv_path = Path(self.paths.data_dictionary_csv_path)
        
        # 1. Save the primary metadata matrix
        df.to_csv(output_csv_path, index=False)

        # 2. Generate the cryptographic signature for the matrix (enforced by test_cleaner orchestration)
        sha256_hash = hashlib.sha256()
        with open(output_csv_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        sig_path = output_csv_path.with_suffix(".signature")
        with open(sig_path, "w") as f:
            f.write(sha256_hash.hexdigest())
            
        self.logger.info(f"🔑 Metadata signature generated at: {sig_path}")
    
    def convert_to_DS_type(self, series: pd.Series) -> Tuple[str, str]:
        """Infers the native Python type and logical category for a given data series."""
        dtype = series.dtype
        
        if pd.api.types.is_numeric_dtype(dtype):
            t_name = "int" if pd.api.types.is_integer_dtype(dtype) else "float"
            l_name = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            t_name = "datetime"
            l_name = "datetime"
        elif pd.api.types.is_bool_dtype(dtype):
            t_name = "bool"
            l_name = "categorical"
        else:
            t_name = "str"
            # Heuristic: Categorical vs Text based on cardinality ratio
            unique_ratio = series.nunique() / len(series) if len(series) > 0 else 1
            l_name = "categorical" if unique_ratio < 0.4 else "text"
            
        return t_name, l_name


    def _write_provisional_report(self, df: pd.DataFrame) -> None:
        """Generates a markdown and CSV report summarizing entity assignments and types."""
        # 🧠 DYNAMIC PATH RESOLUTION: Fetch the report path from the coordinator
        report_path = getattr(self.paths, "parser_provisional_report_path", None)
        
        if not report_path:
            self.logger.warning("⚠️ Report generation skipped: Please check config.yaml to verify that 'parser_provisional_assingnment_dir' and 'parser_provisional_assingnment_filename' are populated.")
            return

        if "attribute_name" not in df.columns:
            return

        report_path = Path(report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        # 🔍 NATIVE TYPE DETECTION: Infer types from the raw dataset if available
        type_map = {}
        logical_map = {}
        raw_path = self.paths.raw_dataset_path
        if raw_path.exists():
            try:
                # Read a small sample to determine types reliably
                sample_df = pd.read_csv(raw_path, sep=None, engine='python', nrows=50)
                for col in sample_df.columns:
                    # Abstracted type and category inference
                    t_name, l_name = self.convert_to_DS_type(sample_df[col])
                    type_map[col.lower()] = t_name
                    logical_map[col.lower()] = l_name
            except Exception as e:
                self.logger.warning(f"⚠️ Could not infer native types from raw dataset: {e}")

        # Extract the relevant columns for the summary report
        raw_tags = self.parser_config.get("entity_tagging") or []
        explicit_targets = [str(t).strip().lower() for t in raw_tags if t]
        tag_cols = [f"is_{target}" for target in explicit_targets]
        
        report_df = df[["attribute_name", "provisional_entity_assignment"] + tag_cols].copy()

        report_df["Logical Category"] = report_df["attribute_name"].apply(
            lambda x: logical_map.get(str(x).lower(), "text")
        )

        # 💾 CSV GENERATION: Save a clean CSV copy before MD presentation formatting
        csv_report_path = report_path.with_suffix(".csv")
        report_df.to_csv(csv_report_path, index=False)
        self.logger.info(f"📊 Provisional assignment CSV generated at: {csv_report_path}")

        # 🎨 PRESENTATION: Apply backticks for a consistent fixed-width font look
        md_display_df = report_df.copy()
        md_display_df["attribute_name"] = md_display_df["attribute_name"].apply(lambda x: f"`{x}`")
        md_display_df["provisional_entity_assignment"] = md_display_df["provisional_entity_assignment"].apply(lambda x: f"`{x}`")
        md_display_df["Logical Category"] = md_display_df["Logical Category"].apply(lambda x: f"`{x}`")

        for col in tag_cols:
            md_display_df[col] = md_display_df[col].apply(lambda x: f"`{x}`")

        # Construct headers dynamically: Consolidating to "Logical Type" per preference
        md_headers = ["Attribute", "Provisional Entity Assignment"] + [f"Flag: {t.title()}" for t in explicit_targets] + ["Logical Type"]
        md_display_df.columns = md_headers

        summary_stats = df["provisional_entity_assignment"].value_counts()

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# 📑 Data Dictionary: Provisional Entity Assignment Report\n")
            f.write(f"**Source Blueprint:** `{self.paths.data_dictionary_path.name}`\n\n### 📊 Classification Summary\n")
            for entity, count in summary_stats.items():
                f.write(f"- **{entity}**: {count} fields\n")
            f.write(f"\n---\n\n### 📋 Detailed Assignments\n")
            f.write(md_display_df.to_markdown(index=False, tablefmt="github"))
            f.write("\n\n---\n*Report generated via automated dd-parser post-processing.*")
        self.logger.info(f"📝 Provisional entity assignment report generated at: {report_path}")