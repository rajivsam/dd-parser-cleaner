# 📑 Project Stash: Data Dictionary Parser & Cleaner State

## 🤖 Agent Operational Directives
* **Domain Agnosticism**: Strict requirement. Zero hardcoded domain-specific items.
* **Communication Style**: Brief, direct answers by default. Explanations provided only on request.
* **Config Management**: The agent must never modify `config.yaml` directly. If a configuration update is required (e.g., adding `tag_heuristics`), the agent must request the user to update the file and provide the intended YAML snippet.

## 🛠️ Active Project State (Last Updated: May 2024)

### 1. Core Architecture
* **Standardized Logging**: All components utilize `logging` (INFO level) for terminal feedback.
* **Path Coordination**: No-defaults policy. `PathCoordinator` raises blocking `ValueError` if any required `config.yaml` variable is missing.
* **Orchestration**: Two-phase LLM pipeline (Macro Discovery + Atomic Assignment) synchronized with raw data headers.

### 2. LLM Discovery & Classification (`llm_client.py`)
* **Phase 1 (Macro Domain)**: Samples fields to identify Logical Entities AND dynamic `tag_keywords` (heuristics) for feature tags like `geographic`.
* **Phase 2 (Atomic Assignment)**: Row-by-row classification to prevent context window crowding.

### 3. Post-Processing Logic (`post_processor.py`)
* **Dynamic Prefix Discovery**: Prefix stems (e.g., `borr`, `bank`) are derived algorithmically from the **attribute names** of successfully assigned entities, not from the entity labels themselves.
* **Heuristic Sweep**: Applies name-based heuristics using LLM-discovered keywords and hardened safety defaults (e.g., `street`, `city`). Performs prefix-stripping (e.g., `borrstreet` -> `street`) to validate tags.
* **Authoritative Overrides**: Absolute final step. Case-insensitive matching for both attribute keys and internal property flags (e.g., `is_geographic`). Overrides explicitly overwrite previous LLM or heuristic values.

### 4. Cleaner Logic & Data Integrity
* **Mixed Value Quarantine**: Before cleaning, the system uses `pd.api.types.infer_dtype` to identify columns with inconsistent types. Outlier records (deviating from the dominant type) are unioned and moved to a coordinated quarantine CSV, then dropped from the pipeline to prevent type corruption.
* **Lightweight Profiling**: Generates a JSON metadata bundle (types, cardinality, null ratio, samples) used for both LLM grounding and post-process validation.

### 4. Reporting Architecture
* **Unified Type Inference**: `convert_to_DS_type()` abstracts native Python types and Logical Categories (numeric, text, datetime, categorical).
* **Dual Output**: Generates both a professional Markdown report (with backticks for fixed-width display) and a raw CSV replica in the `dd_parser_results` directory.
* **Signature Security**: Generates a `.signature` SHA-256 sidecar for the output matrix to ensure pipeline integrity without corrupting CSV headers.
* **Grounded Inference Design**: 
    * **Contextual Sidecar**: Integration point for `fg-data-profiling` to feed physical data reality (cardinality, sample values, inferred types) into the LLM context.
    * **Validation Loop**: The `MetadataPostProcessor` will use profile data to flag logical mismatches (e.g., LLM identifies "City" but profiler sees `float64`).

---

## ⚙️ Authoritative Config Contract (`config.yaml`)

```yaml
parser:
  entity_tagging:
    - geographic
  # Grounding: Physical data distribution injected into Phase 2 prompts
  overrides:
    LocationID:
      is_geographic: false
      provisional_entity_assignment: Lender
cleaner:
  quarantine_directory: quarantine
  quarantine_filename: isolated_records.csv
```

---

## 🧩 Key Code Snippet: Prefix-Stripping Heuristics
```python
def _apply_name_heuristics(self, df, target, keywords, prefixes):
    keywords_lower = {str(k).lower().strip() for k in keywords}
    col_name = f"is_{target}"
    for idx in range(len(df)):
        if df.at[idx, col_name]: continue
        attr_clean = str(df.at[idx, "attribute_name"]).lower().strip()
        
        # Direct match
        if any(attr_clean.endswith(kw) or attr_clean == kw for kw in keywords_lower):
            df.at[idx, col_name] = True
            continue
        
        # Prefix-stripped match
        for prefix in prefixes:
            p_lower = prefix.lower()
            if attr_clean.startswith(p_lower):
                stripped = attr_clean[len(p_lower):].lstrip('_').lstrip('-')
                if any(stripped == kw or stripped.startswith(kw) for kw in keywords_lower):
                    df.at[idx, col_name] = True
                    break
```

---

## 🎯 Resumption Backlog

1. **Grounded Inference Implementation**: 
    * **Task 4.1**: Enhance `null_profiler.py` or integrate `fg-data-profiling` to generate a lightweight JSON metadata bundle (cardinality, top 5 samples, inferred physical type).
    * **Task 4.2**: Update `orchestrator.py` to left-join this profile bundle with the Data Dictionary before LLM dispatch.
    * **Task 4.3**: Augment `LLMEntityClassifier` prompts to include the "Profile Sidecar" for improved zero-shot accuracy.
    * **Task 4.4**: Harden `post_processor.py` to use profile stats as an authoritative safety check against semantic hallucination.

---
*This stash ensures that the "Golden Rule" is maintained: any future updates must build upon the logic summarized here.*