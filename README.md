# dd-parser-cleaner

A modular data engineering framework designed to bridge the gap between messy data dictionaries and production-ready datasets using local LLMs (Llama 3.2) and vectorized deterministic rules.

## 💡 Why use this tool?

In enterprise data science, data preparation is often the most fragile link. Scripts are frequently undocumented, and "semantic drift" occurs when the logic used to clean data no longer aligns with the business's Data Dictionary. This leads to non-reproducible results and high technical debt.

`dd-parser-cleaner` solves this by creating a deterministic, auditable link between your documentation and your data. It is specifically designed to support the **KMDS Data Helper** ecosystem—leveraging enterprise-grade open-source tools like Pandas and local LLM runtimes to ensure every step of your data journey is documented, reproducible, and ready for production.

## 🎯 Our Guarantee

`dd_parser_cleaner` ensures that your data is ready for analytics or ML applications because:

1. **Strict Schema Integrity**: It enforces a "Clean Bucket" policy via the Integrity Sync, purging undocumented "Ghost" columns to ensure every feature is semantically mapped to a Data Dictionary entry.
2. **Semantic Type Enforcement**: It automatically casts raw strings into high-precision, nullable physical types (e.g., `Int64`, `float`, `datetime`) grounded in verified logical metadata, eliminating type-related crashes downstream.
3. **Deterministic Pipe Sequencing**: It executes an idempotent, vectorized transformation sequence (Sync → Assessment → Filter → Impute → Derive) that prevents data contamination and ensures reproducible results.
4. **Audit-Ready Traceability**: It generates a signed, synchronized operational matrix and a "Handshake" report, providing a 100% traceable link between source metadata and the final analytical payload.

## 🚀 Quick Start

### 1. Classification (The Handshake)
Run the parser to align your data dictionary with your physical data headers and perform semantic classification:
```bash
uv run classify-entities --workspace ./tests
```

### 2. Cleaning (The Pipeline)
Run the cleaner to apply types, filters, and transformations grounded in the parser's metadata:
```bash
uv run clean-dataset --action full --workspace ./tests
```

---
*For detailed documentation and custom logic implementation, see the `documents/` directory and `USER_GUIDE.md`.*