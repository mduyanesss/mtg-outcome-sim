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
def run():
    """Run a simulation."""
    typer.echo("Not yet implemented")

if __name__ == "__main__":
    app()
