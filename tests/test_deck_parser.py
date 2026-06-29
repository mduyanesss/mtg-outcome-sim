from mtg_outcome_sim.decklist.parser import parse_decklist

SAMPLE = """1 Chatterfang, Squirrel General
1 Forest
1 Swamp
1 Llanowar Elves
2 Beast Whisperer

# Sideboard
// Comment
1x Sol Ring
"""

def test_parse_counts():
    deck = parse_decklist(SAMPLE)
    assert deck.total_count == 7  # 5+2

def test_parses_format():
    deck = parse_decklist(SAMPLE)
    names = [c.name for c in deck.cards]
    assert "Chatterfang, Squirrel General" in names
    assert "Forest" in names
    assert "Llanowar Elves" in names
    assert "Beast Whisperer" in names
    assert "Sol Ring" in names

def test_ignores_comments():
    deck = parse_decklist(SAMPLE)
    names = [c.name for c in deck.cards]
    assert "Sideboard" not in names

def test_commander_detection():
    # 100 cards is commander
    text = "\n".join([f"1 Card {i}" for i in range(100)])
    deck = parse_decklist(text)
    assert deck.format == "commander"

def test_unknown_format():
    # 60 cards is not commander
    text = "\n".join([f"4 Card {i}" for i in range(15)])
    deck = parse_decklist(text)
    assert deck.format == "unknown"
