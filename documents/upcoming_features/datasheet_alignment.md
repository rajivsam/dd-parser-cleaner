# 📋 Datasheet Alignment: Strategic Design

## 🎯 The Importance of Datasheet Transparency

Modern AI and Data Science often suffer from a "transparency gap." While code is version-controlled and documented, the datasets that feed the code are often treated as black boxes. The foundational paper **"Datasheets for Datasets" (Gebru et al.)** identifies this as a primary source of bias, misuse, and maintenance failure.

Acknowledging this requirement is important because:
1. **Trust and Safety**: Users must know where data came from and what its limitations are before building models.
2. **Regulatory Compliance**: Global standards (like the EU AI Act) are increasingly requiring documented data lineage.
3. **Maintenance Integrity**: Data changes over time. Documentation ensures that "dataset drift" is visible and manageable.

By aligning `dd-parser-cleaner` with this standard, we transform the tool from a technical cleaner into a **transparency agent**.

---

## 🚀 Proposed Features for dd-parser-cleaner

Based on our analysis of the Gebru framework, the following five features are planned for the next evolution of the tool.

### 1. Automated Datasheet Generation (`DATASHEET.md`)
**The Feature**: A command-line utility that automatically compiles the results of the parsing, profiling, and integrity checks into a standardized Markdown report following the Gebru template.
**Design Approach**: 
*   **Source Data**: Aggregates the existing JSON outputs from the `DatasetDataProfiler` and `IntegrityEngine`.
*   **Implementation**: A "Reporting Layer" will map technical metrics (null counts, type distributions) to datasheet sections (Composition, Preprocessing). It will use a pre-defined Markdown template to ensure consistency.

### 2. Sensitive Attribute Guardian (Ethical Risk Scanning)
**The Feature**: An LLM-driven classification step that identifies if specific columns represent "protected classes" (e.g., race, gender, religion) or sensitive PII.
**Design Approach**: 
*   **Expansion**: Update the `entity_discovery_template` in `src/dd_common/llm_prompts.py` to include a boolean flag `is_sensitive`.
*   **Inference**: The LLM will evaluate the field name and description against ethical risk categories. If flagged, the tool will append a "Usage Warning" to the generated datasheet.

### 3. Narrative Context Harvesting
**The Feature**: The ability to extract non-technical metadata such as "Motivation," "Funding Sources," and "Collection Methods" from project documentation.
**Design Approach**: 
*   **Enhancement**: The `DocumentProcessor` will be extended with a "Narrative Summary" mode. 
*   **Workflow**: Instead of looking for magic numbers, it will scan documents in the `documents/` directory for specific keywords associated with the Gebru "Motivation" and "Collection" sections, summarizing its findings for the final datasheet.

### 4. Versioned Errata Ledger (`ERRATA.json`)
**The Feature**: A structured, machine-readable log of every data point that was modified or removed during the cleaning process.
**Design Approach**: 
*   **Persistence**: As the `IntegrityEngine` identifies "Ghosts," "Orphans," or "Mixed-Value" records, it will write their metadata to a sidecar file named `ERRATA.json`.
*   **Integrity**: This file acts as a living history of the dataset’s flaws, allowing "Dataset Consumers" to see exactly what was moved to the `quarantine/` folder and why.

### 5. Usage Restriction Classifier
**The Feature**: An LLM-generated assessment that explicitly states what tasks the dataset is *unfit* for based on its structural quality.
**Design Approach**: 
*   **Logic**: The `CleaningAssistant` will compare the final data profile against a list of "High-Stakes Tasks" (e.g., credit scoring, medical diagnosis).
*   **Output**: If a dataset has high nullity in critical fields (like `TransactionAmount` or `DiagnosisCode`), the tool will generate a "Negative Constraint" statement: *"This dataset is not recommended for financial auditing due to a 40% missing value rate in core metrics."*

---

## 🛠️ Implementation Summary

| Feature | Architecture Impact | Primary Component |
| :--- | :--- | :--- |
| **Datasheet Export** | Low (New Output) | `ReportingModule` |
| **Sensitivity Scan** | Low (Prompt Change) | `LocalEntityClassifier` |
| **Narrative Harvest**| Medium (New Prompts) | `DocumentProcessor` |
| **Errata Ledger**   | Low (New Persistence) | `IntegrityEngine` |
| **Usage Constraints**| Low (Prompt Change) | `CleaningAssistant` |

The existing v0.4.6 architecture is already robust enough to support these additions without major refactoring.

<!--
[PROMPT_SUGGESTION]Draft an updated version of the entity_discovery_template that includes a sensitivity scan for protected classes.[/PROMPT_SUGGESTION]
[PROMPT_SUGGESTION]Design a draft JSON schema for the ERRATA.json sidecar to track quarantined records over time.[/PROMPT_SUGGESTION]
-->