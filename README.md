# dd-parser-cleaner: Enterprise Pipeline Governance Engine

An offline metadata parsing and pipeline governance engine that enforces data provenance and automated schema serialization at the ingestion boundary.

## Technical & Architectural Constraints
This system is built under strict architectural constraints to ensure stability in production enterprise environments:
* **Zero Streaming Footprint:** Exclusively optimized for offline, design-time, and batch processing pipelines.
* **Deterministic Execution:** Operates as a stateless execution wrapper over data ingestion blocks.
* **No Telemetry Leakage:** All metadata parsing, validation, and serialization occur entirely within your closed local or cloud perimeter.

## 📑 Documentation Strategy (Agent-First)
This project utilizes a **Markdown-Native documentation architecture** instead of traditional external sites like ReadTheDocs.

*   **Rationale:** By keeping all technical specifications, design contracts, and implementation guides as structured Markdown files within the repository, we maximize the grounding performance of AI Coding Assistants. This "Agent-First" approach ensures that Migration Assistants can reason about your specific data pipelines with zero external latency or context drift.
*   **Where to look:** Human users seeking authoritative technical methodology should consult the `documents/` directory. For operational workflows and quick-start tutorials, refer to `USER_GUIDE.md`.

## Executive Summary
dd-parser-cleaner eliminates pipeline technical debt by intercepting batch data transfers and programmatically locking down data state, lineage, and structural metadata. It converts runtime data execution into audit-ready JSON/Markdown documentation, guaranteeing absolute reproducibility for downstream batch optimization matrices. This architecture provides **significant time savings for Data Science and ML teams** by automating the most fragile link in the analytical chain: data preparation and semantic alignment.

## Core Capability Matrix

| Capability | Operational Impact |
| :--- | :--- |
| **Deterministic State Capture** | Automatically serializes dataset shapes, cryptographic hashes, data types, and ingestion timestamps to prevent downstream model drift. |
| **Zero-Overhead Schema Extraction** | Generates machine-readable JSON metadata payloads directly from batch dataframes, decoupling physical schema properties from pipeline code. |
| **Automated Pipeline Lineage** | Compiles runtime execution state into standardized, human-readable Markdown asset logs for enterprise compliance reviews. |
| **Strict Schema Integrity** | Enforces a "Clean Bucket" policy via Integrity Sync, purging undocumented columns to ensure 1:1 semantic mapping. |
| **Metadata Discovery API** | Provides a programmatic interface for notebooks to query semantic tags, enabling seamless integration with ML pipelines. |

## 🚀 Quick Start

### 1. Classification (The Handshake)
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