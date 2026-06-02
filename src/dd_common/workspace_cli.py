import argparse
import sys
from pathlib import Path
from dd_common.utilities import prepare_workspace, verify_workspace_status
from rich.console import Console

console = Console()

def main():
    """CLI entry point to initialize or verify a dd-parser-cleaner workspace."""
    parser = argparse.ArgumentParser(description="Initialize a dd-parser-cleaner workspace.")
    parser.add_argument(
        "working_dir", 
        nargs="?", 
        help="The working directory to set up. If omitted, you will be prompted."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check if the workspace is set up; do not create any directories."
    )
    args = parser.parse_args()

    working_dir = args.working_dir
    if not working_dir:
        working_dir = console.input("[bold blue]Enter the working directory path to initialize [default: .]: [/bold blue]").strip() or "."

    target_path = Path(working_dir).resolve()

    # 1. Verification Phase (First order of business)
    is_ready = verify_workspace_status(working_dir)
    
    if args.check:
        if is_ready:
            console.print(f"[bold green]✅ Success:[/bold green] Workspace at [cyan]{target_path}[/cyan] is properly configured.")
            sys.exit(0)
        else:
            console.print(f"[bold red]❌ Error:[/bold red] Workspace at [cyan]{target_path}[/cyan] is NOT configured.")
            sys.exit(1)

    console.print(f"🚀 [bold]Initializing workspace at:[/bold] [cyan]{target_path}[/cyan]")
    prepare_workspace(working_dir=working_dir)
    console.print("[bold green]✅ Workspace verification and setup complete.[/bold green]")

if __name__ == "__main__":
    main()