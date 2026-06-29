import re

def parse_plain_text(text: str) -> list[tuple[int, str]]:
    """Parse a plain-text decklist into (quantity, card_name) tuples."""
    cards = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        # Remove set codes, collector numbers, foil markers
        line = re.sub(r'\s*\([^)]*\)\s*', ' ', line)
        line = re.sub(r'\s*\*F\*\s*', ' ', line)
        # Match "1 Card Name" or "1x Card Name"
        m = re.match(r'^(\d+)\s*x?\s*(.+?)\s*$', line, re.IGNORECASE)
        if m:
            qty = int(m.group(1))
            name = m.group(2).strip()
            cards.append((qty, name))
    return cards
