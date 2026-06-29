from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def print_mana_curve_table(mana_curve_data: list[dict]) -> None:
    """Print a mana curve summary table using Rich.

    Args:
        mana_curve_data: List of dicts from simulate_mana_curve_mc, each with keys:
            turn, mean_mana, median_mana, p10_mana, p90_mana.
    """
    console.print(Panel.fit("[bold]Mana Curve[/bold]", border_style="yellow"))

    table = Table(title="Mana Availability by Turn (10k iterations)")
    table.add_column("Turn", justify="right", style="white")
    table.add_column("Mean", justify="right", style="cyan")
    table.add_column("Median", justify="right", style="green")
    table.add_column("P10", justify="right", style="dim")
    table.add_column("P90", justify="right", style="dim")

    for row in mana_curve_data:
        table.add_row(
            str(row["turn"]),
            f"{row['mean_mana']:.2f}",
            str(row["median_mana"]),
            str(row["p10_mana"]),
            str(row["p90_mana"]),
        )

    console.print(table)


def print_console_report(
    deck_name: str,
    tag_counts: dict[str, int],
    results: list[dict],
    mana_curve_data: list[dict] | None = None,
):
    """Print a formatted console report using Rich.

    Args:
        deck_name: Name of the deck to display.
        tag_counts: Mapping of tag name -> count in deck.
        results: List of result dicts, each with keys:
            name, type, probability, method, and optionally
            iterations, by_turn.
        mana_curve_data: Optional mana curve data from simulate_mana_curve_mc.
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

    if mana_curve_data:
        print_mana_curve_table(mana_curve_data)
