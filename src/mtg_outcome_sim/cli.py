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
def outcomes():
    """List available outcome definitions."""
    typer.echo("Not yet implemented")


@app.command()
def run(
    deck_path: Path = typer.Argument(..., help="Path to decklist file"),
    outcomes_path: Path = typer.Argument(..., help="Path to outcome definitions YAML"),
    iterations: int = typer.Option(100000, help="Monte Carlo iterations"),
    seed: int = typer.Option(42, help="Random seed for reproducibility"),
    method: str = typer.Option("monte_carlo", help="Method: hypergeometric or monte_carlo"),
):
    """Run outcome simulations on a decklist."""
    from .decklist.parser import parse_decklist
    from .cards.normalizer import normalize
    from .tags.classifier import classify_card
    from .simulation.outcome import load_outcomes
    from .simulation.hypergeometric import prob_at_least
    from .simulation.monte_carlo import run_simulation

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

    # Run
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
            # Count tagged cards
            tag = outcome_def.tag
            tagged_count = sum(1 for tags in population_tags.values() if tag in tags)
            draws = 7 + (outcome_def.by_turn - 1)  # on the play
            prob = prob_at_least(
                len(population_tags), tagged_count, draws, outcome_def.minimum
            )
            typer.echo(f"  {outcome_def.name}: {prob:.2%} (hypergeometric)")
        else:
            result = run_simulation(
                population_tags, od, iterations=iterations, seed=seed
            )
            typer.echo(
                f"  {outcome_def.name}: {result.probability:.2%} "
                f"(MC, {result.iterations} iters)"
            )

    typer.echo("Done.")


if __name__ == "__main__":
    app()
