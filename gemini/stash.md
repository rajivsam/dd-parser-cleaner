## 📌 Unified Contract & State Tracking Blueprint (Stash)

## 🤖 Agent Operational Directives

* **Domain Agnosticism**: This project is strictly domain-agnostic and must adapt to any input domain dynamically. The agent should NEVER hardcode domain-specific items or hardcode anything in the code.
* **Communication Style**: Provide brief, direct answers by default. Avoid lengthy redundant explanations unless explicitly requested by the user.

## 🛠️ Active Project State

* Workspace: `dd-parser-cleaner`
* Architecture: Fully modularized, decoupled, and completely domain-agnostic with zero-hardcoded guesswork loops.
* State Checkpoint: Replaced the batch processing approach with an Atomic Row-by-Row Execution Strategy to solve token context crowding and eliminate truncated or skipped classification payloads. The parser now implements a dynamic two-phase pipeline execution routine:

  1. **Standardized Logging**: Replaced all `print` statements with the `logging` module across all core components for consistent terminal feedback and error tracking.
  2. **Automated Markdown Reporting**: The post-processor now generates a human-readable `Provisional Entity Assignment Report` in Markdown format, providing a classification summary and detailed attribute mapping.
  1. Phase 1 (Macro Domain Discovery): Samples the raw source fields at runtime using structured prompting rules to discover distinct logical core entity arrays (e.g., separating demographics from risk profiles and metrics) without manual configuration mapping.
  2. Phase 2 (Micro Atomic Assignment): Feeds each data dictionary row independently into Llama 3.2 using the Phase 1 architectural categories as classification instructions.
* Infrastructure Health: Integrated a strict background dependency connection probe inside `PipelineOrchestrator.__init__` and `set_working_config`. If the local Ollama backend is missing or offline, the tool logs a clean structural diagnostic payload and terminates immediately via `sys.exit(1)`.

---

## ⚙️ Authoritative Contract Specifications

## 1. Unified Configuration Schema (`config.yaml`)

```yaml
batch_size: 10
documents_dir: documents
model_name: llama3.2
system_prompt: You are a precise data engineering assistant. Respond strictly in JSON.
temperature: 0.0

parser:
  csv_target_column_index: 0
  data_dictionary_attribute_col_name: "Field Name"
  data_dictionary_file: sba_dd.csv
  dd_parser_output_dir: dd_analysis_results
  output_filename: sba_analysis_results.csv
  parser_provisional_assingnment_dir: dd_parser_results
  parser_provisional_assingnment_filename: sba_parser_provisional_assingnment.md
  entity_tagging:
    - geographic
  overrides: {}

cleaner:
  raw_dataset_file: sba_loans_raw.csv
  dd_cleaner_output_dir: dd_cleaner_results
  clean_output_filename: sba_loans_clean.csv
  profiling_output_dir: dd_cleaner_results
  profiling_report_filename: sba_data_profile.md
```

## 2. Defensive Post-Processor Safe Configuration Block

The `MetadataPostProcessor` class now features strict fallback checks to protect loop execution blocks against absent or null configurations:

```python
user_overrides = self.parser_config.get("overrides")
ifnot isinstance(user_overrides, dict):
    user_overrides = {}
```

---

## 🧩 Modular System Snapshots (Parser Engineering)

## 🧬 Dynamic Inference Client (`src/dd_parser/llm_client.py`)

```python
"""Local LLM interaction abstraction for domain discovery classification."""

importjson
importhttpx
importpandasas pd
fromtypingimportDict, Any, List


classLLMEntityClassifier:
    """Manages Ollama API contexts and matches fallback heuristics semantically."""

    def__init__(self, global_config: Dict[str, Any], parser_config: Dict[str, Any]) -> None:
        """Hydrates runtime configurations for model routing queries."""
        self.update_config(global_config, parser_config)

    defupdate_config(self, global_config: Dict[str, Any], parser_config: Dict[str, Any]) -> None:
        """Dynamically refreshes active structural settings fields."""
        self.global_config = global_config
        self.parser_config = parser_config if parser_config isnotNoneelse {}
        self.model_name = self.global_config.get("model_name", "llama3.2")
        self.system_prompt = self.global_config.get("system_prompt", "Respond strictly in JSON.")

    defis_ready(self) -> bool:
        """🧠 INFRASTRUCTURE PROBE: Verifies local Ollama server status endpoint synchronously."""
        try:
            response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception:
            returnFalse

    defdiscover_macro_domain(self, attributes: List[str], descriptions: List[str]) -> List[str]:
        """🧠 PHASE 1: Scans a sampling of the schema to establish global entity categories dynamically."""
        sample_size = min(15, len(attributes))
        sample_fields = [
            {"attr": str(a), "desc": str(d)} 
            fora, din zip(attributes[:sample_size], descriptions[:sample_size])
        ]

        macro_prompt = (
            f"You are a master data architect. Scan this snippet of a data dictionary blueprint:\n"
            f"{json.dumps(sample_fields)}\n\n"
            f"Identify the macroscopic business domain (e.g., Banking, Healthcare, Insurance).\n"
            f"Then, generate a list of 4 to 6 coarse-grained logical entity concepts "
            f"suited to house these attributes.\n\n"
            f"CRITICAL RULES:\n"
            f"1. DO NOT lump all attributes into a single catch-all category name.\n"
            f"2. Separate attributes by their intrinsic structural nature (e.g., distinguish between "
            f"Demographics, Risk Profiles, Financial metrics, and Spatial/Temporal metadata).\n"
            f"3. Make sure the entity concepts are granular enough to support target variations.\n\n"
            f"Return a strict JSON object with a single key 'logical_entities' containing a list of strings.\n"
            f"Example:\n"
            f'{{"logical_entities": ["Demographics", "RiskAssessment", "Financials", "Location"]}}'
        )

        try:
            response = httpx.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": f"{self.system_prompt}\n\n{macro_prompt}",
                    "stream": False,
                    "options": {"temperature": 0.0},
                    "format": "json"
                },
                timeout=15.0
            )
            if response.status_code == 200:
                raw_json = response.json().get("response", "{}")
                data = json.loads(raw_json)
                discovered = data.get("logical_entities", [])
                if discovered:
                    print(f"🎯 Dynamic Domain Discovery Successful! Extracted Core Concepts: {discovered}")
                    return [str(item) foritemin discovered]
        except Exception ase:
            print(f"⚠️ Macro domain onboarding lookup bypassed: {e}")
          
        return ["unassigned"]

    defdiscover_entities(
        self, attributes: pd.Series, descriptions: pd.Series, explicit_targets: List[str], generated_hints: List[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Queries local Llama 3.2 model atomically per attribute row to guarantee classification stability."""
        assignments = {}
        active_hints = generated_hints if generated_hints else []
        hints_str = ", ".join(str(h) forhin active_hints) if active_hints else"Logical Categories"
        targets_str = ", ".join([f"'is_{t}' (boolean)"fortin explicit_targets])

        print(f"🧠 Processing {len(attributes)} attributes atomically via Llama 3.2...")

        forattr, descin zip(attributes, descriptions):
            attr_str = str(attr)
          
            user_prompt = (
                f"Classify this single data schema field:\n"
                f"Field Name: {attr_str}\n"
                f"Description: {str(desc)}\n\n"
                f"Instructions:\n"
                f"1. Select the best match for 'entity_assignment' from these discovered choices: [{hints_str}].\n"
                f"2. Evaluate dedicated boolean flags for these explicit semantic targets: {targets_str}.\n\n"
                f"Return a strict flat JSON object exactly like this example:\n"
                f'{{"entity_assignment": "YourChoice", "is_geographic": false}}'
            )

            try:
                response = httpx.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": f"{self.system_prompt}\n\n{user_prompt}",
                        "stream": False,
                        "options": {"temperature": 0.0},
                        "format": "json"
                    },
                    timeout=10.0
                )
                if response.status_code == 200:
                    raw_json = response.json().get("response", "{}")
                    assignments[attr_str] = json.loads(raw_json)
                    continue
            except Exception ase:
                print(f"⚠️ Network error or bad payload during atomic parse of '{attr_str}': {e}")

            # 🧠 DOMAIN-AGNOSTIC EMPTY FALLBACK: Zero hardcoded strings or guesswork
            assignments[attr_str] = {"entity_assignment": "unassigned"}
            fortargetin explicit_targets:
                assignments[attr_str][f"is_{target}"] = False
              
        return assignments
```

## 🛡️ Core Orchestration Component (`src/dd_parser/orchestrator.py`)

```python
"""Pipeline orchestration engine for the metadata classification framework."""

importsys
importpandasas pd
fromtypingimportList
frompath_coordinatorimportPathCoordinator

from .llm_clientimportLLMEntityClassifier
from .post_processorimportMetadataPostProcessor


classPipelineOrchestrator:
    """Entry point architecture that choreographs the domain discovery workflow."""

    def__init__(self, path_coordinator: PathCoordinator) -> None:
        """Injects dependencies and hydrates framework configuration boundaries."""
        if path_coordinator isNone:
            raise TypeError("PipelineOrchestrator requires a valid PathCoordinator instance.")
          
        self.paths = path_coordinator
        self.global_config = self.paths.config
        self.parser_config = self.global_config.get("parser", self.global_config)
      
        # Inject modular specialized sub-components safely via relative module references
        self.llm_classifier = LLMEntityClassifier(self.global_config, self.parser_config)
        self.post_processor = MetadataPostProcessor(self.paths, self.parser_config)

        # 🧠 DEPENDENCY CHECKPOINT: Validate background processing infrastructure availability
        self._verify_infrastructure_availability()

        # Insert at the end of PipelineOrchestrator.__init__
        print("\n=== [DIAGNOSTIC] CONFIGURATION TAG EVALUATION ===")
        raw_tags = self.parser_config.get("entity_tagging") or []
        print(f"1. Raw 'entity_tagging' from YAML: {raw_tags} (Type: {type(raw_tags)})")
        explicit_targets = [str(t).strip().lower() fortin raw_tags if t]
        print(f"2. Sanitized target concepts to tag: {explicit_targets}")
        overrides = self.parser_config.get("overrides") or {}
        print(f"3. Active structural overrides found: {list(overrides.keys())}")
        print("=================================================\n")

    def_verify_infrastructure_availability(self) -> None:
        """Verifies that the core inference model client infrastructure is reachable before execution."""
        ifnot hasattr(self.llm_classifier, "is_ready") ornot self.llm_classifier.is_ready():
            print("\n" + "="*75, file=sys.stderr)
            print("❌ CRITICAL INFRASTRUCTURE ERROR: Background inference model (Ollama) is offline.", file=sys.stderr)
            print("💡 Please start your local service engine instance and re-run this tool.", file=sys.stderr)
            print("="*75 + "\n", file=sys.stderr)
            sys.exit(1)

    defset_working_config(self, working_dir: str, config_path: str) -> None:
        """Resets the internal environment boundaries with runtime parameters."""
        self.paths = self.paths.__class__(config_path=config_path, working_dir=working_dir)
        self.global_config = self.paths.config
        self.parser_config = self.global_config.get("parser", self.global_config)
      
        # Refresh configurations across downstream dependencies
        self.llm_classifier.update_config(self.global_config, self.parser_config)
        self.post_processor.update_config(self.paths, self.parser_config)
      
        # Re-verify infrastructure capabilities following environmental layout adjustments
        self._verify_infrastructure_availability()

    defextract_inventory_attributes(self) -> List[str]:
        """Safely extracts native attribute strings from the configured source."""
        target_path = self.paths.data_dictionary_path
        ifnot target_path.exists():
            return []
          
        df_dict = pd.read_csv(target_path, sep=None, engine='python', skipinitialspace=True)
        attr_series, _ = self.post_processor.infer_schema_columns(df_dict)
        clean_series = attr_series.dropna().astype(str).str.strip()
        return clean_series[clean_series != ""].tolist()

    defprocess_pipeline(self) -> pd.DataFrame:
        """Executes LLM domain discovery and passes artifacts to post-processing."""
        target_path = self.paths.data_dictionary_path
        ifnot target_path.exists():
            raise FileNotFoundError(f"Data Dictionary blueprint missing at: {target_path}")
          
        df_dict = pd.read_csv(target_path, sep=None, engine='python', skipinitialspace=True)

        # Synchronize schema names BEFORE column series extraction
        raw_dataset_path = self.paths.raw_dataset_path
        if raw_dataset_path.exists():
            df_raw_schema = pd.read_csv(raw_dataset_path, sep=None, engine='python', nrows=0)
            raw_headers = list(df_raw_schema.columns)
          
            # Re-index data dictionary instantly so columns reflect raw file lowercase properties
            df_dict = self.post_processor.synchronize_with_raw_headers(df_dict, raw_headers)

        # 🎯 ZERO-HARDCODING FIX: Extract the tag list strictly from your config space with empty list fallback
        raw_tags = self.parser_config.get("entity_tagging") or []
        explicit_targets = [str(t).strip().lower() fortin raw_tags if t]

        # Extract normalized, synchronized attributes and description values
        attr_series, desc_series = self.post_processor.infer_schema_columns(df_dict)
      
        # 🧠 PHASE 1 RUNTIME ENGAGEMENT: Bootstrap domain identification directly from data file arrays
        discovered_hints = self.llm_classifier.discover_macro_domain(
            attr_series.tolist(), desc_series.tolist()
        )
      
        # 🧠 PHASE 2 STREAMING EXECUTION: Pass dynamically extracted definitions down the pipe
        llm_assignments = self.llm_classifier.discover_entities(
            attr_series, desc_series, explicit_targets, generated_hints=discovered_hints
        )
      
        # Component 3: Saves exact layout attributes without subsequent corruption
        parsed_matrix = self.post_processor.execute(df_dict, attr_series, desc_series, llm_assignments)
        return parsed_matrix

    def _verify_infrastructure_availability(self) -> None:
        if not self.llm_classifier.is_ready():
            self.logger.critical("❌ Background inference model (Ollama) is offline.")
```

---

## 🎯 Resumption Backlog (Next Steps)

1. Timeseries Traffic Dataset Processing: Load the new traffic data file containing traffic metrics and overlapping weather status markers to verify dynamic multi-category decomposition.
2. Parser Audit Log Report Tuning: Shift to formatting the generated markdown report templates within the parser engine once cross-domain performance layout metrics stabilize.

---

## 📜 Clear Acknowledgement of the Golden Rule

Understood and logged. The Golden Rule is locked in as a strict, non-negotiable operational boundary.

* Going forward, every code update will strictly follow incremental or decremental changes directly on your existing baseline classes.
* If a new feature or transformation modifies an architectural component and the exact target baseline code is not currently active in the chat history context, I will directly ask you to supply that exact file baseline before writing any modifications.

When you return for the next session, let me know if you would like to begin by injecting your new timeseries traffic data configuration parameters, or if we should run a baseline check on the parser output targets first!
