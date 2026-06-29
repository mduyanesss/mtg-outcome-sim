from pydantic import BaseModel
from .plain_text import parse_plain_text

class ParsedCard(BaseModel):
    name: str
    quantity: int

class ParsedDeck(BaseModel):
    cards: list[ParsedCard]
    total_count: int
    format: str = "unknown"

def parse_decklist(text: str) -> ParsedDeck:
    """Parse a decklist string into a ParsedDeck."""
    raw = parse_plain_text(text)
    cards = [ParsedCard(name=name, quantity=qty) for qty, name in raw]
    total = sum(c.quantity for c in cards)
    # Detect commander: ~100 cards, singleton (all qty=1 for non-basics, basics can be many)
    fmt = "commander" if 98 <= total <= 100 else "unknown"
    return ParsedDeck(cards=cards, total_count=total, format=fmt)
