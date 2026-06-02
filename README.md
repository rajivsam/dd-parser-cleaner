# dd-parser-cleaner: AI-Driven Data Preparation & Documentation

A specialized framework for automating data preparation documentation and preparing datasets for machine learning through AI-driven metadata discovery.

## 🌍 The Big Picture
KMDS is an initiative focused on developing documented, maintainable data science and ML projects using open-source tools and knowledge graphs. The `kmds-data-helper` was the first step in this journey—automatically building knowledge graphs from standard repository structures.

`dd-parser-cleaner` is a further refinement of this ecosystem. It targets **data preparation**, historically the most difficult and detail-loaded segment of any data science project. This tool provides:
1.  An **AI-driven framework** to generate comprehensive cleaning documentation.
2.  An **agent-driven interface** for developing datasets for ML featurization and analytics.

By capturing metadata during the cleaning phase, we create the foundation upon which future featurization logic is built.

## 🚀 Status & Roadmap
*   **Current State:** `dd-parser-cleaner` is feature-complete (v0.4.2).
*   **Short Term:** We will be releasing public examples of dataset migrations shortly.
*   **Future:** Development of specialized featurization modules for ML and analytics projects will begin once the migration examples are public.

## 📑 Documentation Strategy (Agent-First)
This project uses a **Markdown-Native documentation architecture** rather than traditional external sites.

*   **Why?** Keeping technical guides and design contracts as Markdown within the repo allows AI Agents (like your Migration Assistant) to "read" the documentation and provide better code suggestions.
*   **Where to look:** Human users should consult the `documents/` directory for methodology, and `USER_GUIDE.md` for quick-start instructions.

## 🛠️ Technical Constraints
*   **Offline First:** Optimized for batch processing without external streaming dependencies.
*   **Deterministic:** Ensures that running the same config on the same data yields the same results.
*   **Privacy-Centric:** All processing and LLM grounding (via local models) stay within your local environment.

## Core Capability Matrix

| Capability | Operational Impact |
| :--- | :--- |
| **AI Recommendations** | **Saves Hours:** Replaces manual data profiling with LLM-generated `cleaning_recommendations.md`. |
| **Clean Bucket Policy** | **De-risks Models:** Prevents "ghost" data and undocumented noise from leaking into ML training sets. |
| **Handshake Protocol** | **Audit-Ready:** Creates a formal, documented bridge between Raw Data and Logic Implementation. |
| **Agent Interface** | **AI-Native:** Designed for AI Assistants to autonomously implement complex, vectorized domain logic. |
| **Metadata Discovery API** | **Faster Featurization:** Programmatic access to semantic tags (Geographic, Risk, Financial) for ML pipelines. |

## 🚀 The KMDS Onboarding Flow

Moving a new client or project into the `dd-parser-cleaner` framework is now a guided, three-step process designed to eliminate configuration guesswork:

1.  **`init-workspace`**: Builds the authoritative KMDS directory structure (`data/`, `data_dictionary/`, `documents/`, `notebooks/`, `scripts/`) and initializes the `domain_logic.py` stub.
2.  **`location-helper`**: Acts as the verification gate and placement guide. It verifies that the KMDS structure is ready and defines the exact locations and column requirements for your source assets (Raw Data, Data Dictionary, and Narratives) so the automation can find them.
3.  **`bootstrap-config`**: The "Smart Scan." This utility discovers your placed assets, peeks at your data dictionary headers to identify the primary attribute column, and generates an authoritative `config.yaml` (including all necessary LLM prompt templates) to get you running in minutes.

## ⚙️ Installation

### Standard Installation (CLI Only)
```bash
pip install dd-parser-cleaner
```

### Installation with Notebook Support (Migration Assistant)
```bash
pip install "dd-parser-cleaner[notebook]"
```

## 🚀 Quick Start

### 1. Bootstrap Your Workspace
Initialize and configure your project without writing a single line of YAML:
```bash
uv run init-workspace ./my_project
# ... move your CSV files to ./my_project/data/ ...
uv run bootstrap-config ./my_project
```

### 2. Classification (The Handshake)
Synchronize metadata and execute semantic classification:
```bash
classify-entities
```

### 2. Cleaning (The Pipeline)
Run the cleaner to apply types, filters, and transformations grounded in the parser's metadata:
```bash
uv run clean-dataset --action full --workspace ./tests
```

---
*For detailed documentation and custom logic implementation, see the `documents/` directory and `USER_GUIDE.md`.*