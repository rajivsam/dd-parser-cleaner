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
        bridge_report: Dict[str, Any] = None,
        use_case_answers: Dict[str, Any] = None
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
            dataset_type (str, optional): Configured structural nature.
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
        provisional_df["static_dynamic"] = "none"
        
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

        # Determine whether event-log dynamic/static inference is available from config
        event_log_dynamic_map = {}
        if dataset_type in {"event_log", "longitudinal"} and self.paths.subject_id_attribute and df_raw_sample is not None:
            event_log_dynamic_map = self._infer_static_dynamic_from_sample(
                df_raw_sample,
                self.paths.subject_id_attribute,
                attributes.tolist()
            )

        # 2. PHASE 1: Apply LLM Assignments
        for idx in range(len(provisional_df)):
            attr_raw = str(attributes.iloc[idx])
            field_metadata = llm_assignments.get(attr_raw, {})

            # Apply LLM Category
            assigned_label = field_metadata.get("entity_assignment", "unassigned")
            provisional_df.at[idx, "provisional_entity_assignment"] = assigned_label

            # Apply Static/Dynamic only for panel-like datasets.
            if dataset_type in {"panel", "event_log", "longitudinal"}:
                if "static_dynamic" in field_metadata:
                    provisional_df.at[idx, "static_dynamic"] = str(field_metadata.get("static_dynamic", "static")).lower()
                elif dataset_type == "panel":
                    provisional_df.at[idx, "static_dynamic"] = self._infer_static_dynamic(
                        attr_raw,
                        str(descriptions.iloc[idx]),
                        provisional_df.loc[idx]
                    )
                else:
                    if event_log_dynamic_map:
                        provisional_df.at[idx, "static_dynamic"] = event_log_dynamic_map.get(attr_raw, "static")
                    else:
                        provisional_df.at[idx, "static_dynamic"] = self._infer_static_dynamic(
                            attr_raw,
                            str(descriptions.iloc[idx]),
                            provisional_df.loc[idx]
                        )

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
        self._write_manifest_artifacts(provisional_df, dataset_type, use_case_answers=use_case_answers)
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

    def _infer_static_dynamic_from_sample(
        self,
        df_raw_sample: pd.DataFrame,
        subject_id_attr: str,
        attributes: list,
        sample_frac: float = 0.5
    ) -> Dict[str, str]:
        """
        Infers static/dynamic status for an event-log dataset using a raw sample grouped by subject.

        Args:
            df_raw_sample (pd.DataFrame): Raw dataset sample.
            subject_id_attr (str): Subject ID header name.
            attributes (list): List of attribute names from the data dictionary.
            sample_frac (float): Fraction of rows to sample for inference.

        Returns:
            Dict[str, str]: Mapping from attribute name to 'static' or 'dynamic'.
        """
        results: Dict[str, str] = {}
        if not subject_id_attr or subject_id_attr not in df_raw_sample.columns:
            self.logger.warning(
                f"⚠️ Subject id attribute '{subject_id_attr}' is missing from the raw dataset sample. "
                "Skipping deterministic static/dynamic inference."
            )
            return results

        if sample_frac <= 0 or sample_frac > 1:
            sample_frac = 0.5

        if len(df_raw_sample) == 0:
            return results

        if sample_frac < 1.0 and len(df_raw_sample) > 1:
            df_sample = df_raw_sample.sample(frac=sample_frac, random_state=0)
        else:
            df_sample = df_raw_sample.copy()

        group = df_sample.groupby(subject_id_attr)
        for attr in attributes:
            if attr == subject_id_attr:
                results[attr] = "static"
                continue
            if attr not in df_sample.columns:
                continue
            try:
                dynamic = group[attr].nunique(dropna=False).gt(1).any()
            except Exception as exc:
                self.logger.warning(
                    f"⚠️ Error inferring static/dynamic for '{attr}' from sample: {exc}. "
                    "Defaulting to static."
                )
                dynamic = False
            results[attr] = "dynamic" if dynamic else "static"

        return results

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

    def _write_manifest_artifacts(self, df: pd.DataFrame, dataset_type: str, use_case_answers: Dict[str, Any] = None) -> None:
        """
        Writes the dataset manifest, attribute manifest, and handshake file.

        Args:
            df (pd.DataFrame): Finalized metadata matrix.
            dataset_type (str): Configured dataset type.
            use_case_answers (Dict[str, Any], optional): Optional questionnaire answers to include in the dataset manifest.
        """
        dataset_manifest = self._build_dataset_manifest(df, dataset_type, use_case_answers=use_case_answers)
        attribute_manifest = self._build_attribute_manifest(df)

        dataset_manifest_path = self.paths.dataset_manifest_path
        attribute_manifest_path = self.paths.attribute_manifest_path

        with open(dataset_manifest_path, "w", encoding="utf-8") as f:
            json.dump(dataset_manifest, f, indent=2)

        with open(attribute_manifest_path, "w", encoding="utf-8") as f:
            json.dump(attribute_manifest, f, indent=2)

        self.logger.info(f"📦 Dataset manifest written to: {dataset_manifest_path}")
        self.logger.info(f"📦 Attribute manifest written to: {attribute_manifest_path}")

        self._write_handshake_file(dataset_manifest_path, attribute_manifest_path, dataset_manifest)

    def _build_dataset_manifest(self, df: pd.DataFrame, dataset_type: str, use_case_answers: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Constructs the dataset-level manifest payload.

        Args:
            df (pd.DataFrame): Finalized metadata matrix.
            dataset_type (str): Configured dataset type.
            use_case_answers (Dict[str, Any], optional): Optional questionnaire answers to include in the manifest.
        """
        dataset_id = self.paths.config.get("dataset_id")
        if not dataset_id:
            raw_path = getattr(self.paths, "raw_dataset_path", None)
            dataset_id = Path(raw_path).stem if raw_path and Path(raw_path).exists() else Path(self.paths.data_dictionary_path).stem

        primary_key_spec = self._infer_primary_key_spec(df)
        time_key_spec = self._infer_time_key_spec(df, dataset_type)

        validation_errors = []
        if not primary_key_spec:
            validation_errors.append("primary_key_spec is empty")
        if dataset_type in {"panel", "event_log"} and not time_key_spec:
            validation_errors.append("time_key_spec is missing for longitudinal or event log dataset")

        notes = "Generated by dd_parser metadata pipeline."
        use_case_answers = use_case_answers or {}
        questionnaire_required = bool(self.paths.config.get("handshake_require_questions") and not use_case_answers)
        if questionnaire_required:
            validation_errors.append("questionnaire responses required")

        if self.parser_config.get("wide_short_homogeneous"):
            wide_short_info = self._build_wide_short_info_from_config(df)
            if not wide_short_info:
                self.logger.warning("Wide-short config present but failed to build group info; falling back to auto-detection.")
                wide_short_info = self._infer_wide_short_homogeneous_info(df)
        else:
            wide_short_info = self._infer_wide_short_homogeneous_info(df)

        if wide_short_info:
            validation_errors = validation_errors or []
            flags = {"skip_columnwise_intelligence": True}
        else:
            flags = {}

        if questionnaire_required:
            status = "blocked"
        else:
            status = "ready" if not validation_errors else "warnings"

        manifest = {
            "dataset_id": dataset_id,
            "dataset_type": dataset_type,
            "primary_key_spec": primary_key_spec,
            "time_key_spec": time_key_spec,
            "entity_files": [],
            "relation_files": [],
            "notes": notes,
            "notes_structure": wide_short_info.get("structure") if wide_short_info else None,
            "flags": flags,
            "use_case_answers": use_case_answers,
            "validation_errors": validation_errors,
            "status": status
        }

        if wide_short_info:
            manifest["wide_short_group"] = wide_short_info

        return manifest

    def _build_attribute_manifest(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Constructs per-attribute manifest entries."""
        manifest = []
        for _, row in df.iterrows():
            attr_name = str(row.get("attribute_name", ""))
            attr_role = self._infer_attribute_role(row)
            modality = self._infer_attribute_modality(row)
            suggested_checks = self._infer_suggested_checks(row, modality)

            manifest.append({
                "attribute_name": attr_name,
                "role": attr_role,
                "time_dependency": str(row.get("static_dynamic", "none")) if "static_dynamic" in row else "none",
                "static_dynamic": str(row.get("static_dynamic", "none")) if "static_dynamic" in row else "none",
                "granularity": None,
                "modality": modality,
                "suggested_checks": suggested_checks,
                "generated_key_flag": False
            })
        return manifest

    def _infer_static_dynamic(self, attr_name: str, description: str, row: pd.Series = None) -> str:
        """
        Infers whether a panel attribute is static or dynamic.

        Args:
            attr_name (str): Attribute name.
            description (str): Attribute description.
            row (pd.Series, optional): Current metadata row.

        Returns:
            str: 'static' or 'dynamic'
        """
        attr_lower = str(attr_name).lower()
        desc_lower = str(description).lower()

        dynamic_indicators = [
            "state", "status", "open", "close", "resolved", "updated", "timestamp",
            "date", "time", "duration", "due", "assigned_to", "priority", "urgency",
            "impact", "reopen", "closed_at", "resolved_at", "opened_at", "updated_at"
        ]
        static_indicators = [
            "id", "number", "code", "type", "category", "subcategory", "location",
            "vendor", "caller_id", "contact_type", "problem_id", "rfc", "identifier"
        ]

        if any(token in attr_lower for token in dynamic_indicators) or any(token in desc_lower for token in dynamic_indicators):
            return "dynamic"
        if any(token in attr_lower for token in static_indicators) or any(token in desc_lower for token in static_indicators):
            return "static"

        if row is not None:
            logical_type = str(row.get("logical_type", "")).lower()
            physical_type = str(row.get("physical_type", "")).lower()
            if "datetime" in logical_type or "datetime" in physical_type:
                return "dynamic"

        return "static"

    def _infer_primary_key_spec(self, df: pd.DataFrame) -> List[str]:
        """Uses a heuristic to discover primary key-like attributes."""
        if "attribute_name" not in df.columns:
            return []
        candidate_ids = [
            str(v) for v in df["attribute_name"].astype(str).tolist()
            if str(v).strip().lower().endswith("id")
        ]
        if candidate_ids:
            return candidate_ids[:1]

        # Wide-short datasets often use time or week identifiers as the primary axis.
        fallback_keys = [
            str(v) for v in df["attribute_name"].astype(str).tolist()
            if str(v).strip().lower() in {"woy", "week", "week_of_year", "weekofyear", "date"}
        ]
        return fallback_keys[:1]

    def _infer_time_key_spec(self, df: pd.DataFrame, dataset_type: str) -> Any:
        """Infers a time key for longitudinal or event datasets."""
        if dataset_type not in {"panel", "event_log"}:
            return None
        if "attribute_name" not in df.columns:
            return None
        time_candidates = [
            str(v) for v in df["attribute_name"].astype(str).tolist()
            if any(k in str(v).lower() for k in ["date", "time", "timestamp", "ts"])
        ]
        return time_candidates[0] if time_candidates else None

    def _infer_wide_short_homogeneous_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detects wide-and-short homogeneous datasets and returns group metadata."""
        if len(df) < 50:
            return {}

        attr_col = "attribute_name" if "attribute_name" in df.columns else None
        if attr_col is None:
            candidate_cols = [c for c in df.columns if str(c).strip().lower() in {"attribute", "field name", "field_name"}]
            attr_col = candidate_cols[0] if candidate_cols else df.columns[0]

        attrs = df[attr_col].astype(str).tolist()
        time_keys = [a for a in attrs if str(a).strip().lower() in {"woy", "week", "week_of_year", "weekofyear", "date"}]
        if len(time_keys) != 1:
            return {}

        desc_series = None
        if "description" in df.columns:
            desc_series = df["description"]
        elif "Description" in df.columns:
            desc_series = df["Description"]
        else:
            remaining = [c for c in df.columns if c != attr_col]
            desc_series = df[remaining[0]] if remaining else None

        if desc_series is None:
            return {}

        prefix = self._common_description_prefix(desc_series, min_count=0.75)
        if not prefix:
            return {}

        non_time_attrs = [a for a in attrs if str(a).strip().lower() not in {"woy", "week", "week_of_year", "weekofyear", "date"}]
        if not non_time_attrs:
            return {}

        representative_column = non_time_attrs[0]

        rep_row = df[df[attr_col] == representative_column].iloc[0]
        modality = self._infer_attribute_modality(rep_row)
        validation_rules = self._wide_short_validation_rules(modality)

        return {
            "structure": "wide_short_homogeneous",
            "group_name": re.sub(r"[^a-z0-9]+", "_", prefix.lower()).strip("_"),
            "representative_column": representative_column,
            "data_type": modality,
            "validation_rules": validation_rules,
            "count_columns": len(df) - 1,
            "description_prefix": prefix,
        }

    def _common_description_prefix(self, desc_series: pd.Series, min_count: float = 0.75) -> str:
        """Detects a repeated leading description prefix across a series of descriptions."""
        normalized = []
        for desc in desc_series.astype(str).dropna().tolist():
            desc_clean = re.sub(r"[^a-z0-9 ]+", " ", desc.lower()).strip()
            if not desc_clean:
                continue
            tokens = desc_clean.split()
            if len(tokens) < 4:
                continue
            normalized.append(" ".join(tokens[:5]))

        if not normalized:
            return ""

        best_prefix = max(set(normalized), key=normalized.count)
        if normalized.count(best_prefix) / len(normalized) >= min_count:
            return best_prefix
        return ""

    def _wide_short_validation_rules(self, modality: str) -> List[str]:
        rules: List[str] = []
        if modality in {"numeric", "currency"}:
            rules.extend(["non_negative", "range_consistency"])
        if modality == "date":
            rules.append("monotonicity")
        return rules

    def _build_wide_short_info_from_config(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Builds wide-short metadata from explicit parser configuration."""
        rep_column = self.parser_config.get("wide_short_representative_column")
        if not rep_column:
            return {}

        attr_col = "attribute_name" if "attribute_name" in df.columns else None
        if attr_col is None:
            candidate_cols = [c for c in df.columns if str(c).strip().lower() in {"attribute", "field name", "field_name"}]
            attr_col = candidate_cols[0] if candidate_cols else df.columns[0]

        attrs = df[attr_col].astype(str).tolist()
        if rep_column not in attrs:
            self.logger.warning(f"Wide-short representative column '{rep_column}' not found in dictionary attributes.")
            return {}

        if "description" in df.columns:
            desc_series = df["description"]
        elif "Description" in df.columns:
            desc_series = df["Description"]
        else:
            remaining = [c for c in df.columns if c != attr_col]
            desc_series = df[remaining[0]] if remaining else pd.Series([""] * len(df))

        prefix = self._common_description_prefix(desc_series, min_count=0.5)
        if not prefix:
            rep_row = df[df[attr_col] == rep_column].iloc[0]
            rep_desc = str(rep_row.get("description", "") or rep_row.get("Description", ""))
            prefix = " ".join(str(rep_desc).lower().split()[:5]).strip() if rep_desc else rep_column

        rep_row = df[df[attr_col] == rep_column].iloc[0]
        modality = self._infer_attribute_modality(rep_row)
        validation_rules = self._wide_short_validation_rules(modality)
        group_name = re.sub(r"[^a-z0-9]+", "_", prefix.lower()).strip("_") or re.sub(r"[^a-z0-9]+", "_", str(rep_column).lower()).strip("_")

        return {
            "structure": "wide_short_homogeneous",
            "group_name": group_name,
            "representative_column": rep_column,
            "data_type": modality,
            "validation_rules": validation_rules,
            "count_columns": len(df) - 1,
            "description_prefix": prefix,
        }

    def _infer_attribute_role(self, row: pd.Series) -> str:
        """Infers a generic role for the attribute."""
        name = str(row.get("attribute_name", "")).lower()
        if name.endswith("id"):
            return "subject_key"
        if any(k in name for k in ["date", "time", "timestamp", "ts"]):
            return "time_key"
        return "feature"

    def _infer_attribute_modality(self, row: pd.Series) -> str:
        """Infers field modality from metadata row values."""
        logical_type = str(row.get("logical_type", "")).lower()
        physical_type = str(row.get("physical_type", "")).lower()
        attr_name = str(row.get("attribute_name", "")).lower()

        if "datetime" in logical_type or "datetime" in physical_type or any(k in attr_name for k in ["date", "time", "timestamp"]):
            return "date"
        if row.get("is_geographic"):
            return "geo_address"
        if "url" in attr_name:
            return "text_url"
        if any(k in attr_name for k in ["amount", "price", "cost", "total"]):
            return "currency"
        if logical_type in {"numeric", "int", "float"} or any(k in physical_type for k in ["int", "float", "decimal"]):
            return "numeric"
        if logical_type in {"categorical", "text", "str", "string"}:
            return "categorical" if "cat" in logical_type else "text"
        return "other"

    def _infer_suggested_checks(self, row: pd.Series, modality: str) -> List[str]:
        """Provides suggested checks based on the inferred modality."""
        checks = []
        if modality == "date":
            checks.append("monotonicity")
        if modality == "geo_address":
            checks.append("geo_parse")
        if modality == "text_url":
            checks.append("url_validity")
        if modality == "currency":
            checks.append("range_consistency")
        if row.get("is_geographic") and modality == "numeric":
            checks.append("geo_parse")
        return checks

    def _write_handshake_file(
        self,
        dataset_manifest_path: Path,
        attribute_manifest_path: Path,
        dataset_manifest: Dict[str, Any]
    ) -> None:
        """Writes the parser-cleaner handshake file for downstream consumption."""
        handshake_path = self.paths.handshake_path
        handshake_path.parent.mkdir(parents=True, exist_ok=True)

        handshake_payload = {
            "status": dataset_manifest.get("status", "warnings"),
            "dataset_id": dataset_manifest.get("dataset_id"),
            "dataset_manifest_path": str(dataset_manifest_path.resolve()),
            "attribute_manifest_path": str(attribute_manifest_path.resolve()),
            "blocking_reasons": dataset_manifest.get("validation_errors", []),
            "notes": dataset_manifest.get("notes", "")
        }

        with open(handshake_path, "w", encoding="utf-8") as f:
            f.write("# Parser-Cleaner Handshake\n")
            f.write("This file indicates parser readiness and connects downstream cleaner/featurizer flows.\n\n")
            f.write("```json\n")
            json.dump(handshake_payload, f, indent=2)
            f.write("\n```")

        self.logger.info(f"🤝 Parser handshake written to: {handshake_path}")

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
        
        if dataset_type in {"panel", "event_log", "longitudinal"}:
            report_df = df[["attribute_name", "provisional_entity_assignment", "static_dynamic", "logical_type", "physical_type"] + tag_cols].copy()
        else:
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
        if dataset_type in {"panel", "event_log", "longitudinal"}:
            md_headers = ["Attribute", "Assignment", "Static/Dynamic", "Logical Type", "Physical Type"] + [f"Flag: {t.title()}" for t in explicit_targets]
        else:
            md_headers = ["Attribute", "Assignment", "Logical Type", "Physical Type"] + [f"Flag: {t.title()}" for t in explicit_targets]
        md_display_df.columns = md_headers

        summary_stats = df["provisional_entity_assignment"].value_counts()

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# 📑 Data Dictionary: Provisional Entity Assignment Report\n")
            f.write(f"**Generation Timestamp:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n")
            f.write(f"**Source Blueprint:** `{self.paths.data_dictionary_path.name}`\n\n")
            f.write(f"### 🏗️ Structural Assessment\n")
            f.write(f"- **Dataset Type:** `{dataset_type}`\n")
            f.write(f"> ⚠️ **Note:** This dataset type is provided by configuration and should match your workspace settings. ")
            f.write(
                "Update `dataset_type` in `config.yaml` if the dataset "
                "is actually a panel or longitudinal dataset.\n\n"
            )
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