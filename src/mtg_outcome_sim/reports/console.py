from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def print_console_report(
    deck_name: str,
    tag_counts: dict[str, int],
    results: list[dict],
):
    """Print a formatted console report using Rich.

    Args:
        deck_name: Name of the deck to display.
        tag_counts: Mapping of tag name -> count in deck.
        results: List of result dicts, each with keys:
            name, type, probability, method, and optionally
            iterations, by_turn.
    """
    console.print(Panel.fit(f"[bold]{deck_name}[/bold] - Tag Distribution", border_style="blue"))

    tag_table = Table(title="Card Tags")
    tag_table.add_column("Tag", style="cyan")
    tag_table.add_column("Count", justify="right", style="green")
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        tag_table.add_row(tag, str(count))
    console.print(tag_table)

    console.print(Panel.fit("[bold]Outcome Probabilities[/bold]", border_style="blue"))

    results_table = Table(title="Results")
    results_table.add_column("Outcome", style="white")
    results_table.add_column("Probability", justify="right", style="bold green")
    results_table.add_column("Method", style="dim")
    results_table.add_column("Details", style="dim")

    for r in results:
        pct = f"{r['probability']:.2%}"
        method = r["method"]
        details = ""
        if "by_turn" in r:
            details += f"by T{r['by_turn']} "
        if r["method"] == "Monte Carlo" and "iterations" in r:
            details += f"({r['iterations']:,} iters)"
        results_table.add_row(r["name"], pct, method, details.strip())

    console.print(results_table)
