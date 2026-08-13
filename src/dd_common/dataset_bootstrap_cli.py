import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import yaml
from rich.console import Console
from rich.panel import Panel

from dd_common.utilities import verify_workspace_status

console = Console()


VALID_DATASET_TYPES = {
    "cross-sectional",
    "panel",
    "event_log",
    "graph_homogeneous",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap dataset metadata before generating config.",
        epilog=(
            "After running dataset-bootstrap, run 'bootstrap-config --output config.yaml .' "
            "to publish bootstrap metadata into config.yaml so it is available to the parser, "
            "cleaner, and notebook metadata flows."
        ),
    )
    parser.add_argument("working_dir", nargs="?", help="The working directory to inspect.")
    parser.add_argument(
        "--wide-short-homogeneous",
        dest="wide_short_homogeneous",
        action="store_true",
        default=None,
        help="Mark the dataset as wide-and-short homogeneous.",
    )
    parser.add_argument(
        "--no-wide-short-homogeneous",
        dest="wide_short_homogeneous",
        action="store_false",
        help="Explicitly mark the dataset as not wide-and-short homogeneous.",
    )
    parser.add_argument(
        "--wide-short-representative-column",
        help="Representative column name for wide-short homogeneous datasets.",
    )
    parser.add_argument(
        "--graph-mode",
        choices=["node_list", "edge_list", "tabular", "graph", "graph_homogeneous"],
        help="Choose whether the dataset is a graph or tabular dataset.",
    )
    parser.add_argument(
        "--graph-homogeneous",
        action="store_true",
        help="Mark the graph dataset as homogeneous and learnable from tabular data.",
    )
    parser.add_argument(
        "--dataset-type",
        choices=["cross-sectional", "panel", "event_log", "longitudinal", "graph_homogeneous"],
        help="Optional dataset structural type.",
    )
    parser.add_argument("--subject", help="Subject description for the dataset.")
    parser.add_argument("--subject-id-attribute", help="Subject id attribute name for event_log or panel datasets.")
    parser.add_argument("--use-case", help="Primary use case description.")
    parser.add_argument("--analysis-objective", help="Analysis objective description.")
    parser.add_argument("--skip-use-case-answers", action="store_true", help="Do not prompt for optional use case answers.")
    parser.add_argument("--json", action="store_true", help="Output the captured metadata as JSON instead of saving it to disk.")
    return parser.parse_args()


def ask_yes_no(prompt: str, default_no: bool = True) -> bool:
    answer = console.input(f"[bold white]{prompt} [/bold white]").strip().lower()
    if not answer:
        return not default_no
    return answer in {"y", "yes", "true", "1"}


def choose_from_list(options: list[str], prompt: str) -> int:
    for idx, option in enumerate(options):
        console.print(f" [{idx}] {option}")
    while True:
        raw = console.input(f"[bold white]{prompt} [/bold white]").strip()
        try:
            choice = int(raw)
        except ValueError:
            try:
                choice = int(raw.strip("[]"))
            except ValueError:
                choice = -1
        if 0 <= choice < len(options):
            return choice
        console.print("[red]Invalid selection. Please enter a number.[/red]")


def list_data_files(directory: Path) -> list[Path]:
    files = []
    for path in sorted(directory.iterdir(), key=lambda p: p.name):
        if path.is_file() and path.suffix.lower() in {".csv", ".parquet"}:
            files.append(path)
    return files


def resolve_data_targets(data_dir: Path, target_path: Path):
    data_files = list_data_files(data_dir)
    if not data_files:
        console.print(f"[bold red]❌ Error:[/bold red] No valid CSV/Parquet files found in [cyan]{data_dir.relative_to(target_path)}[/cyan].")
        return [], "single_file"

    if len(data_files) == 1:
        return [data_files[0]], "single_file"

    console.print("\n[bold yellow]I see multiple files in your 'data/' directory.[/bold yellow]")
    console.print("[white]1) Connected components: related parts of a single network/relational dataset[/white]")
    console.print("[white]2) Independent/Redundant: separate copies or backups; pick one active file[/white]")
    response = console.input("[bold white]How should these be treated? [1/2]: [/bold white]").strip().lower()
    if response in {"1", "connected", "multi", "graph", "network"}:
        return data_files, "multi_file"

    choice = choose_from_list([p.name for p in data_files], "Select the single active data file: ")
    return [data_files[choice]], "single_file"


def resolve_dictionary_target(dd_dir: Path, target_path: Path) -> str | None:
    files = list_data_files(dd_dir)
    if not files:
        console.print(f"[bold red]❌ Error:[/bold red] No valid dictionary files found in [cyan]{dd_dir.relative_to(target_path)}[/cyan].")
        return None
    if len(files) == 1:
        return files[0].name

    choice = choose_from_list([p.name for p in files], "Select the correct data dictionary file: ")
    return files[choice].name


def legacy_prompt_workflow(target_path: Path, raw_file: str, dd_file: str, args: argparse.Namespace):
    data_dir = target_path / "data"
    subject = args.subject or ""
    dataset_type = args.dataset_type
    graph_mode = args.graph_mode

    wide_short_homogeneous = args.wide_short_homogeneous
    if wide_short_homogeneous is None:
        wide_short_homogeneous = ask_yes_no(
            "Is this a wide-and-short homogeneous dataset (one shared axis plus many repeated attributes)? [y/N]: ",
            default_no=True,
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
        title="Bootstrapping Phase",
    ))

    if graph_mode is None:
        graph_mode = console.input("[bold white]Do you want to analyze a Graph or Tabular dataset? [Graph/Tabular]: [/bold white]").strip().lower()

    is_homogeneous_graph = False
    if graph_mode in {"graph", "g", "node_list", "edge_list", "graph_homogeneous"}:
        if args.graph_homogeneous or graph_mode in {"node_list", "edge_list", "graph_homogeneous"}:
            is_homogeneous_graph = True
        else:
            graph_type = console.input(
                "[bold white]Is this a homogeneous graph learnable from tabular data, or another graph type? [homogeneous/other]: [/bold white]"
            ).strip().lower()
            if graph_type in {"homogeneous", "h"}:
                is_homogeneous_graph = True
            else:
                console.print("[bold red]Only homogeneous graph bootstrapping is supported in this version. Other graph types are out of scope for now.[/bold red]")
                sys.exit(1)

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

    subject = args.subject or subject or ""
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
        "notes": "Generated by dataset bootstrapping.",
    }
    if is_homogeneous_graph:
        metadata["graph_type"] = "homogeneous"
    return metadata


def _infer_wide_short_shape(data_file: Path) -> tuple[bool, str | None]:
    """Infers whether a tabular dataset is wide-short from its shape.

    Conservative policy: treat as wide-short only when the dataset is compact on rows
    relative to the number of observed features, e.g. rows <= 0.5 * columns with a
    minimum feature count guardrail. This avoids over-classifying normal tabular data.
    """
    try:
        df = pd.read_csv(data_file, nrows=50)
    except Exception:
        return False, None

    if df.empty:
        return False, None

    num_rows = len(df)
    num_cols = len(df.columns)
    if num_cols < 6 or num_rows < 2:
        return False, None

    if num_rows <= max(2, int(num_cols * 0.5)):
        id_like = {"id", "customer_id", "subject_id", "user_id", "record_id", "entity_id", "loan_id", "account_id"}
        columns = list(df.columns)
        candidate = None
        for col in columns:
            name = str(col).lower()
            if name.endswith("_id") or name in id_like:
                continue
            candidate = col
            break
        if candidate is None:
            candidate = columns[0] if columns else None
        return True, candidate

    return False, None


def new_staged_workflow(target_path: Path, data_files: list[Path], dd_file: str, args: argparse.Namespace):
    file_headers = []
    if data_files:
        try:
            first_df = pd.read_csv(data_files[0], nrows=0)
            file_headers = first_df.columns.tolist()
        except Exception:
            file_headers = []

    auto_wide_short = False
    auto_wide_short_rep = None
    if args.wide_short_homogeneous is None:
        auto_wide_short, auto_wide_short_rep = _infer_wide_short_shape(data_files[0])

    wide_short_homogeneous = args.wide_short_homogeneous
    wide_short_representative_column = args.wide_short_representative_column
    if wide_short_homogeneous is None:
        wide_short_homogeneous = auto_wide_short
    if wide_short_homogeneous and not wide_short_representative_column:
        wide_short_representative_column = auto_wide_short_rep

    if len(data_files) > 1:
        response = console.input(
            "[bold white]Is this a homogeneous graph learnable from flat files, or another graph structure? [homogeneous/other]: [/bold white]"
        ).strip().lower()
        if response in {"other", "heterogeneous", "2"}:
            console.print("[bold red]ABORT:[/bold red] Heterogeneous and multi-entity relational graphs are currently out of scope for this version of dd-parser-cleaner.")
            raise SystemExit(1)
        graph_mode = "tabular"
        graph_type = "homogeneous"
        dataset_type = "graph_homogeneous"
    else:
        response = console.input(
            "[bold white]In your data file, does a single row represent one subject or an interaction between subjects? [1/2/tabular/graph]: [/bold white]"
        ).strip().lower()
        if response in {"2", "interaction", "edge", "transaction", "link"}:
            edge_same_type = ask_yes_no("Are the interacting subjects of the same type? [y/N]: ", default_no=True)
            if not edge_same_type:
                console.print("[bold red]ABORT:[/bold red] Heterogeneous edge lists are out of scope for this version.")
                raise SystemExit(1)
            dataset_type = "graph_homogeneous"
            graph_mode = "edge_list"
            graph_type = "homogeneous"
        else:
            goal = console.input(
                "[bold white]What is your primary analysis goal? [1=tabular/2=network]: [/bold white]"
            ).strip().lower()
            if goal in {"2", "network", "graph", "node"}:
                breaker = ask_yes_no("Are you building a true network graph? [y/N]: ", default_no=True)
                if breaker:
                    dataset_type = "graph_homogeneous"
                    graph_mode = "node_list"
                    graph_type = "homogeneous"
                else:
                    dataset_type = "tabular"
                    graph_mode = "tabular"
                    graph_type = None
            else:
                dataset_type = "tabular"
                graph_mode = "tabular"
                graph_type = None

    subject = args.subject or ""
    if dataset_type != "graph_homogeneous" or graph_mode in {"tabular", "edge_list", "node_list"}:
        subject = subject or console.input(
            "[bold white]What is the single primary subject you are tracking in this file? (e.g., customer, server, student): [/bold white]"
        ).strip()

    if dataset_type == "graph_homogeneous":
        final_dataset_type = "graph_homogeneous"
    else:
        taxonomy_choice = console.input(
            "[bold white]How do your subject_id values appear? [1=cross-sectional/2=event_log/3=panel]: [/bold white]"
        ).strip().lower()
        if taxonomy_choice in {"1", "cross-sectional", "cross", "single"}:
            final_dataset_type = "cross-sectional"
        elif taxonomy_choice in {"2", "event_log", "event", "transaction", "log"}:
            final_dataset_type = "event_log"
        elif taxonomy_choice in {"3", "panel", "longitudinal"}:
            final_dataset_type = "panel"
        else:
            final_dataset_type = "cross-sectional"

    if final_dataset_type in {"cross-sectional", "event_log", "panel"} and args.wide_short_homogeneous is None:
        wide_short_homogeneous = auto_wide_short

    if wide_short_homogeneous and not wide_short_representative_column:
        if file_headers:
            console.print(f"[bold green]Discovered columns:[/bold green] {file_headers[:20]}")
        if auto_wide_short_rep:
            wide_short_representative_column = auto_wide_short_rep
        elif args.wide_short_homogeneous is True:
            while True:
                wide_short_representative_column = console.input("[bold white]Enter the wide-short representative base column name: [/bold white]").strip()
                if not wide_short_representative_column:
                    console.print("[red]Representative column is required for a wide-short homogeneous dataset.[/red]")
                    continue
                if file_headers and wide_short_representative_column not in file_headers:
                    console.print(f"[bold yellow]Warning:[/bold yellow] '{wide_short_representative_column}' is not present in the detected headers. Please re-enter the exact column name.")
                    continue
                break

    has_wide_short_override = args.wide_short_homogeneous is not None
    if final_dataset_type == "graph_homogeneous" and not has_wide_short_override:
        wide_short_homogeneous = False
    elif wide_short_homogeneous is None:
        wide_short_homogeneous = False

    if not wide_short_homogeneous:
        wide_short_representative_column = None

    subject_id_attribute = args.subject_id_attribute
    if final_dataset_type in {"event_log", "panel"} and not subject_id_attribute:
        subject_id_attribute = console.input("[bold white]Enter the subject id attribute name: [/bold white]").strip() or ""

    use_case_answers = {}
    if not args.skip_use_case_answers:
        if args.use_case or args.analysis_objective:
            if args.use_case:
                use_case_answers["use_case"] = args.use_case
            if args.analysis_objective:
                use_case_answers["analysis_objective"] = args.analysis_objective
        elif ask_yes_no("Would you like to capture short use-case answers for this dataset? [y/N]: "):
            use_case_answers["use_case"] = console.input("[bold white]Describe the primary use case for this dataset: [/bold white]").strip()
            use_case_answers["analysis_objective"] = console.input("[bold white]What is the analysis objective? [/bold white]").strip()

    metadata = {
        "dataset_type": final_dataset_type,
        "graph_mode": graph_mode,
        "subject": subject,
        "subject_id_attribute": subject_id_attribute,
        "wide_short_homogeneous": wide_short_homogeneous,
        "wide_short_representative_column": wide_short_representative_column,
        "use_case_answers": use_case_answers,
        "notes": "Generated by dataset bootstrapping.",
    }
    if graph_type:
        metadata["graph_type"] = graph_type
    return metadata


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

    data_files, data_layout = resolve_data_targets(data_dir, target_path)
    dd_file = resolve_dictionary_target(dd_dir, target_path)
    if not data_files or not dd_file:
        console.print("\n[bold red]Stopping:[/bold red] Required files are missing. Please populate the directories and run this utility again.")
        sys.exit(1)

    metadata = new_staged_workflow(target_path, data_files, dd_file, args)

    output_path = target_path / "bootstrap_metadata.yaml"
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(metadata, f, sort_keys=False)

    console.print(f"\n[bold green]✅ Success:[/bold green] Bootstrapped metadata written to [cyan]{output_path}[/cyan]")
    console.print("[bold blue]Next step:[/bold blue] Run [white]bootstrap-config --output config.yaml .[/white] to publish the bootstrap metadata into the active runtime config.")
    if args.json:
        console.print_json(data=metadata)


if __name__ == "__main__":
    main()
