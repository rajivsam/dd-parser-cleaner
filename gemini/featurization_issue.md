Here is a comprehensive Issue Summary you can use to initialize the next session. This encapsulates the gaps we discovered between data dictionary schema generation and real-world pipeline execution.

---

## 📑 Issue Summary: `dd_parser` Rework & Schema Synchronization

## 🔴 Problem Statement

The `featurization` pipeline relies on the automated Data Dictionary parser output (`sba_analysis_results.csv`) as its definitive source of truth for geographical feature grouping, tracking, and exclusion logic. However, end-to-end integration tests revealed structural mismatches, missing mappings, and inconsistent naming rules between the generated dictionary metadata and the raw/cleaned data files.

---

## 🔍 Identified Root Causes & Gaps

1. Schema Suffix Omissions (Missing Columns)

   * The Issue: The `dd_parser` completely missed identifying or listing complex organizational columns like Certified Development Company (`cdc_city`, `cdc_state`, `cdc_zip`) and third-party entity columns (`thirdpartylender_city`, `thirdpartylender_state`).
   * The Risk: Downstream modules miss these hidden geographical fields, leading to raw location text leaking directly into ML baseline engines or breaking clean data strippers.
2. Case Sensitivity Disconnects

   * The Issue: The parser outputs structural columns in PascalCase (e.g., `BorrStreet`, `BankCity`), while the upstream dataset and cleaning tools frequently output lowercase schemas (`borrstreet`, `bankcity`).
   * The Risk: Standard string lookups fail silently on basic identity mismatches, forcing backend scripts to require defensive case-insensitive lookup decorators.
3. Parser Metadata Row Contamination

   * The Issue: The data dictionary script prepends a custom descriptive tracking tag (`# DD-PARSER-SIGNATURE: PROCESSED-BY-LLAMA3.2`) directly onto the first line of the CSV.
   * The Risk: Standard CSV parsers (like `pandas.read_csv`) misinterpret this signature line as the lone column header, pushing the true tabular table headers down into the dataset array rows and causing compilation crashes.

---

## 🛠️ Required `dd_parser` Enhancements (Next Session Action Items)

When we return from the break, we will re-work the `dd_parser` to integrate the following criteria:

* Enforce Hardened Suffix Heuristics: Instruct the parser's entity-extraction prompt or post-processing layer to perform catch-all flag sweeps. If an attribute ends with `_street`, `_city`, `_state`, `_zip`, `_county`, or contains `district`, it must be explicitly flagged as `is_geographical = True`.
* Total Inventory Matching: Ensure the parser generates a schema that covers 100% of the incoming columns in the dataset rather than predicting standard entity patterns (Bank, Borrower, Project) and hallucinating or discarding complex prefixes (CDC, ThirdParty).
* Standardized Case/Output Formatters: Ensure name mappings are cleanly integrated with standard string cleaning utilities, keeping file metadata headers consistent with actual operational formats.
* Clean Metadata Exporting: Restructure the signature tag to be a standard file property or ensure it does not corrupt default file stream header row structures.

---

Enjoy your break! Whenever you are ready to jump into the `dd_parser` rewrite, just copy-paste or reference this issue layout, and we will update the extraction scripts to be completely bulletproof.
