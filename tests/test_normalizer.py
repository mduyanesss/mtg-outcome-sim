from mtg_outcome_sim.cards.normalizer import normalize

def test_normalize_forest():
    # Exact match should work
    card = normalize("Forest")
    assert card is not None
    assert card.name == "Forest"

def test_normalize_fuzzy():
    # Partial name fuzzy match (Scryfall rejects very short names as ambiguous)
    card = normalize("Squirrel General")
    assert card is not None
    assert "Chatterfang" in card.name

def test_normalize_unknown():
    card = normalize("XyzzyNotACardName12345")
    assert card is None

def test_cache_roundtrip():
    from mtg_outcome_sim.cards.mtgjson_cache import Cache
    c = Cache()
    c.put("test_card", {"name": "Test Card", "oracle_text": ""})
    assert c.has("test_card")
    data = c.get("test_card")
    assert data["name"] == "Test Card"
