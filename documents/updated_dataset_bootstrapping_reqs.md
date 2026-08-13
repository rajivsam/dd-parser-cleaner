
------------------------------
## Dataset Bootstrapping Specification & CLI Layout Blueprint## 1. Architectural Purpose
Introduce a interactive CLI bootstrapping phase in dd-parser-cleaner to capture dataset metadata before config generation. This ensures downstream components receive correct dataset taxonomy and subject-level signals.
This layout blueprint translates semantic data modeling concepts into a strict terminal interface, standardizing text prompts, component styles, and data validation rules.
------------------------------
## 2. Global CLI Terminal Component Design
To ensure a consistent user experience, implement all interactive steps using the following terminal components (leveraging a library like questionary or inquirer):

* [Select] / List Component: Vertical navigApplying this file-selection filter to the data_dictionary/ folder rounds out the workspace verification. It ensures that any backup dictionaries, scratchpad text files, or outdated sheets do not corrupt downstream schema parsing.
By unifying this layout validation into Step 0: Workspace Verification, the CLI establishes a clean "Source of Truth" (exactly one data file and exactly one data dictionary file) before Step 1 even runs.
------------------------------
## Revised Step 0 & Step 1 Logic with Workspace Cleanup
Here is how the combined verification and selection flows look programmatically:
## Step 0: Workspace verification

* The utility checks that the target directory is an initialized workspace containing data/ and data_dictionary/ folders.
* It scans both directories, logs the file counts, and prompts the user to resolve ambiguity if redundant or backup files are found.

## Data Directory Resolution

* If Multiple files found in data/:

I see multiple files in your 'data/' directory. How should these be treated?
1) Connected components: They are all related parts of a single network/relational dataset.
2) Independent/Redundant: They are separate copies or backups. Only ONE specific file matters.

* If Option 1 (Connected) → Cache all files for the Multi-File Graph Check in Step 1.
   * If Option 2 (Independent) → Display a selective menu of the CSV files, prompt the user to pick the active file, ignore the others, and tag this execution path for the Single Data File Flow in Step 1. [1] 

## Data Dictionary Resolution

* If Multiple files found in data_dictionary/:

I see multiple schema files in your 'data_dictionary/' directory. Only one active metadata mapping can be used. Please select the correct file for this configuration:
[Display all discovered files in data_dictionary/...]

* Cache the selected file path as the absolute source of truth for downstream bootstrap-config executions.

------------------------------
## Complete Redrafted Specification Document
Here is the final, hardened specification integrating both folder gatekeepers.

# Dataset Bootstrapping Specification## PurposeIntroduce a dedicated bootstrapping phase in `dd-parser-cleaner` to capture dataset metadata before config generation. This ensures the parser, cleaner, and notebook metadata flows receive the correct dataset taxonomy and subject-level signals. It replaces manual dataset-type assignment with an interactive inference flow that isolates tabular layouts, structural edge lists, and node-list graph learning tasks while automatically resolving messy or redundant workspace directories.
---## Bootstrapping Flow### Step 0: Workspace Verification & File Clean-UpThe utility checks that the target directory is an initialized workspace containing `data/` and `data_dictionary/` folders. It safely filters out redundant, old, or backup files using explicit user confirmation.
#### 1. Data File Target Resolution- The utility scans the `data/` folder for files.- **If a single file is found:** Cache it as the target dataset and route to **Branch B (Single Data File Flow)**.- **If multiple files are found:** Prompt the user to establish their analytical relationship:

I see multiple files in your 'data/' directory. How should these be treated?

   1. Connected components: They are all related parts of a single network/relational dataset.
   2. Independent/Redundant: They are separate copies or backups. Only ONE specific file matters.

- **If Option 1 (Connected):** Cache all files and route to **Branch A (Multiple Data Files Flow)**.
- **If Option 2 (Independent):** Present a selection menu:
  ```
  Please select the single data file you want to use for this analysis:
  [List detected data files...]
  ```
  Cache the chosen file, ignore the remaining files, and route to **Branch B (Single Data File Flow)**.

#### 2. Data Dictionary Target Resolution
- The utility scans the `data_dictionary/` folder for files.
- **If a single file is found:** Cache it as the absolute metadata schema file.
- **If multiple files are found:** Present an immediate resolution prompt:

I see multiple files in your 'data_dictionary/' directory. Only one active metadata schema can be used. Please select the correct file for this configuration:
[List detected dictionary files...]

Cache the selected file and completely ignore the redundant copies.

---

### Step 1: Structural & Intent Inference (Graph vs. Tabular)
Using the clean file targets established in Step 0, the CLI dynamically branches.

#### Branch A: Multiple Data Files Flow
- **System Presentation:** "Based on your input, your use case spans multiple distinct subjects (e.g., Users, Products, Logs) interacting with each other."
- **Action:** Proceed directly to the **Multi-File Graph Check**.

#### Branch B: Single Data File Flow
- **System Presentation:** The CLI prompts the user to define the semantic layout of the rows within the selected file:

In your data file, does a single row represent a static profile/event of ONE subject, or does it represent an interaction between TWO OR MORE subjects?

   1. One subject (e.g., a customer profile, a single sensor log line).
   2. An interaction, link, or transaction between subjects (e.g., User A followed User B, IP X pinged IP Y).

- **Routing:**
- If **Option 2 (Interaction)** → Proceed to **Edge List Homogeneity Check**.
- If **Option 1 (One Subject)** → Trigger the **Intent Check** to catch Node-List graph learning and isolate standard clustering:
  ```
  Structurally, this is a single file with one row per subject. What is your primary analysis goal?
  1) Analyze individual profiles, predict outcomes, or group subjects into buckets (e.g., Classification, Regression, or K-Means Clustering).
  2) Discover hidden network connections between these subjects to build/infer a geometric network graph (e.g., connecting similar patients via a web of edges).
  ```
  - If **Option 1** → Proceed to **Step 2 (Tabular Branch)**.
  - If **Option 2** → Trigger the **Clustering Circuit Breaker**:
    ```
    Just to double-check: If you want to group similar rows together into buckets (like customer segmentation), that belongs in Option 1. Option 2 means your downstream model relies on an explicit network topology of lines/edges connecting your rows. Are you building a true network graph?
    1) No, I am just doing standard grouping/clustering. -> [Reroute to Step 2: Tabular Branch]
    2) Yes, I am explicitly inferring a network topology. -> [Set dataset_type: graph_homogeneous, graph_mode: node_list, then skip to Step 4]
    ```

---

### Downstream Graph Scoping Checks

#### Multi-File Graph Check
- Ask: *Is this a homogeneous graph learnable from tabular data, or another graph type?*
- If **homogeneous** → Proceed with the tabular questionnaire flow and record `dataset_type: graph_homogeneous` with `graph_type: homogeneous`.
- If **other/heterogeneous** → Stop execution with a clear error message that non-homogeneous multi-file graph types are out of scope for this version.

#### Edge List Homogeneity Check
- **System Presentation:** "Got it. This looks like an Edge List graph structure. Are the interacting subjects of the same semantic type or different types?"


   1. Same type (e.g., User to User, Document to Document).
   2. Different types (e.g., User to Product, Transaction to Bank Account). [2] 

- If **Option 1 (Same type)** → Record `dataset_type: graph_homogeneous` with `graph_mode: edge_list` and `graph_type: homogeneous`. Then skip to Step 4.
- If **Option 2 (Different types)** → Stop execution with a clear error message that heterogeneous edge list graphs are out of scope for this version.

---

## Step 2: Tabular Branch (Subject Identification)

1. **Subject identification**
 - **System Presentation:** 
   ```
   Let's identify the primary "Subject" of your dataset.

   In a tabular dataset, the subject is the main "Actor" or entity you are evaluating or predicting an outcome for.
   * It is always a noun/entity (e.g., customer, device, employee, website).
   * It is NOT the action or event it performs (e.g., purchase, login, click, alert).

   What is the single primary subject you are tracking in this file? (e.g., customer, server, student):
   ```
 - Store text input in `subject`.

---

## Step 3: Structural & Temporal Diagnostic (Taxonomy Discovery)

Directly following subject naming, the CLI executes the structural diagnostic step to dynamically infer if the layout is `cross-sectional`, `event_log`, or `panel`.

- **System Presentation:**

Subject set to '{subject}'. Let's confirm your data layout.
Look at your raw file and check how your '{subject}_id' values appear:

   1. My '{subject}_id' appears EXACTLY ONCE per row in the entire file. All columns capture details from the exact same snapshot in time for everyone.
   → This is Cross-Sectional Data.
   2. My '{subject}_id' appears MULTIPLE TIMES because each row is an irregular action, click, or transaction that happened at a specific timestamp.
   → This is an Event Log.
   3. My '{subject}_id' appears MULTIPLE TIMES because I am tracking the exact same attributes at regular, repeated intervals over time (e.g., every month, every year).
   → This is Panel / Longitudinal Data.


- **Routing Logic & Metadata Assignment:**
- If **Option 1** → Set `dataset_type: cross-sectional`
- If **Option 2** → Set `dataset_type: event_log`
- If **Option 3** → Set `dataset_type: panel`

---

## Step 4: Optional use-case metadata
- The CLI captures `use_case` and `analysis_objective` unless `--skip-use-case-answers` is used.
- These answers are stored under `use_case_answers`.

---

## Step 5: Wide-short homogeneous dataset support
- After the dataset has been classified as tabular, the CLI auto-detects wide-and-short structure from the raw table shape.
- The default heuristic is conservative: if the table has at least 6 columns and the number of rows is at or below half the number of columns, it is treated as wide-short.
- The inferred representative column is chosen from non-ID-like columns so primary keys such as `customer_id` or `id` are not used as the anchor field.
- If `--wide-short-homogeneous` or `--no-wide-short-homogeneous` is provided, that explicit flag overrides the auto-detection result.
- If the dataset is classified as wide-short, the CLI prompts for `wide_short_representative_column` only when a usable representative column cannot be inferred automatically.
- The bootstrapped metadata records both `wide_short_homogeneous` and `wide_short_representative_column`.

---

## Step 6: Output
- Writes `bootstrap_metadata.yaml` in the target workspace.
- Supports `--json` to emit captured metadata as JSON to stdout.

---

## Supported CLI options
- `--wide-short-homogeneous` / `--no-wide-short-homogeneous`
- `--wide-short-representative-column`
- `--graph-mode node_list|edge_list|tabular`
- `--graph-homogeneous`
- `--dataset-type cross-sectional|panel|event_log|longitudinal|graph_homogeneous`
- `--subject`
- `--subject-id-attribute`
- `--use-case`
- `--analysis-objective`
- `--skip-use-case-answers`
- `--json`

---

## Bootstrapped metadata fields
The generated `bootstrap_metadata.yaml` includes:

- `dataset_type` (`cross-sectional`, `panel`, `event_log`, `graph_homogeneous`)
- `graph_mode` (`node_list`, `edge_list`, `tabular`)
- `subject`
- `subject_id_attribute`
- `wide_short_homogeneous` (boolean)
- `wide_short_representative_column`
- `use_case_answers` (object)
- `notes: Generated by dataset bootstrapping.`
- `graph_type: homogeneous` (when `dataset_type` is `graph_homogeneous`)

---

## Integration with config generation
- After `dataset-bootstrap`, run `bootstrap-config --output config.yaml .`.
- `bootstrap-config` consumes `bootstrap_metadata.yaml`, discovers the selected `data/` and `data_dictionary/` files, and writes `config.yaml`.
- For `cross-sectional` paths, the system sets up standard individual flattening pipelines.
- For `event_log` and `panel` selections, the system unlocks chronological group-by sorting windows pinned precisely to the validated `{subject}_id`.

---

## Acceptance Criteria
- `dataset-bootstrap` validates workspace layout constraints.
- Multi-file workspace layouts are dynamically parsed to identify and filter out version backups or scratchpads.
- Misconfigured tabular clustering intentions are safely intercepted and routed back to standard tabular paths.
- Tabular subject isolation strictly enforces an individual entity focus without causing menu or category bloat.
- Final configuration taxonomy (`cross-sectional` vs `event_log` vs `panel`) maps explicitly to the user's observational verification of `subject_id` density and regularity.

---

## Value Added
- Eradicates "workspace clutter" crashes by giving users a native tool to prune backup datasets and dictionaries mid-flight.
- Eliminates user data science terminology guesswork by substituting theoretical classification requests with visual layout matchers.
- Secures early downstream processing safety for automated feature engineering engines by locking down strict semantic constraints around the primary tabular indexing entity.

------------------------------
## Next Action Step
With the architectural spec fully finalized and protected against messy workspaces, where would you like to take this next? We can:

   1. Write the core CLI presentation logic in Python to render these exact multi-choice menus.
   2. Build the structural Pydantic configuration layer to handle saving and loading bootstrap_metadata.yaml.
   3. Outline the logic for automatically extracting potential --subject-id-attribute values from the validated data file headers.

Let me know what you would like to map out!

[1] [https://www.thedataschool.co.uk](https://www.thedataschool.co.uk/james-driver/tableau-prep-wildcard-unions/)
[2] [https://github.com](https://github.com/dotnet/sdk/issues/1543)
ation using arrow keys (↑, ↓) or numerical shortcuts (1, 2, 3). Selected items are highlighted with a cyan indicator (>).
* [Input] Text Component: Clear text input line with an explicit gray placeholder or example syntax.
* [Confirm] Toggle Component: Simple [Y/n] verification.
* [Status] Info/Error Badges:
* [INFO] Bold Blue: General setup state changes.
   * [SUCCESS] Bold Green: Successful routing confirmation or file write blocks.
   * [ABORT] Bold Red: Scope exclusions or structural errors resulting in terminal exit.

------------------------------
## 3. Step-by-Step Interactive Layout & Logic Flows## Step 0: Workspace Verification & File Clean-Up
Logic: Scan local data/ and data_dictionary/ directories. Resolve layout ambiguity through interactive target mapping before starting metadata inference.
## 0.1 Data Target Resolution

* Condition: If data/ contains exactly 1 CSV/Parquet file, automatically select it and print:

[INFO] Automatically selected primary data file: data/customer_churn.csv

* Condition: If data/ contains >1 files, prompt with a [Select] menu:

? I see multiple files in your 'data/' directory. How should these be treated?
> 1) Connected components: They are all related parts of a single network/relational dataset.
  2) Independent/Redundant: They are separate copies or backups. Only ONE specific file matters.

* Selection 1: Cache all files as input paths. Set workspace_layout = "multi_file". Proceed to Step 1: Branch A.
   * Selection 2: Trigger secondary [Select] list component using scanned filenames:
   
   ? Please select the single data file you want to use for this analysis:
   > data/active_users_2026.csv
     data/old_backup_2025.csv
     data/test_scratchpad.csv
   
   Cache chosen file path, ignore remaining files, set workspace_layout = "single_file", and route to Step 1: Branch B.

## 0.2 Data Dictionary Target Resolution

* Condition: If data_dictionary/ contains >1 files, present an immediate [Select] resolution layout:

? I see multiple files in your 'data_dictionary/' directory. Please select the correct active schema:
> data_dictionary/schema_v2.csv
  data_dictionary/schema_old.csv

Cache selected path as the unified metadata baseline; ignore others.

------------------------------
## Step 1: Structural & Intent Inference (Graph vs. Tabular)## Branch A: Multi-File Graph Flow

* Trigger: Triggered when workspace_layout == "multi_file".
* Terminal Presentation:
Applying this file-selection filter to the data_dictionary/ folder rounds out the workspace verification. It ensures that any backup dictionaries, scratchpad text files, or outdated sheets do not corrupt downstream schema parsing.
By unifying this layout validation into Step 0: Workspace Verification, the CLI establishes a clean "Source of Truth" (exactly one data file and exactly one data dictionary file) before Step 1 even runs.
------------------------------
## Revised Step 0 & Step 1 Logic with Workspace Cleanup
Here is how the combined verification and selection flows look programmatically:
## Step 0: Workspace verification

* The utility checks that the target directory is an initialized workspace containing data/ and data_dictionary/ folders.
* It scans both directories, logs the file counts, and prompts the user to resolve ambiguity if redundant or backup files are found.

## Data Directory Resolution

* If Multiple files found in data/:

I see multiple files in your 'data/' directory. How should these be treated?
1) Connected components: They are all related parts of a single network/relational dataset.
2) Independent/Redundant: They are separate copies or backups. Only ONE specific file matters.

* If Option 1 (Connected) → Cache all files for the Multi-File Graph Check in Step 1.
   * If Option 2 (Independent) → Display a selective menu of the CSV files, prompt the user to pick the active file, ignore the others, and tag this execution path for the Single Data File Flow in Step 1. [1] 

## Data Dictionary Resolution

* If Multiple files found in data_dictionary/:

I see multiple schema files in your 'data_dictionary/' directory. Only one active metadata mapping can be used. Please select the correct file for this configuration:
[Display all discovered files in data_dictionary/...]

* Cache the selected file path as the absolute source of truth for downstream bootstrap-config executions.

------------------------------
## Complete Redrafted Specification Document
Here is the final, hardened specification integrating both folder gatekeepers.

# Dataset Bootstrapping Specification## PurposeIntroduce a dedicated bootstrapping phase in `dd-parser-cleaner` to capture dataset metadata before config generation. This ensures the parser, cleaner, and notebook metadata flows receive the correct dataset taxonomy and subject-level signals. It replaces manual dataset-type assignment with an interactive inference flow that isolates tabular layouts, structural edge lists, and node-list graph learning tasks while automatically resolving messy or redundant workspace directories.
---## Bootstrapping Flow### Step 0: Workspace Verification & File Clean-UpThe utility checks that the target directory is an initialized workspace containing `data/` and `data_dictionary/` folders. It safely filters out redundant, old, or backup files using explicit user confirmation.
#### 1. Data File Target Resolution- The utility scans the `data/` folder for files.- **If a single file is found:** Cache it as the target dataset and route to **Branch B (Single Data File Flow)**.- **If multiple files are found:** Prompt the user to establish their analytical relationship:

I see multiple files in your 'data/' directory. How should these be treated?

   1. Connected components: They are all related parts of a single network/relational dataset.
   2. Independent/Redundant: They are separate copies or backups. Only ONE specific file matters.

- **If Option 1 (Connected):** Cache all files and route to **Branch A (Multiple Data Files Flow)**.
- **If Option 2 (Independent):** Present a selection menu:
  ```
  Please select the single data file you want to use for this analysis:
  [List detected data files...]
  ```
  Cache the chosen file, ignore the remaining files, and route to **Branch B (Single Data File Flow)**.

#### 2. Data Dictionary Target Resolution
- The utility scans the `data_dictionary/` folder for files.
- **If a single file is found:** Cache it as the absolute metadata schema file.
- **If multiple files are found:** Present an immediate resolution prompt:

I see multiple files in your 'data_dictionary/' directory. Only one active metadata schema can be used. Please select the correct file for this configuration:
[List detected dictionary files...]

Cache the selected file and completely ignore the redundant copies.

---

### Step 1: Structural & Intent Inference (Graph vs. Tabular)
Using the clean file targets established in Step 0, the CLI dynamically branches.

#### Branch A: Multiple Data Files Flow
- **System Presentation:** "Based on your input, your use case spans multiple distinct subjects (e.g., Users, Products, Logs) interacting with each other."
- **Action:** Proceed directly to the **Multi-File Graph Check**.

#### Branch B: Single Data File Flow
- **System Presentation:** The CLI prompts the user to define the semantic layout of the rows within the selected file:

In your data file, does a single row represent a static profile/event of ONE subject, or does it represent an interaction between TWO OR MORE subjects?

   1. One subject (e.g., a customer profile, a single sensor log line).
   2. An interaction, link, or transaction between subjects (e.g., User A followed User B, IP X pinged IP Y).

- **Routing:**
- If **Option 2 (Interaction)** → Proceed to **Edge List Homogeneity Check**.
- If **Option 1 (One Subject)** → Trigger the **Intent Check** to catch Node-List graph learning and isolate standard clustering:
  ```
  Structurally, this is a single file with one row per subject. What is your primary analysis goal?
  1) Analyze individual profiles, predict outcomes, or group subjects into buckets (e.g., Classification, Regression, or K-Means Clustering).
  2) Discover hidden network connections between these subjects to build/infer a geometric network graph (e.g., connecting similar patients via a web of edges).
  ```
  - If **Option 1** → Proceed to **Step 2 (Tabular Branch)**.
  - If **Option 2** → Trigger the **Clustering Circuit Breaker**:
    ```
    Just to double-check: If you want to group similar rows together into buckets (like customer segmentation), that belongs in Option 1. Option 2 means your downstream model relies on an explicit network topology of lines/edges connecting your rows. Are you building a true network graph?
    1) No, I am just doing standard grouping/clustering. -> [Reroute to Step 2: Tabular Branch]
    2) Yes, I am explicitly inferring a network topology. -> [Set dataset_type: graph_homogeneous, graph_mode: node_list, then skip to Step 4]
    ```

---

### Downstream Graph Scoping Checks

#### Multi-File Graph Check
- Ask: *Is this a homogeneous graph learnable from tabular data, or another graph type?*
- If **homogeneous** → Proceed with the tabular questionnaire flow and record `dataset_type: graph_homogeneous` with `graph_type: homogeneous`.
- If **other/heterogeneous** → Stop execution with a clear error message that non-homogeneous multi-file graph types are out of scope for this version.

#### Edge List Homogeneity Check
- **System Presentation:** "Got it. This looks like an Edge List graph structure. Are the interacting subjects of the same semantic type or different types?"


   1. Same type (e.g., User to User, Document to Document).
   2. Different types (e.g., User to Product, Transaction to Bank Account). [2] 

- If **Option 1 (Same type)** → Record `dataset_type: graph_homogeneous` with `graph_mode: edge_list` and `graph_type: homogeneous`. Then skip to Step 4.
- If **Option 2 (Different types)** → Stop execution with a clear error message that heterogeneous edge list graphs are out of scope for this version.

---

## Step 2: Tabular Branch (Subject Identification)

1. **Subject identification**
 - **System Presentation:** 
   ```
   Let's identify the primary "Subject" of your dataset.

   In a tabular dataset, the subject is the main "Actor" or entity you are evaluating or predicting an outcome for.
   * It is always a noun/entity (e.g., customer, device, employee, website).
   * It is NOT the action or event it performs (e.g., purchase, login, click, alert).

   What is the single primary subject you are tracking in this file? (e.g., customer, server, student):
   ```
 - Store text input in `subject`.

---

## Step 3: Structural & Temporal Diagnostic (Taxonomy Discovery)

Directly following subject naming, the CLI executes the structural diagnostic step to dynamically infer if the layout is `cross-sectional`, `event_log`, or `panel`.

- **System Presentation:**

Subject set to '{subject}'. Let's confirm your data layout.
Look at your raw file and check how your '{subject}_id' values appear:

   1. My '{subject}_id' appears EXACTLY ONCE per row in the entire file. All columns capture details from the exact same snapshot in time for everyone.
   → This is Cross-Sectional Data.
   2. My '{subject}_id' appears MULTIPLE TIMES because each row is an irregular action, click, or transaction that happened at a specific timestamp.
   → This is an Event Log.
   3. My '{subject}_id' appears MULTIPLE TIMES because I am tracking the exact same attributes at regular, repeated intervals over time (e.g., every month, every year).
   → This is Panel / Longitudinal Data.


- **Routing Logic & Metadata Assignment:**
- If **Option 1** → Set `dataset_type: cross-sectional`
- If **Option 2** → Set `dataset_type: event_log`
- If **Option 3** → Set `dataset_type: panel`

---

## Step 4: Optional use-case metadata
- The CLI captures `use_case` and `analysis_objective` unless `--skip-use-case-answers` is used.
- These answers are stored under `use_case_answers`.

---

## Step 5: Wide-short homogeneous dataset support
- After the dataset has been classified as tabular, the CLI auto-detects wide-and-short structure from the raw table shape.
- The default heuristic is conservative: if the table has at least 6 columns and the number of rows is at or below half the number of columns, it is treated as wide-short.
- The inferred representative column is chosen from non-ID-like columns so primary keys such as `customer_id` or `id` are not used as the anchor field.
- If `--wide-short-homogeneous` or `--no-wide-short-homogeneous` is provided, that explicit flag overrides the auto-detection result.
- If the dataset is classified as wide-short, the CLI prompts for `wide_short_representative_column` only when a usable representative column cannot be inferred automatically.
- The bootstrapped metadata records both `wide_short_homogeneous` and `wide_short_representative_column`.

---

## Step 6: Output
- Writes `bootstrap_metadata.yaml` in the target workspace.
- Supports `--json` to emit captured metadata as JSON to stdout.

---

## Supported CLI options
- `--wide-short-homogeneous` / `--no-wide-short-homogeneous`
- `--wide-short-representative-column`
- `--graph-mode node_list|edge_list|tabular`
- `--graph-homogeneous`
- `--dataset-type cross-sectional|panel|event_log|longitudinal|graph_homogeneous`
- `--subject`
- `--subject-id-attribute`
- `--use-case`
- `--analysis-objective`
- `--skip-use-case-answers`
- `--json`

---

## Bootstrapped metadata fields
The generated `bootstrap_metadata.yaml` includes:

- `dataset_type` (`cross-sectional`, `panel`, `event_log`, `graph_homogeneous`)
- `graph_mode` (`node_list`, `edge_list`, `tabular`)
- `subject`
- `subject_id_attribute`
- `wide_short_homogeneous` (boolean)
- `wide_short_representative_column`
- `use_case_answers` (object)
- `notes: Generated by dataset bootstrapping.`
- `graph_type: homogeneous` (when `dataset_type` is `graph_homogeneous`)

---

## Integration with config generation
- After `dataset-bootstrap`, run `bootstrap-config --output config.yaml .`.
- `bootstrap-config` consumes `bootstrap_metadata.yaml`, discovers the selected `data/` and `data_dictionary/` files, and writes `config.yaml`.
- For `cross-sectional` paths, the system sets up standard individual flattening pipelines.
- For `event_log` and `panel` selections, the system unlocks chronological group-by sorting windows pinned precisely to the validated `{subject}_id`.

---

## Acceptance Criteria
- `dataset-bootstrap` validates workspace layout constraints.
- Multi-file workspace layouts are dynamically parsed to identify and filter out version backups or scratchpads.
- Misconfigured tabular clustering intentions are safely intercepted and routed back to standard tabular paths.
- Tabular subject isolation strictly enforces an individual entity focus without causing menu or category bloat.
- Final configuration taxonomy (`cross-sectional` vs `event_log` vs `panel`) maps explicitly to the user's observational verification of `subject_id` density and regularity.

---

## Value Added
- Eradicates "workspace clutter" crashes by giving users a native tool to prune backup datasets and dictionaries mid-flight.
- Eliminates user data science terminology guesswork by substituting theoretical classification requests with visual layout matchers.
- Secures early downstream processing safety for automated feature engineering engines by locking down strict semantic constraints around the primary tabular indexing entity.

------------------------------
## Next Action Step
With the architectural spec fully finalized and protected against messy workspaces, where would you like to take this next? We can:

   1. Write the core CLI presentation logic in Python to render these exact multi-choice menus.
   2. Build the structural Pydantic configuration layer to handle saving and loading bootstrap_metadata.yaml.
   3. Outline the logic for automatically extracting potential --subject-id-attribute values from the validated data file headers.

Let me know what you would like to map out!

[1] [https://www.thedataschool.co.uk](https://www.thedataschool.co.uk/james-driver/tableau-prep-wildcard-unions/)
[2] [https://github.com](https://github.com/dotnet/sdk/issues/1543)

[INFO] Multi-file input layout detected. This layout implies your use case spans multiple distinct subjects interacting with each other.

? Is this a homogeneous graph learnable from flat files, or another graph structure?
> 1) Homogeneous Graph (All tables map node features/edges for one primary entity type)
  2) Other / Heterogeneous Graph (Complex multi-entity relational webs, bipartite networks)

* Selection 1: Record dataset_type: graph_homogeneous with graph_type: homogeneous. Skip directly to Step 4.
   * Selection 2: Print [ABORT] layout and exit process:
   
   [ABORT] Heterogeneous and multi-entity relational graphs are currently out of scope for this version of dd-parser-cleaner. Exiting safely.
   
   
## Branch B: Single Data File Flow

* Trigger: Triggered when workspace_layout == "single_file".
* Terminal Presentation ([Select] Layout):

? In your data file, does a single row represent a profile/event of ONE subject, or does it represent an interaction between TWO OR MORE subjects?
> 1) One subject (e.g., a customer profile snapshot, a single sensor log line).
  2) An interaction, link, or transaction between subjects (e.g., User A followed User B, IP X pinged IP Y).

* Selection 2 (Interaction): Route to Edge List Homogeneity Check:
   
   ? [INFO] This structure maps an Edge List. Are the interacting subjects of the same type?
   > 1) Same type (e.g., User to User, Document to Document).
     2) Different types (e.g., User to Product, Transaction to Bank Account).
   
   * Option 1: Record dataset_type: graph_homogeneous, graph_mode: edge_list, graph_type: homogeneous. Skip to Step 4.
      * Option 2: Abort process: [ABORT] Heterogeneous edge lists are out of scope. Exiting.
   * Selection 1 (One Subject): Trigger Intent Check to isolate graph learning from tabular clustering:
   
   ? Structurally, this is a single file with one row per subject. What is your primary analysis goal?
   > 1) Analyze individual profiles, predict outcomes, or group subjects into buckets (e.g., Classification, Regression, or K-Means Clustering).
     2) Discover hidden network connections between these subjects to build/infer a geometric network graph (e.g., connecting similar patients via a web of edges).
   
   * Selection 2 (Graph Inference Target): Launch the Clustering Circuit Breaker:
      
      ? [WARNING] Just to double-check: If you want to group similar rows together into buckets (like customer segmentation), that belongs in Option 1. Option 2 means your downstream model relies on an explicit network topology of lines/edges connecting your rows. Are you building a true network graph?
      > 1) No, I am just doing standard grouping/clustering.
        2) Yes, I am explicitly inferring a network topology.
      
      * Option 1: Reroute to Step 2 (Tabular Branch).
         * Option 2: Record dataset_type: graph_homogeneous, graph_mode: node_list. Skip to Step 4.
      * Selection 1 (Tabular Target): Route directly to Step 2 (Tabular Branch).
   
------------------------------
## Step 2: Tabular Branch (Subject Identification)

* Terminal Presentation ([Input] Layout):

Let's identify the primary "Subject" of your dataset.

In a tabular dataset, the subject is the main "Actor" or entity you are evaluating or predicting an outcome for.
* It is always a noun/entity (e.g., customer, device, employee, website).
* It is NOT the action or event it performs (e.g., purchase, login, click, alert).

? What is the single primary subject you are tracking in this file? (e.g., customer, server, student):
>> 

* Validation Rule: Require a non-empty string. Convert to lowercase, strip trailing whitespace, and cache in variable {subject}.

------------------------------
## Step 3: Structural & Temporal Diagnostic (Taxonomy Discovery)

* Terminal Presentation ([Select] Layout):

[SUCCESS] Subject set to '{subject}'. Let's confirm your data layout.
Look at your raw file and check how your '{subject}_id' values appear:

> 1) My '{subject}_id' appears EXACTLY ONCE per row in the entire file. All columns capture details from the exact same snapshot in time for everyone.
     → This is Cross-Sectional Data.
  2) My '{subject}_id' appears MULTIPLE TIMES because each row is an irregular action, click, or transaction that happened at a specific timestamp.
     → This is an Event Log.
  3) My '{subject}_id' appears MULTIPLE TIMES because I am tracking the exact same attributes at regular, repeated intervals over time (e.g., every month, every year).
     → This is Panel / Longitudinal Data.

* Routing Logic & Metadata Assignment:
* Selection 1: Record dataset_type: cross-sectional
   * Selection 2: Record dataset_type: event_log
   * Selection 3: Record dataset_type: panel

------------------------------
## Step 4: Optional Use-Case Metadata

* Terminal Presentation ([Input] Layout):
* Skip Option Check: If execution includes the command line flag --skip-use-case-answers, skip these inputs entirely.

? Enter the primary business use case name (Optional, press Enter to skip):
>> 

? Enter the primary analysis objective (Optional, press Enter to skip):
>> 

* Storage Configuration: Map non-empty inputs to the use_case_answers object metadata.

------------------------------
## Step 5: Wide-Short Homogeneous Dataset Support

* Auto-detection is performed only after the dataset has been classified as tabular.
* Default heuristic: if the table has at least 6 columns and the row count is at or below half the column count, it is treated as wide-short.
* Representative column selection prefers a non-ID-like column; primary keys such as `customer_id` or `id` are not used as the wide-short anchor unless the user explicitly overrides the value.
* Explicit CLI overrides win: `--wide-short-homogeneous` or `--no-wide-short-homogeneous` takes precedence over auto-detection.
* If a usable representative column cannot be inferred automatically, the CLI asks for it and validates it against the file headers before saving it to `wide_short_representative_column`.
* The output metadata records both `wide_short_homogeneous` and `wide_short_representative_column`.
   
------------------------------
## Step 6: Output Emission

* Layout Check: If --json flag was included in the runtime CLI trigger, format the metadata fields into standard JSON and print to stdout instead of creating file assets.
* Standard Layout File Generation:
Write a structured bootstrap_metadata.yaml serialization block into the active workspace directory. Print final completion message:

[SUCCESS] Dataset bootstrapping complete! Written: ./bootstrap_metadata.yaml
[INFO] You can now proceed to run configuration generation using:
       bootstrap-config --output config.yaml .


------------------------------
## 4. Metadata Mapping Rules for Implementation
The implementation must populate the following metadata schemas based on the user choices above:

| Field Name | Expected Data Type | Permitted Value Options | Source Component Step |
|---|---|---|---|
| dataset_type | String | cross-sectional, panel, event_log, graph_homogeneous | Step 1 / Step 3 |
| graph_mode | String | node_list, edge_list, tabular | Step 1 |
| graph_type | String | homogeneous (Omitted if dataset is tabular) | Downstream Graph Check |
| subject | String | User custom input string text | Step 2 |
| subject_id_attribute | String | Auto-matched or fallback input column tracking | Step 2 / Post-bootstrap matching |
| wide_short_homogeneous | Boolean | true, false | Step 5 |
| wide_short_representative_column | String | User-provided validated header name string | Step 5 |
| use_case_answers | Object / Dict | {"use_case": "...", "analysis_objective": "..."} | Step 4 |

------------------------------
## 5. Downstream Integration Hooks

* Config Generation Interaction: The engine feeding off bootstrap_metadata.yaml via bootstrap-config --output config.yaml . reads the layout context.
* If dataset_type == "cross-sectional", it configures static rows without window tracking.
* If dataset_type is either "event_log" or "panel", it automatically establishes temporal ordering loops and time-series feature window rules mapped directly to the extracted {subject}_id tracker.

------------------------------
## Verification Checklist for VS Code Implementation Planning

   1. Ensure the app flags can intercept prompts natively (--skip-use-case-answers, --json, etc.).
   2. Confirm the directory index engine correctly processes file arrays when data/ houses redundant log configurations, dropping elements accurately into Step 0.1 Selection 2.
   3. Verify the Clustering Circuit Breaker cleanly reroutes selection data streams to the standard tabular logic loop.


