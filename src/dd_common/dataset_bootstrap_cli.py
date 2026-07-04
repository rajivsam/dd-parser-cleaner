import argparse
import sys
import yaml
import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from dd_common.utilities import verify_workspace_status

console = Console()

def select_csv(directory: Path, type_label: str, target_path: Path) -> str:
    """Finds CSVs and prompts the user for selection if multiple exist."""
    csv_files = list(directory.glob("*.csv"))
    if not csv_files:
        console.print(f"[bold red]❌ Error:[/bold red] No valid {type_label} CSV files found in [cyan]{directory.relative_to(target_path)}[/cyan].")
        return None

    if len(csv_files) == 1:
        return csv_files[0].name

    console.print(f"\n[bold yellow]Multiple {type_label} candidates found:[/bold yellow]")
    for idx, f in enumerate(csv_files):
        console.print(f" [{idx}] {f.name}")

    while True:
        choice = console.input(f"Select the correct {type_label} file (0-{len(csv_files)-1}): ")
        try:
            index = int(choice)
            if 0 <= index < len(csv_files):
                return csv_files[index].name
        except ValueError:
            pass
        console.print("[red]Invalid selection. Please enter a number.[/red]")


def ask_yes_no(prompt: str, default_no: bool = True) -> bool:
    answer = console.input(f"[bold white]{prompt} [/bold white]").strip().lower()
    if not answer:
        return not default_no
    return answer in {"y", "yes", "true", "1"}


def main():
    parser = argparse.ArgumentParser(description="Bootstrap dataset metadata before generating config.")
    parser.add_argument(
        "working_dir",
        nargs="?",
        help="The working directory to inspect. If omitted, defaults to current directory."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the captured metadata as JSON instead of saving it to disk."
    )
    args = parser.parse_args()

    working_dir = args.working_dir or "."
    target_path = Path(working_dir).resolve()

    if not verify_workspace_status(target_path):
        console.print(f"[bold red]❌ Error:[/bold red] The directory '{target_path}' is not an initialized workspace.")
        console.print("👉 Run 'init-workspace' first.")
        sys.exit(1)

    data_dir = target_path / "data"
    dd_dir = target_path / "data_dictionary"

    raw_file = select_csv(data_dir, "Raw Data", target_path)
    dd_file = select_csv(dd_dir, "Data Dictionary", target_path)

    if not raw_file or not dd_file:
        console.print("\n[bold red]Stopping:[/bold red] Required files are missing. Please populate the directories and run this utility again.")
        sys.exit(1)

    console.print(Panel(
        "[bold green]Dataset Bootstrapping[/bold green]\n\nThis step captures the dataset type and subject-level metadata before config generation.",
        title="Bootstrapping Phase"
    ))

    graph_mode = console.input("[bold white]Do you want to analyze a Graph or Tabular dataset? [Graph/Tabular]: [/bold white]").strip().lower()
    if graph_mode in {"graph", "g"}:
        console.print("[bold red]Graph datasets are not supported in this version.[/bold red]")
        sys.exit(1)

    dataset_type = None
    dataset_type_answer = console.input("[bold white]Is the dataset cross-sectional, panel, or are you unsure? [cross-sectional/panel/unsure]: [/bold white]").strip().lower()
    if dataset_type_answer in {"cross-sectional", "cross sectional", "cross_sectional", "cross"}:
        dataset_type = "cross-sectional"
    elif dataset_type_answer in {"panel", "longitudinal"}:
        dataset_type = "panel"
    else:
        subject = console.input("[bold white]What is the subject of the dataset? (e.g., customer, device, employee): [/bold white]").strip()
        subject = subject or ""
        row_time = ask_yes_no("Does each row represent the subject at a single point in time? [y/N]: ")
        if not row_time:
            dataset_type = "event_log"
        else:
            same_time = ask_yes_no("Are all subjects evaluated at the same point in time? [y/N]: ")
            dataset_type = "cross-sectional" if same_time else "panel"

    subject = locals().get("subject") or ""
    if not subject:
        subject = console.input("[bold white]What is the subject of the dataset? (e.g., customer, device, employee): [/bold white]").strip()

    subject_id_attribute = None
    if dataset_type == "event_log":
        subject_id_attribute = console.input("[bold white]Enter the subject id attribute name: [/bold white]").strip()

    use_case_answers = {}
    if ask_yes_no("Would you like to capture short use-case answers for this dataset? [y/N]: "):
        use_case_answers["use_case"] = console.input("[bold white]Describe the primary use case for this dataset: [/bold white]").strip()
        use_case_answers["analysis_objective"] = console.input("[bold white]What is the analysis objective? [/bold white]").strip()

    metadata = {
        "dataset_type": dataset_type,
        "subject": subject,
        "subject_id_attribute": subject_id_attribute,
        "use_case_answers": use_case_answers,
        "notes": "Generated by dataset bootstrapping."
    }

    output_path = target_path / "bootstrap_metadata.yaml"
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(metadata, f, sort_keys=False)

    console.print(f"\n[bold green]✅ Success:[/bold green] Bootstrapped metadata written to [cyan]{output_path}[/cyan]")
    if args.json:
        console.print_json(data=metadata)


if __name__ == "__main__":
    main()
