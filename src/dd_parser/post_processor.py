"""Applies overrides, dynamic tags, and serializes cryptographic metadata matrix tables."""

import re
import json
import hashlib
import logging
from datetime import datetime
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple, List, Set
from dd_common.path_coordinator import PathCoordinator
from .rules import IntegrityEngine


class MetadataPostProcessor:
    """
    Structures extracted entity values and manages storage rules.

    Attributes:
        paths (PathCoordinator): resource routing manager.
        parser_config (dict): Parser-specific configuration.
        all_keywords (dict): Cache of tag-identifying keywords.
        known_prefixes (list): Stems discovered for prefix-stripping logic.
    """

    def __init__(self, path_coordinator: PathCoordinator, parser_config: Dict[str, Any]) -> None:
        """Initializes the processor layers."""
        self.logger = logging.getLogger(__name__)
        self.all_keywords: Dict[str, Set[str]] = {}
        self.known_prefixes: List[str] = []
        self.update_config(path_coordinator, parser_config)

    def update_config(self, path_coordinator: PathCoordinator, parser_config: Dict[str, Any]) -> None:
        """
        Refreshes operational configurations and targets dynamically.

        Args:
            path_coordinator (PathCoordinator): Resource manager.
            parser_config (dict): Configuration block.
        """
        self.paths = path_coordinator
        self.parser_config = parser_config if parser_config is not None else {}
        # 🧠 EARLY HYDRATION: Populate keywords from config immediately to support 
        # type inference during synchronization (Early Binding).
        self.all_keywords = {t: set(kws) for t, kws in (self.parser_config.get("tag_heuristics") or {}).items()}

    def _normalize(self, s: str) -> str:
        """Proxy for the centralized integrity normalization logic."""
        return IntegrityEngine.normalize(s)

    def infer_schema_columns(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Extracts attribute names and descriptions from dictionary data dynamically.

        Args:
            df (pd.DataFrame): The raw data dictionary file.

        Returns:
            Tuple[pd.Series, pd.Series]: (Attribute names, Description strings).
        """
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

    def synchronize_with_raw_headers(self, df_dict: pd.DataFrame, df_raw_sample: pd.DataFrame) -> pd.DataFrame:
        """
        Replaces attributes with authoritative headers and performs Early Binding of data types.

        Args:
            df_dict (pd.DataFrame): The processed data dictionary.
            df_raw_sample (pd.DataFrame): A sample of the raw dataset for type probing.

        Returns:
            pd.DataFrame: Dictionary with headers aligned to the raw data file.
        """
        raw_headers = list(df_raw_sample.columns)
        raw_header_map = {self._normalize(h): h for h in raw_headers}
        
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
            dict_attr_norm = self._normalize(dict_attr_val)
            
            matched_header = raw_header_map.get(dict_attr_norm)
            
            if matched_header:
                # 🛡️ DEDUPLICATION GATE: Prevents multiple dictionary entries from mapping 
                # to the same physical header (e.g., due to aggressive normalization).
                if matched_header in matched_raw_headers:
                    self.logger.warning(
                        f"⚠️ Duplicate entry for header '{matched_header}' in Data Dictionary. Skipping redundant definition."
                    )
                    continue
                row_dict[target_col_name] = matched_header
                # 🎯 AUTHORITATIVE GATEWAY: Assign types early while the bridge is active
                p_type, l_type = self.convert_to_DS_type(df_raw_sample[matched_header])
                row_dict["physical_type"] = p_type
                row_dict["logical_type"] = l_type
                matched_raw_headers.add(matched_header)
                updated_rows.append(row_dict)
            else:
                # 🕵️ DEBUG: Log mismatches to identify naming drift
                self.logger.debug(
                    f"🔍 Bridge Sync Miss: Dictionary attribute '{dict_attr_val}' (norm: '{dict_attr_norm}') "
                    "not found in raw headers.")

        return pd.DataFrame(updated_rows)

    def _derive_prefix_stems(self, assigned_attributes: List[str]) -> List[str]:
        """
        Algorithmatically computes common structural tokens from attributes.

        Identifies common prefix candidates (e.g., 'borr', 'bank') to facilitate 
        accurate heuristic stripping in semantic classification.

        Args:
            assigned_attributes (List[str]): Attributes already classified by the LLM.

        Returns:
            List[str]: Sorted list of unique prefix stems.
        """
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
        grounding_profile: Dict[str, Any] = None,
        df_raw_sample: pd.DataFrame = None,
        dataset_type: str = "cross-sectional",
        bridge_report: Dict[str, Any] = None
    ) -> pd.DataFrame:
        """
        Assembles data matrix and resolves configuration overrides.

        Args:
            df (pd.DataFrame): Operational dictionary matrix.
            attributes (pd.Series): Synchronized field names.
            descriptions (pd.Series): Definitions.
            llm_assignments (Dict[str, dict]): LLM classification payload.
            grounding_profile (dict, optional): Physical data stats.
            df_raw_sample (pd.DataFrame, optional): Sample raw data for type probing.
            dataset_type (str, optional): Inferred structural nature.
            bridge_report (dict, optional): Integrity check results.

        Returns:
            pd.DataFrame: Finalized metadata matrix for cleaner ingestion.
        """
        provisional_df = df.copy()
        
        # 🛡️ INTEGRITY LOGGING: The bridge has already been synchronized in the orchestrator.
        # We simply log the active operational count for the session.
        self.logger.info(f"🚀 Processing {len(provisional_df)} matched attributes in the operational pool.")

        # 1. Initialize Columns
        provisional_df["attribute_name"] = attributes
        provisional_df["provisional_entity_assignment"] = "unassigned"
        
        # Preserve Early-Bound types if they exist (from synchronization)
        if "physical_type" not in provisional_df.columns:
            provisional_df["physical_type"] = "unknown"
        if "logical_type" not in provisional_df.columns:
            provisional_df["logical_type"] = "unknown"

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

        # 🧠 PREFIX DISCOVERY: Derive stems from assignments to improve heuristic matching
        assigned_attrs = [a for a, m in llm_assignments.items() if m.get("entity_assignment") != "unassigned"]
        self.known_prefixes = self._derive_prefix_stems(assigned_attrs)

        for target in explicit_targets:
            keywords = self.all_keywords.get(target, set())
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
                        if "provisional_entity_assignment" in override_node:
                            provisional_df.at[idx, "provisional_entity_assignment"] = override_node["provisional_entity_assignment"]
                        for target in explicit_targets:
                            flag_key = f"is_{target}"
                            if flag_key in override_node:
                                v = override_node[flag_key]
                                provisional_df.at[idx, flag_key] = (str(v).lower() == 'true') if isinstance(v, str) else bool(v)
                    else:
                        provisional_df.at[idx, "provisional_entity_assignment"] = str(override_node)

        # 🛡️ GROUNDING VALIDATION: Flag obvious mismatches between LLM and Physical reality
        self._validate_grounding_consistency(provisional_df, grounding_profile)

        # 🛡️ INTEGRITY GATE: Force deduplication of the operational matrix before artifact generation
        provisional_df = provisional_df.drop_duplicates(subset=["attribute_name"]).reset_index(drop=True)

        # � PERSISTENCE: Save the finalized matrix and generate report
        self._write_pipeline_artifacts(provisional_df)
        self._write_provisional_report(provisional_df, grounding_profile, dataset_type=dataset_type, bridge_report=bridge_report)
        
        return provisional_df

    def _apply_name_heuristics(self, df: pd.DataFrame, target: str, keywords: Set[str], prefixes: List[str]) -> pd.DataFrame:
        """
        Applies name-based suffix heuristics using dynamic prefix-stripping.

        Args:
            df (pd.DataFrame): Operational matrix.
            target (str): Target semantic flag (e.g., 'geographic').
            keywords (Set[str]): Tokens defining the target.
            prefixes (List[str]): Discovered stems to strip.

        Returns:
            pd.DataFrame: Matrix with updated boolean flags.
        """
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

    def _validate_grounding_consistency(self, df: pd.DataFrame, profile: Dict[str, Any]) -> None:
        """
        Checks for semantic hallucinations.

        Args:
            df (pd.DataFrame): Operational matrix.
            profile (dict): Physical data stats.
        """
        if not profile:
            return

        for idx, row in df.iterrows():
            attr = str(row["attribute_name"]).lower()
            stats = profile.get(attr, {})
            
            # Example Check: Geographic tag on a field with 0 cardinality or non-string type
            if row.get("is_geographic") and stats:
                is_numeric = "int" in stats.get("physical_type", "") or "float" in stats.get("physical_type", "")
                if is_numeric and stats.get("cardinality", 0) > 100:
                    self.logger.warning(
                        f"⚠️ Potential Hallucination: '{row['attribute_name']}' tagged as GEOGRAPHIC but contains high-cardinality numeric data."
                    )

    def _write_pipeline_artifacts(self, df: pd.DataFrame) -> None:
        """
        Writes matrix result tables and cryptographic metadata signatures.

        Args:
            df (pd.DataFrame): Finalized metadata matrix.
        """
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
        """
        Infers the native Python type and logical category for a series.

        Args:
            series (pd.Series): Raw data column.

        Returns:
            Tuple[str, str]: (Physical type string, Logical type string).
        """
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
            # 🕵️ TEMPORAL PROBE: Detect datetime objects from string patterns or values
            is_temporal = False
            attr_name = str(series.name).lower() if series.name else ""
            
            # 🧠 ZERO-HARDCODING: Use keywords found during discovery/config for logical typing
            temporal_keywords = self.all_keywords.get("temporal", set()) | {"date", "time", "year", "timestamp"}
            
            if any(kw in attr_name for kw in temporal_keywords):
                is_temporal = True
            
            # 2. Check Value sample if name check is inconclusive
            if not is_temporal and (dtype == "object" or pd.api.types.is_string_dtype(dtype)):
                sample = series.dropna().head(10).astype(str)
                if not sample.empty:
                    import warnings
                    with warnings.catch_warnings():
                        # Suppress the UserWarning: "Could not infer format, so each element will be parsed individually..."
                        warnings.simplefilter("ignore", UserWarning)
                        try:
                            pd.to_datetime(sample, errors='raise')
                            is_temporal = True
                        except (ValueError, TypeError, OverflowError):
                            pass
            
            if is_temporal:
                return "datetime", "datetime"

            t_name = "str"
            # Heuristic: Categorical vs Text based on cardinality ratio
            unique_ratio = series.nunique() / len(series) if len(series) > 0 else 1
            l_name = "categorical" if unique_ratio < 0.4 else "text"
            
        return t_name, l_name


    def _write_provisional_report(
        self, 
        df: pd.DataFrame, 
        grounding_profile: Dict[str, Any] = None, 
        dataset_type: str = "cross-sectional",
        bridge_report: Dict[str, Any] = None
    ) -> None:
        """Generates a human-readable markdown report summarizing entity assignments and types."""
        # 🧠 DYNAMIC PATH RESOLUTION: Fetch the report path from the coordinator
        report_path = self.paths.parser_provisional_report_path
        
        if "attribute_name" not in df.columns:
            return

        report_path.parent.mkdir(parents=True, exist_ok=True)

        # Extract the relevant columns for the summary report
        raw_tags = self.parser_config.get("entity_tagging") or []
        explicit_targets = [str(t).strip().lower() for t in raw_tags if t]
        tag_cols = [f"is_{target}" for target in explicit_targets]
        
        # Use the Early-Bound "Sticky" cargo columns for the report
        report_df = df[["attribute_name", "provisional_entity_assignment", "logical_type", "physical_type"] + tag_cols].copy()

        # 🎨 PRESENTATION: Apply backticks for a consistent fixed-width font look
        md_display_df = report_df.copy()
        md_display_df["attribute_name"] = md_display_df["attribute_name"].apply(lambda x: f"`{x}`")
        md_display_df["provisional_entity_assignment"] = md_display_df["provisional_entity_assignment"].apply(lambda x: f"`{x}`")
        md_display_df["logical_type"] = md_display_df["logical_type"].apply(lambda x: f"`{x}`")
        md_display_df["physical_type"] = md_display_df["physical_type"].apply(lambda x: f"`{x}`")

        for col in tag_cols:
            md_display_df[col] = md_display_df[col].apply(lambda x: f"`{x}`")

        # Construct headers dynamically
        md_headers = ["Attribute", "Assignment", "Logical Type", "Physical Type"] + [f"Flag: {t.title()}" for t in explicit_targets]
        md_display_df.columns = md_headers

        summary_stats = df["provisional_entity_assignment"].value_counts()

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# 📑 Data Dictionary: Provisional Entity Assignment Report\n")
            f.write(f"**Generation Timestamp:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n")
            f.write(f"**Source Blueprint:** `{self.paths.data_dictionary_path.name}`\n\n")
            f.write(f"### 🏗️ Structural Assessment\n")
            f.write(f"- **Inferred Dataset Type:** `{dataset_type}`\n")
            f.write(f"> ⚠️ **Note:** This inference is an automated suggestion based on schema patterns and may be incorrect. ")
            f.write(f"The `dataset_type` must be explicitly confirmed or defined in `config.yaml` before the Cleaner phase begins.\n\n")
            f.write(f"### 📊 Classification Summary\n")
            for entity, count in summary_stats.items():
                f.write(f"- **{entity}**: {count} fields\n")
            
            # 🚩 INTEGRITY REPORTING: Explicit mismatch sections
            if bridge_report:
                orphans = bridge_report.get("orphans", [])
                if orphans:
                    f.write("\n### ⚠️ Orphans in Data Dictionary\n")
                    f.write("> These attributes exist in the dictionary but were **not found** in the raw data file. They have been excluded from the assignments below.\n\n")
                    for item in orphans:
                        f.write(f"- `{item}`\n")
                
                ghosts = bridge_report.get("ghosts", [])
                if ghosts:
                    f.write("\n### 👻 Orphans in Data (Ghosts)\n")
                    f.write("> These headers exist in the raw data file but have **no corresponding entry** in the data dictionary.\n\n")
                    for item in ghosts:
                        f.write(f"- `{item}`\n")

            f.write(f"\n---\n\n### 📋 Detailed Assignments\n")
            f.write(md_display_df.to_markdown(index=False, tablefmt="github"))
            f.write("\n\n---\n*Report generated via automated dd-parser post-processing.*")
        self.logger.info(f"📝 Provisional entity assignment report generated at: {report_path}")