# 📑 Location Helper Utility: Detailed Design

## 🎯 Purpose
The `location-helper` utility is designed to guide users on the correct placement of their raw data files, data dictionaries, and narrative documents within an initialized `dd-parser-cleaner` workspace. It acts as a crucial onboarding tool, ensuring users understand the expected file structure and how their `config.yaml` settings influence file discovery.

This utility addresses the "where to place what document" question, serving as a logical follow-up to the `init-workspace` command.

## 🚀 Core Functionality
The `location-helper` performs the following steps:

1.  **Workspace Pre-check**:
    *   It first verifies if the provided `working_dir` (or the current directory) is an initialized `dd-parser-cleaner` workspace by calling `dd_common.utilities.verify_workspace_status()`.
    *   If the workspace is not initialized (i.e., the core `data`, `data_dictionary`, `documents`, `notebooks`, and `scripts` directories are missing), it will print an error message, instruct the user to run `init-workspace`, and exit with a non-zero status code.

2.  **Structural Guidance (Pre-Configuration)**:
    *   Since this utility is run immediately after `init-workspace` and before a `config.yaml` is created, it provides static guidance on the KMDS file placement standards.
    *   It then outputs clear instructions for each type of document:
        *   **Raw Data (CSV)**:
            *   Recommends placing the file in the `./data/` directory.
            *   Indicates the future config key: `cleaner.raw_dataset_file`.
        *   **Data Dictionary (CSV)**:
            *   Recommends placing the file in the `./data_dictionary/` directory.
            *   Indicates future config keys: `parser.data_dictionary_file` and `parser.data_dictionary_attribute_col_name`.
            *   **Highlights Required Columns**: Specifically mentions that the file must contain an attribute column (matching physical headers) and a description column for AI semantic context.
        *   **Narrative Documents (MD/PDF)**:
            *   Recommends placing domain SOPs or requirements in the `./documents/` directory.
            *   Indicates the future config key: `documents_dir`.

3.  **User Feedback**:
    *   Provides a clear summary and informs the user that the next step involves a bootstrapping utility to create the `config.yaml`.

## 💻 CLI Usage
The `location-helper` utility is exposed as a CLI command:

```bash
uv run location-helper [working_dir]
```

*   `working_dir`: (Optional) The path to the workspace directory. If omitted, the current working directory (`.`) is used.

## 🤝 Interaction with Other Components

*   **`init-workspace`**: The `location-helper` explicitly depends on `init-workspace` having been run first. It enforces this dependency through its pre-check.
*   **Bootstrapping Utility (Future)**: The `location-helper` prepares the user for the next phase where a configuration-bootstrapping tool will scan the directories and generate the initial `config.yaml`.

## 🎨 Output Format
The output is designed to be user-friendly and actionable, using emojis for visual cues and clear headings to segment information.

```
📍 [KMDS Location Helper] for: /path/to/your/workspace
------------------------------------------------------------

📂 1. RAW DATA (CSV)
   Place your source data file in: ./data/
   💡 This is your primary operational table (e.g., 'raw_data.csv').
   Config key (future): cleaner.raw_dataset_file

📂 2. DATA DICTIONARY (CSV)
   Place your metadata schema in: ./data_dictionary/
   💡 Required Columns:
      - Attribute column (e.g., 'Field Name'): Maps to your data headers.
      - Description column: Provides semantic context for AI discovery.
   Config key (future): parser.data_dictionary_file
   Config key (future): parser.data_dictionary_attribute_col_name

📂 3. NARRATIVE DOCUMENTS (MD/PDF)
   Place domain SOPs or requirements in: ./documents/
   💡 These files help the agent extract domain thresholds and logic.
   Config key (future): documents_dir

------------------------------------------------------------
✅ Once files are placed, the next utility will help you bootstrap your config.yaml.
```

## 📈 Future Considerations
*   **`config.yaml` Generation**: Potentially integrate a feature to generate a basic `config.yaml` template if one is missing, pre-populating it with default filenames.
*   **File Existence Check**: Enhance the helper to optionally check if the files specified in `config.yaml` (e.g., `raw_dataset_file`, `data_dictionary_file`) actually exist at their designated locations.