import argparse
import sys
import json
from pathlib import Path
from dd_common.utilities import verify_workspace_status

def main():
    """CLI entry point to guide users on file placement within the KMDS workspace."""
    parser = argparse.ArgumentParser(description="Guidance on where to place data and documents.")
    parser.add_argument(
        "working_dir", 
        nargs="?", 
        help="The working directory to inspect. If omitted, defaults to current directory."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the location guidance in JSON format for automation."
    )
    args = parser.parse_args()

    working_dir = args.working_dir or "."
    target_path = Path(working_dir).resolve()

    # 1. Pre-check: Verify workspace existence
    if not verify_workspace_status(target_path):
        print(f"❌ Error: The directory '{target_path}' is not an initialized workspace.")
        print("👉 Please run 'init-workspace' first to create the required KMDS structure.")
        sys.exit(1)

    if args.json:
        guidance = {
            "workspace_root": str(target_path),
            "recommendations": {
                "raw_data": {
                    "path": "./data/",
                    "config_key": "cleaner.raw_dataset_file"
                },
                "data_dictionary": {
                    "path": "./data_dictionary/",
                    "config_keys": ["parser.data_dictionary_file", "parser.data_dictionary_attribute_col_name"]
                },
                "narrative_documents": {
                    "path": "./documents/",
                    "config_key": "documents_dir"
                }
            }
        }
        print(json.dumps(guidance, indent=4))
        return

    # 2. Provide structural guidance (Dependency on config.yaml removed)
    print(f"\n📍 [KMDS Location Helper] for: {target_path}")
    print("-" * 60)
    
    print(f"\n📂 1. RAW DATA (CSV)")
    print(f"   Place your source data file in: ./data/")
    print(f"   💡 This is your primary operational table (e.g., 'raw_data.csv').")
    print(f"   Config key (future): cleaner.raw_dataset_file")

    print(f"\n📂 2. DATA DICTIONARY (CSV)")
    print(f"   Place your metadata schema in: ./data_dictionary/")
    print(f"   💡 Required Columns:")
    print(f"      - Attribute column (e.g., 'Field Name'): Maps to your data headers.")
    print(f"      - Description column: Provides semantic context for AI discovery.")
    print(f"   Config key (future): parser.data_dictionary_file")
    print(f"   Config key (future): parser.data_dictionary_attribute_col_name")

    print(f"\n📂 3. NARRATIVE DOCUMENTS (MD/PDF)")
    print(f"   Place domain SOPs, narratives, or requirements in: ./documents/")
    print(f"   💡 These files help the agent extract domain thresholds and logic.")
    print(f"   Config key (future): documents_dir")
    
    print("\n" + "-" * 60)
    print("✅ Once files are placed, the next utility will help you bootstrap your config.yaml.\n")

if __name__ == "__main__":
    main()