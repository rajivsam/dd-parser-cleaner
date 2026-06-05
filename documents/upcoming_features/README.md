# � Upcoming Features

This folder contains **feature descriptions and design documents for features planned for future releases** of `dd-parser-cleaner`. Each document describes a proposed feature in detail.

---

## 📋 Current Upcoming Features

### **Datasheet Alignment & Transparency Features**
- **[datasheet_alignment.md](datasheet_alignment.md)** — Proposes 5 planned features for transparent dataset documentation:
  - Automated Datasheet Generation (`DATASHEET.md`)
  - Sensitive Attribute Guardian (ethical risk scanning)
  - Narrative Context Harvesting (documentation extraction)
  - Versioned Errata Ledger (`ERRATA.json`)
  - Usage Restriction Classifier (task fitness assessment)
  
  **Status**: Design phase. Ready for v0.5 implementation. Current v0.4.6 architecture supports these additions.

### **Featurization Tool (Modeling & Feature Engineering)**
- **[features_from_Provost_Fawcett.md](features_from_Provost_Fawcett.md)** — Modeling features derived from Provost & Fawcett's CRISP-DM methodology:
  - Supervised Task Identifier
  - Leakage Sentinel
  - Similarity & Link Prediction
  - Causal Logic Check
  
  **Status**: Strategic planning. Bucket 1: Future Tool. Separate product from current Cleaner.

- **[features_from_Pyles_text.md](features_from_Pyles_text.md)** — Modeling features derived from Dorian Pyle's data preparation methodology:
  - Future Leakage Check
  - Missing Data Signatures
  - Dataset Readiness Grade
  - Information Shadow Analysis
  
  **Status**: Strategic planning. Bucket 1: Future Tool. Part of planned "Featurization Tool".

---

## 🎯 Feature Prioritization & Timeline

| Feature | Complexity | Dependencies | Estimated Release |
|---------|-----------|--------------|-------------------|
| Datasheet Generation | Low | Parser/Cleaner output | v0.5 |
| Sensitive Attribute Guardian | Low | LLM prompt expansion | v0.5 |
| Narrative Context Harvesting | Medium | Document processor enhancement | v0.5–v0.6 |
| Errata Ledger | Low | IntegrityEngine extension | v0.5 |
| Usage Restriction Classifier | Low | LLM logic expansion | v0.5 |
| Featurization Tool | High | New architecture | v1.0+ |

---

## 📌 How to Use This Directory

- **For feature planning**: Reference these documents when prioritizing upcoming work
- **For implementation**: Each document includes "Design Approach" and "Architecture Impact" sections to guide development
- **For current v0.4.6 usage**: These features are NOT yet implemented; refer to parent `documents/` directory for active documentation
  - `stash.md` — Authoritative v0.4.6 state
  - `transfer_to_migration.md` — Agent-Programmer's Handbook
  - `cleaner_design.md` — Diagnostic pipeline
  - `path_coordinator_design.md` — Path routing
  - `config_setup.md` — Configuration reference

---

**Last Updated**: June 5, 2026  
**Current Baseline**: v0.4.6 (Maintenance Mode)  
**Next Target Release**: v0.5 (Datasheet & Transparency Features)

**Last Updated**: June 5, 2026
