import argparse
import sys
import yaml
import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from dd_common.utilities import verify_workspace_status

console = Console()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap dataset metadata before generating config.")
    parser.add_argument(
        "working_dir",
        nargs="?",
        help="The working directory to inspect. If omitted, defaults to current directory."
    )
    parser.add_argument(
        "--wide-short-homogeneous",
        dest="wide_short_homogeneous",
        action="store_true",
        default=None,
        help="Mark the dataset as wide-and-short homogeneous."
    )
    parser.add_argument(
        "--no-wide-short-homogeneous",
        dest="wide_short_homogeneous",
        action="store_false",
        help="Explicitly mark the dataset as not wide-and-short homogeneous."
    )
    parser.add_argument(
        "--wide-short-representative-column",
        help="Representative column name for wide-short homogeneous datasets."
    )
    parser.add_argument(
        "--graph-mode",
        choices=["graph", "tabular"],
        help="Choose whether the dataset is a graph or tabular dataset."
    )
    parser.add_argument(
        "--graph-homogeneous",
        action="store_true",
        help="Mark the graph dataset as homogeneous and learnable from tabular data."
    )
    parser.add_argument(
        "--dataset-type",
        choices=["cross-sectional", "panel", "event_log", "longitudinal"],
        help="Optional dataset structural type."
    )
    parser.add_argument(
        "--subject",
        help="Subject description for the dataset (e.g., customer, device, employee)."
    )
    parser.add_argument(
        "--subject-id-attribute",
        help="Subject id attribute name for event_log or panel datasets."
    )
    parser.add_argument(
        "--use-case",
        help="Primary use case description."
    )
    parser.add_argument(
        "--analysis-objective",
        help="Analysis objective description."
    )
    parser.add_argument(
        "--skip-use-case-answers",
        action="store_true",
        help="Do not prompt for optional use case answers."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the captured metadata as JSON instead of saving it to disk."
    )
    return parser.parse_args()

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


def ask_graph_homogeneous_path() -> bool:
    graph_type = console.input(
        "[bold white]Is this a homogeneous graph learnable from tabular data, or another graph type? [homogeneous/other]: [/bold white]"
    ).strip().lower()
    if graph_type in {"homogeneous", "h"}:
        console.print(
            "[bold green]Homogeneous graph selected. The tabular questionnaire will be used for metadata capture.[/bold green]"
        )
        return True

    console.print(
        "[bold red]Only homogeneous graph bootstrapping is supported in this version. Other graph types are out of scope for now.[/bold red]"
    )
    return False


def main():
    args = parse_args()
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

    wide_short_homogeneous = args.wide_short_homogeneous
    if wide_short_homogeneous is None:
        wide_short_homogeneous = ask_yes_no(
            "Is this a wide-and-short homogeneous dataset (one shared axis plus many repeated attributes)? [y/N]: ",
            default_no=True
        )

    wide_short_representative_column = args.wide_short_representative_column
    if wide_short_homogeneous and not wide_short_representative_column:
        headers = []
        try:
            df_raw = pd.read_csv(data_dir / raw_file, nrows=0)
            headers = df_raw.columns.tolist()
            console.print(f"[bold green]Detected raw headers (first 20):[/bold green] {headers[:20]}")
        except Exception:
            console.print("[bold yellow]Warning:[/bold yellow] Could not preview raw dataset headers. Please enter the representative column name exactly as it appears in the file.")

        while True:
            wide_short_representative_column = console.input(
                "[bold white]Enter the representative column name for the homogeneous group: [/bold white]"
            ).strip()
            if not wide_short_representative_column:
                console.print("[red]Representative column is required for a wide-short homogeneous dataset.[/red]")
                continue
            if headers and wide_short_representative_column not in headers:
                console.print(f"[bold yellow]Warning:[/bold yellow] '{wide_short_representative_column}' was not found in the raw headers. Please enter an exact header name.")
                continue
            break

    console.print(Panel(
        "[bold green]Dataset Bootstrapping[/bold green]\n\nThis step captures the dataset type and subject-level metadata before config generation.",
        title="Bootstrapping Phase"
    ))

    graph_mode = args.graph_mode
    if graph_mode is None:
        graph_mode = console.input("[bold white]Do you want to analyze a Graph or Tabular dataset? [Graph/Tabular]: [/bold white]").strip().lower()
    is_homogeneous_graph = False
    if graph_mode in {"graph", "g"}:
        if args.graph_homogeneous:
            is_homogeneous_graph = True
        else:
            if not ask_graph_homogeneous_path():
                sys.exit(1)
            is_homogeneous_graph = True
    elif graph_mode not in {"tabular", "t"}:
        console.print("[bold yellow]Unrecognized choice. Proceeding as Tabular dataset.[/bold yellow]")

    if is_homogeneous_graph:
        console.print(
            "[bold yellow]Note:[/bold yellow] Homogeneous graph metadata will be captured using the tabular questionnaire flow."
        )

    dataset_type = args.dataset_type
    if not dataset_type:
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

    subject = args.subject or locals().get("subject") or ""
    if not subject:
        subject = console.input("[bold white]What is the subject of the dataset? (e.g., customer, device, employee): [/bold white]").strip()

    subject_id_attribute = args.subject_id_attribute
    if dataset_type == "event_log" and not subject_id_attribute:
        subject_id_attribute = console.input("[bold white]Enter the subject id attribute name: [/bold white]").strip()

    use_case_answers = {}
    if not args.skip_use_case_answers:
        if args.use_case or args.analysis_objective:
            if args.use_case:
                use_case_answers["use_case"] = args.use_case
            if args.analysis_objective:
                use_case_answers["analysis_objective"] = args.analysis_objective
        else:
            if ask_yes_no("Would you like to capture short use-case answers for this dataset? [y/N]: "):
                use_case_answers["use_case"] = console.input("[bold white]Describe the primary use case for this dataset: [/bold white]").strip()
                use_case_answers["analysis_objective"] = console.input("[bold white]What is the analysis objective? [/bold white]").strip()

    metadata = {
        "dataset_type": "graph_homogeneous" if is_homogeneous_graph else dataset_type,
        "subject": subject,
        "subject_id_attribute": subject_id_attribute,
        "wide_short_homogeneous": wide_short_homogeneous,
        "wide_short_representative_column": wide_short_representative_column,
        "use_case_answers": use_case_answers,
        "notes": "Generated by dataset bootstrapping."
    }
    if is_homogeneous_graph:
        metadata["graph_type"] = "homogeneous"

    output_path = target_path / "bootstrap_metadata.yaml"
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(metadata, f, sort_keys=False)

    console.print(f"\n[bold green]✅ Success:[/bold green] Bootstrapped metadata written to [cyan]{output_path}[/cyan]")
    if args.json:
        console.print_json(data=metadata)


if __name__ == "__main__":
    main()
