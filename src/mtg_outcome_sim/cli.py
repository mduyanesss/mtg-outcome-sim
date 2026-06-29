import typer
from pathlib import Path

app = typer.Typer(name="mtg-outcome-sim")


@app.command(name="import")
def import_(deck_path: Path = typer.Argument(..., help="Path to decklist file")):
    """Import and parse a decklist, showing a summary."""
    text = deck_path.read_text()
    from .decklist.parser import parse_decklist

    deck = parse_decklist(text)
    typer.echo(f"Deck: {len(deck.cards)} unique cards, {deck.total_count} total")
    typer.echo(f"Format: {deck.format}")
    typer.echo("---")
    for card in deck.cards[:10]:
        typer.echo(f"  {card.quantity}x {card.name}")
    if len(deck.cards) > 10:
        typer.echo(f"  ... and {len(deck.cards) - 10} more")


@app.command()
def outcomes(
    outcomes_path: Path = typer.Argument(..., help="Path to outcome definitions YAML"),
):
    """List outcome definitions from a YAML file."""
    from .simulation.outcome import load_outcomes

    config = load_outcomes(outcomes_path)
    typer.echo(f"Deck format: {config.deck_format}")
    typer.echo(f"Commander: {config.commander}")
    typer.echo(f"Turn limit: {config.turn_limit}")
    typer.echo(f"Iterations: {config.iterations:,}")
    typer.echo("")
    for i, o in enumerate(config.outcomes):
        typer.echo(f"{i+1}. {o.name}")
        typer.echo(f"   Type: {o.type}, Tag: {o.tag}, Min: {o.minimum}, By turn: {o.by_turn}")
        if o.groups:
            for g in o.groups:
                typer.echo(f"   - {g['tag']}: min {g['minimum']}")


@app.command()
def run(
    deck_path: Path = typer.Argument(..., help="Path to decklist file"),
    outcomes_path: Path = typer.Argument(..., help="Path to outcome definitions YAML"),
    iterations: int = typer.Option(100000, help="Monte Carlo iterations"),
    seed: int = typer.Option(42, help="Random seed"),
    method: str = typer.Option("monte_carlo", help="Method: hypergeometric or monte_carlo"),
    output_dir: Path = typer.Option(None, help="Output directory for reports"),
    report_format: str = typer.Option("all", help="Report formats: json, markdown, console, all"),
):
    """Run outcome simulations on a decklist and generate reports."""
    from .decklist.parser import parse_decklist
    from .cards.normalizer import normalize
    from .tags.classifier import classify_card
    from .simulation.outcome import load_outcomes
    from .simulation.hypergeometric import prob_at_least
    from .simulation.monte_carlo import run_simulation
    from .reports.console import print_console_report
    from .reports.json_report import generate_json_report
    from .reports.markdown import generate_markdown_report

    # Load deck
    text = deck_path.read_text()
    deck = parse_decklist(text)

    # Normalize card names (best effort - skip Scryfall failures)
    card_data = []
    for card in deck.cards:
        cd = normalize(card.name)
        card_data.append(
            (
                card.name,
                cd.oracle_text if cd else "",
                cd.type_line if cd else "",
            )
        )

    # Classify tags
    deck_tags_dict: dict[str, set[str]] = {}
    for name, oracle, type_line in card_data:
        ct = classify_card(name, oracle, type_line)
        deck_tags_dict[name] = ct.tags

    # Build full population (each card counted once for Commander singleton;
    # for non-singleton formats, replicate by quantity).
    population_tags: dict[str, set[str]] = {}
    idx = 0
    for card in deck.cards:
        count = card.quantity
        for _ in range(count):
            population_tags[f"{card.name}_{idx}"] = deck_tags_dict.get(card.name, set())
            idx += 1

    # Load outcomes
    config = load_outcomes(outcomes_path)

    typer.echo(f"Running {len(config.outcomes)} outcomes on {len(population_tags)} cards...")

    # Compute tag distribution counts from the population
    tag_counts: dict[str, int] = {}
    for tags in population_tags.values():
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Run simulations and collect results
    results: list[dict] = []
    for outcome_def in config.outcomes:
        od = {
            "name": outcome_def.name,
            "type": outcome_def.type,
            "tag": outcome_def.tag,
            "minimum": outcome_def.minimum,
            "by_turn": outcome_def.by_turn,
        }
        if outcome_def.groups:
            od["groups"] = outcome_def.groups

        if method == "hypergeometric" and outcome_def.type in (
            "minimum_cards_seen",
            "has_tag",
        ):
            tag = outcome_def.tag
            tagged_count = sum(1 for tags in population_tags.values() if tag in tags)
            draws = 7 + (outcome_def.by_turn - 1)  # on the play
            prob = prob_at_least(
                len(population_tags), tagged_count, draws, outcome_def.minimum
            )
            result_entry = {
                "name": outcome_def.name,
                "type": outcome_def.type,
                "probability": prob,
                "method": "Hypergeometric",
                "by_turn": outcome_def.by_turn,
            }
        else:
            mc_result = run_simulation(
                population_tags, od, iterations=iterations, seed=seed
            )
            result_entry = {
                "name": outcome_def.name,
                "type": outcome_def.type,
                "probability": mc_result.probability,
                "method": "Monte Carlo",
                "iterations": mc_result.iterations,
                "by_turn": outcome_def.by_turn,
            }

        results.append(result_entry)

    # Print console report (always)
    if report_format in ("console", "all"):
        deck_name = deck_path.stem
        print_console_report(deck_name, tag_counts, results)

    # Write file reports if output_dir specified
    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        deck_name = deck_path.stem

        if report_format in ("json", "all"):
            json_path = output_dir / "report.json"
            generate_json_report(
                deck_name=deck_name,
                deck_format=config.deck_format,
                commander=config.commander,
                card_count=len(population_tags),
                tag_counts=tag_counts,
                results=results,
                output_path=json_path,
            )
            typer.echo(f"JSON report: {json_path}")

        if report_format in ("markdown", "all"):
            md_path = output_dir / "report.md"
            generate_markdown_report(
                deck_name=deck_name,
                deck_format=config.deck_format,
                commander=config.commander,
                card_count=len(population_tags),
                tag_counts=tag_counts,
                results=results,
                output_path=md_path,
            )
            typer.echo(f"Markdown report: {md_path}")

    typer.echo("Done.")


if __name__ == "__main__":
    app()
