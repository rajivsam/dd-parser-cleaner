import argparse
import sys
import yaml
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.panel import Panel
from dd_common.utilities import verify_workspace_status
from dd_common.llm_prompts import PROMPT_TEMPLATES

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

    # 5. Build Provisional Config
    config = {
        "working_dir": str(target_path),
        "batch_size": 5,
        "model_name": "llama3.2",
        "llm_timeout": 180.0,
        "documents_dir": "documents",
        "system_prompt": "You are a precise data engineering assistant. Respond strictly in JSON.",
        "temperature": 0.0,
        "parser": {
            "data_dictionary_file": dd_file,
            "data_dictionary_attribute_col_name": attr_col,
            "csv_target_column_index": 0,
            "dd_parser_output_dir": "dd_analysis_results",
            "output_filename": f"{Path(raw_file).stem}_analysis_results.csv",
            "entity_tagging": ["geographic"],
            "prompts": PROMPT_TEMPLATES["parser"]["prompts"]
        },
        "cleaner": {
            "raw_dataset_file": raw_file,
            "clean_output_filename": f"{Path(raw_file).stem}_clean.csv",
            "metadata_table_filename": f"{Path(raw_file).stem}_metadata_table.csv",
            "user_cleaned_output_filename": f"{Path(raw_file).stem}_user_cleaned.csv",
            "dd_cleaner_output_dir": "dd_cleaner",
            "handshake_file": "parser_cleaner_handshake.md",
            "profiling_report_filename": f"{Path(raw_file).stem}_profiling_report.md",
            "quarantine_dir": "quarantine",
            "quarantine_filename": f"{Path(raw_file).stem}_quarantine.csv",
            "pipeline": ["integrity", "profile", "assessment"],
            "structural_assessment": {
                "auto_drop_constant": False,
                "dataset_type": "cross-sectional (inferred)",
                "null_threshold": 0.95
            },
            "missing_values": {
                "prompts": PROMPT_TEMPLATES["cleaner"]["missing_values"]["prompts"]
            }
        }
    }

    # 6. Save
    output_file = target_path / "provisional_config.yaml"
    with open(output_file, "w") as f:
        f.write("# 🤖 PROVISIONAL KMDS CONFIGURATION\n")
        f.write("# Generated by bootstrap-config utility.\n\n")
        yaml.safe_dump(config, f, sort_keys=False, default_flow_style=False)

    console.print(f"\n[bold green]✅ Success:[/bold green] [cyan]provisional_config.yaml[/cyan] has been created at {target_path}")
    console.print("🚀 You are now ready to run [white]classify-entities[/white].\n")

if __name__ == "__main__":
    main()