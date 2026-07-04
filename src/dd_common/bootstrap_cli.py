import argparse
import sys
import yaml
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from dd_common.utilities import verify_workspace_status
from dd_common.llm_prompts import PROMPT_TEMPLATES

BOOTSTRAP_METADATA_FILENAME = "bootstrap_metadata.yaml"


def load_bootstrap_metadata(target_path: Path) -> dict:
    metadata_path = target_path / BOOTSTRAP_METADATA_FILENAME
    if not metadata_path.exists():
        return {}

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

console = Console()

def select_csv(directory: Path, type_label: str, target_path: Path) -> str:
    """Finds CSVs and prompts user for selection if multiple exist."""
    csv_files = list(directory.glob("*.csv"))
    
    if type_label == "Data Dictionary":
        # Filter candidates by reading first 3 rows
        candidates = []
        for f in csv_files:
            try:
                df = pd.read_csv(f, nrows=3)
                if len(df.columns) > 1:
                    candidates.append(f)
                else:
                    console.print(f"[dim]ℹ️  Skipping {f.name}: Data Dictionary must have at least 2 columns.[/dim]")
            except Exception:
                console.print(f"[dim]ℹ️  Skipping {f.name}: File is empty or not a valid CSV.[/dim]")
        csv_files = candidates

    if not csv_files:
        console.print(f"[bold red]❌ Error:[/bold red] No valid {type_label} CSV files found in [cyan]{directory.relative_to(target_path)}[/cyan].")
        return None

    if len(csv_files) == 1:
        return csv_files[0].name

    console.print(f"\n[bold yellow]Multiple {type_label} candidates found:[/bold yellow]")
    for idx, f in enumerate(csv_files):
        console.print(f" [{idx}] {f.name}")
    
    while True:
        try:
            choice = int(console.input(f"Select the correct {type_label} file (0-{len(csv_files)-1}): "))
            if 0 <= choice < len(csv_files):
                return csv_files[choice].name
        except ValueError:
            pass
        console.print("[red]Invalid selection. Please enter a number.[/red]")

def main():
    parser = argparse.ArgumentParser(description="Bootstrap a KMDS config.yaml by discovering project assets.")
    parser.add_argument(
        "working_dir",
        nargs="?",
        help="The working directory to bootstrap. If omitted, you will be prompted."
    )
    parser.add_argument(
        "--dataset-type",
        choices=["cross-sectional", "panel", "longitudinal"],
        help="Optional dataset structural type for the generated config. If omitted, the utility will prompt."
    )
    parser.add_argument(
        "--enable-questionnaire",
        action="store_true",
        help="Enable dataset questionnaire support in the generated config."
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive questionnaire mode in the generated config."
    )
    parser.add_argument(
        "--require-questions",
        action="store_true",
        help="Require questionnaire answers before proceeding when generating the config."
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file name for the generated config (default: provisional_config.yaml)."
    )
    args = parser.parse_args()

    working_dir = args.working_dir
    if not working_dir:
        working_dir = console.input("[bold blue]Enter the working directory path to bootstrap [default: .]: [/bold blue]").strip() or "."

    target_path = Path(working_dir).resolve()

    # 1. Verify Workspace
    if not verify_workspace_status(target_path):
        console.print(f"[bold red]❌ Error:[/bold red] '{target_path}' is not an initialized workspace.")
        console.print("👉 Run [white]init-workspace[/white] first.")
        sys.exit(1)

    # 2. Check for required assets
    data_dir = target_path / "data"
    dd_dir = target_path / "data_dictionary"
    doc_dir = target_path / "documents"

    raw_file = select_csv(data_dir, "Raw Data", target_path)
    dd_file = select_csv(dd_dir, "Data Dictionary", target_path)

    if not raw_file or not dd_file:
        console.print("\n[bold red]Stopping:[/bold red] Required files are missing. Please populate the directories and run this utility again.")
        sys.exit(1)

    # 3. Check Documents
    if not any(doc_dir.iterdir()):
        console.print(Panel(
            "[bold yellow]⚠️ Warning:[/bold yellow] The [cyan]documents/[/cyan] directory is empty.\n\n"
            "Operating with an empty documents folder is a suboptimal idea. "
            "Providing a use-case narrative or SOP in this directory is highly recommended "
            "to help the AI extract relevant thresholds and business logic. Without these, results are usually sub-optimal.",
            title="Sub-optimal Workspace State"
        ))

    # 4. Prompt for Attribute Column Name
    # Peek at the DD to help the user
    df_peek = pd.read_csv(dd_dir / dd_file, nrows=0)
    cols = df_peek.columns.tolist()
    console.print(f"\n[bold green]Detected columns in {dd_file}:[/bold green] {cols}")
    attr_col = console.input("[bold white]Enter the name of the 'Attribute' column (e.g., 'Field Name'): [/bold white]").strip()
    if not attr_col:
        attr_col = "Field Name"
        console.print(f"Using default: [cyan]{attr_col}[/cyan]")

    dataset_id = Path(raw_file).stem if raw_file else Path(dd_file).stem

    bootstrap_metadata = load_bootstrap_metadata(target_path)

    dataset_type = args.dataset_type
    if not dataset_type and bootstrap_metadata.get("dataset_type"):
        dataset_type = bootstrap_metadata["dataset_type"]
        console.print(f"[bold green]Using bootstrapped dataset_type:[/bold green] {dataset_type}")

    if not dataset_type:
        dataset_type = console.input(
            "[bold white]Enter the dataset type [cross-sectional/panel/longitudinal] (default: cross-sectional): [/bold white]"
        ).strip().lower()
        if dataset_type not in {"cross-sectional", "panel", "longitudinal"}:
            dataset_type = "cross-sectional"

    subject_id_attribute = bootstrap_metadata.get("subject_id_attribute")
    if not subject_id_attribute and dataset_type in {"panel", "event_log", "longitudinal"}:
        if dataset_type == "panel":
            event_log_answer = console.input(
                "[bold white]Is this dataset an event log (multiple records per subject)? [y/N]: [/bold white]"
            ).strip().lower()
            if event_log_answer in {"y", "yes"}:
                dataset_type = "event_log"
            else:
                console.print(
                    "[bold green]Treating as a standard panel dataset with static attributes.[/bold green]"
                )

        if dataset_type == "event_log":
            subject_id_attribute = console.input(
                "[bold white]Enter the subject id attribute name: [/bold white]"
            ).strip()
            if not subject_id_attribute:
                console.print(
                    "[bold yellow]Warning: No subject id attribute provided. "
                    "Event log static/dynamic inference will be incomplete.[/bold yellow]"
                )

    enable_dataset_questionnaire = args.enable_questionnaire
    interactive_mode = args.interactive
    handshake_require_questions = args.require_questions

    if dataset_type in {"panel", "event_log", "longitudinal"}:
        if not args.enable_questionnaire:
            enable_dataset_questionnaire = True
        if not args.interactive:
            interactive_mode = True
        if not args.require_questions:
            handshake_require_questions = True

    output_filename = args.output or "provisional_config.yaml"
    output_file = target_path / output_filename

    # 5. Build Provisional Config
    config = {
        "working_dir": str(target_path),
        "batch_size": 5,
        "model_name": "llama3.2",
        "llm_timeout": 180.0,
        "documents_dir": "documents",
        "system_prompt": "You are a precise data engineering assistant. Respond strictly in JSON.",
        "temperature": 0.0,
        "dataset_type": dataset_type,
        "dataset_id": dataset_id,
        "require_manifest_before_featurize": True,
        "enable_dataset_questionnaire": enable_dataset_questionnaire,
        "interactive_mode": interactive_mode,
        "questionnaire_schema_path": "documents/config/dataset_questions.json",
        "handshake_require_questions": handshake_require_questions,
        "parser": {
            "data_dictionary_file": dd_file,
            "data_dictionary_attribute_col_name": attr_col,
            "csv_target_column_index": 0,
            "dd_parser_output_dir": "dd_analysis_results",
            "output_filename": f"{dataset_id}_analysis_results.csv",
            "dataset_manifest_filename": f"{dataset_id}_dataset_manifest.json",
            "attribute_manifest_filename": f"{dataset_id}_attribute_manifest.json",
            "entity_tagging": [],
            "prompts": PROMPT_TEMPLATES["parser"]["prompts"]
        },
        "cleaner": {
            "raw_dataset_file": raw_file,
            "clean_output_filename": f"{dataset_id}_clean.csv",
            "metadata_table_filename": f"{dataset_id}_metadata_table.csv",
            "user_cleaned_output_filename": f"{dataset_id}_user_cleaned.csv",
            "dd_cleaner_output_dir": "dd_cleaner",
            "handshake_file": f"{dataset_id}_parser_cleaner_handshake.md",
            "profiling_report_filename": f"{dataset_id}_profiling_report.md",
            "quarantine_dir": "quarantine",
            "quarantine_filename": f"{dataset_id}_quarantine.csv",
            "pipeline": ["integrity", "profile", "assessment"],
            "structural_assessment": {
                "auto_drop_constant": False,
                "dataset_type": dataset_type,
                "subject_id_attribute": subject_id_attribute,
                "null_threshold": 0.95
            },
            "missing_values": {
                "prompts": PROMPT_TEMPLATES["cleaner"]["missing_values"]["prompts"]
            }
        }
    }

    # 6. Save
    with open(output_file, "w") as f:
        f.write("# 🤖 PROVISIONAL KMDS CONFIGURATION\n")
        f.write("# Generated by bootstrap-config utility.\n\n")
        yaml.safe_dump(config, f, sort_keys=False, default_flow_style=False)

    console.print(f"\n[bold green]✅ Success:[/bold green] [cyan]{output_file.name}[/cyan] has been created at {target_path}")
    console.print("🚀 You are now ready to run [white]classify-entities[/white].\n")

if __name__ == "__main__":
    main()