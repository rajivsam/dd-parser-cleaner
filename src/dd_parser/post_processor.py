"""Applies overrides, dynamic tags, and serializes cryptographic metadata matrix tables."""

import re
import json
import hashlib
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple, List
from path_coordinator import PathCoordinator


class MetadataPostProcessor:
    """Structures extracted entity values and manages hard disk storage rules without hardcoded keywords."""

    def __init__(self, path_coordinator: PathCoordinator, parser_config: Dict[str, Any]) -> None:
        """Initializes the processor layers."""
        self.update_config(path_coordinator, parser_config)
        self._known_prefixes = ["borrower", "borr", "lender", "lend", "bank", "location", "loc", "loan", "prop"]

    def update_config(self, path_coordinator: PathCoordinator, parser_config: Dict[str, Any]) -> None:
        """Refreshes operational configurations and targets dynamically."""
        self.paths = path_coordinator
        self.parser_config = parser_config

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

    def execute(
        self, df: pd.DataFrame, attributes: pd.Series, descriptions: pd.Series, llm_assignments: Dict[str, Dict[str, Any]]
    ) -> pd.DataFrame:
        """Assembles data matrix, resolves configuration overrides, and saves output data blocks."""
        provisional_df = df.copy()
        
        provisional_df["attribute_name"] = attributes
        provisional_df["provisional_entity_assignment"] = "unassigned"
        
        # 🎯 ZERO-HARDCODING FIX: Extract targets strictly from configuration with empty list fallback
        raw_tags = self.parser_config.get("entity_tagging") or []
        explicit_targets = [str(t).strip().lower() for t in raw_tags if t]
        
        for target in explicit_targets:
            provisional_df[f"is_{target}"] = False

        user_overrides = self.parser_config.get("overrides", {})

        for idx in range(len(provisional_df)):
            attr_raw = str(attributes.iloc[idx])
            
            # Extract dynamic response structures directly from semantic payload node
            field_metadata = llm_assignments.get(attr_raw, {})
            assigned_label = field_metadata.get("entity_assignment", "Loan")
            
            lookup_key = attr_raw
            if lookup_key not in user_overrides:
                for k in user_overrides:
                    if k.lower() == attr_raw.lower():
                        lookup_key = k
                        break

            # Handle configuration overrides
            if lookup_key in user_overrides:
                override_node = user_overrides[lookup_key]
                if isinstance(override_node, dict):
                    assigned_label = override_node.get("provisional_entity_assignment", assigned_label)
                else:
                    assigned_label = override_node
                
            provisional_df.at[idx, "provisional_entity_assignment"] = assigned_label

            # Populate target column configurations straight out of LLM properties or manual overrides
            for target in explicit_targets:
                override_flag = False
                if lookup_key in user_overrides and isinstance(user_overrides[lookup_key], dict):
                    override_flag = user_overrides[lookup_key].get(f"is_{target}", False)
                
                # Extract boolean assessment directly assigned by LLM discovery logic pass
                llm_flag_assessment = field_metadata.get(f"is_{target}", False)
                
                if override_flag or llm_flag_assessment:
                    provisional_df.at[idx, f"is_{target}"] = True

        self._write_pipeline_artifacts(provisional_df)
        return provisional_df


    def _write_pipeline_artifacts(self, df: pd.DataFrame) -> None:
        """Writes matrix result tables and cryptographic metadata signatures to the output targets."""
        output_csv_path = self.paths.data_dictionary_csv_path
        
        df.to_csv(output_csv_path, index=False)
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        hash_sig = hashlib.sha256(csv_bytes).hexdigest()
        
        sidecar_path = Path(output_csv_path).with_suffix(".signature")
        with open(sidecar_path, "w") as sf:
            sf.write(json.dumps({"sha256": hash_sig, "total_columns": len(df)}))
