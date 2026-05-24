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

### 4. Reporting Architecture
* **Unified Type Inference**: `convert_to_DS_type()` abstracts native Python types and Logical Categories (numeric, text, datetime, categorical).
* **Dual Output**: Generates both a professional Markdown report (with backticks for fixed-width display) and a raw CSV replica in the `dd_parser_results` directory.
* **Signature Security**: Generates a `.signature` SHA-256 sidecar for the output matrix to ensure pipeline integrity without corrupting CSV headers.

---

## ⚙️ Authoritative Config Contract (`config.yaml`)

```yaml
parser:
  entity_tagging:
    - geographic
  overrides:
    LocationID:
      is_geographic: false
      provisional_entity_assignment: Lender
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
1. **Scale Testing**: Run the pipeline against a synthetic 5,000-row schema to verify LLM latency and memory usage.
2. **HITL UI**: Build a lightweight terminal interface to allow the user to approve/edit classifications before the final matrix is signed.
3. **Timeseries Integration**: Test the dynamic multi-category decomposition on the new traffic/weather datasets.

---
*This stash ensures that the "Golden Rule" is maintained: any future updates must build upon the logic summarized here.*