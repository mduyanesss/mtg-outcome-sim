from mtg_outcome_sim.tags.classifier import classify_card

def test_land_tag():
    ct = classify_card("Forest", "", "Basic Land — Forest")
    assert "lands" in ct.tags

def test_ramp_tag():
    ct = classify_card("Rampant Growth", "Search your library for a basic land card, put that card onto the battlefield tapped, then shuffle.", "Sorcery")
    assert "ramp" in ct.tags

def test_removal_tag():
    ct = classify_card("Beast Within", "Destroy target permanent. Its controller creates a 3/3 green Beast creature token.", "Instant")
    assert "removal" in ct.tags

def test_sac_outlet_tag():
    ct = classify_card("Ashnod's Altar", "Sacrifice a creature: Add {C}{C}.", "Artifact")
    assert "sac_outlet" in ct.tags

def test_payoff_tag():
    ct = classify_card("Blood Artist", "Whenever Blood Artist or another creature dies, target player loses 1 life and you gain 1 life.", "Creature — Vampire")
    assert "payoff" in ct.tags

def test_token_maker_tag():
    ct = classify_card("Avenger of Zendikar", "When Avenger of Zendikar enters, create a 0/1 green Plant creature token for each land you control.", "Creature — Elemental")
    assert "token_maker" in ct.tags

def test_multi_tag_card():
    """A card that's both a land and ramp should get both tags."""
    ct = classify_card("Krosan Verge", "{T}: Add {C}.\n{2}, {T}, Sacrifice Krosan Verge: Search your library for a Forest card and a Plains card, put them onto the battlefield tapped, then shuffle.", "Land")
    assert "lands" in ct.tags
    assert "ramp" in ct.tags

def test_land_does_not_get_ramp():
    """Basic lands should NOT be tagged as ramp."""
    ct = classify_card("Forest", "({T}: Add {G}.)", "Basic Land — Forest")
    assert "lands" in ct.tags
    assert "ramp" not in ct.tags

def test_mana_dork_gets_ramp():
    """Non-land mana producers SHOULD be tagged as ramp."""
    ct = classify_card("Llanowar Elves", "{T}: Add {G}.", "Creature — Elf Druid")
    assert "ramp" in ct.tags
    assert "lands" not in ct.tags

def test_fetchland_gets_ramp():
    """Fetchlands search for lands, so they ARE ramp despite being lands."""
    ct = classify_card("Verdant Catacombs", "{T}, Pay 1 life, Sacrifice Verdant Catacombs: Search your library for a Swamp or Forest card, put it onto the battlefield, then shuffle.", "Land")
    assert "lands" in ct.tags
    assert "ramp" in ct.tags

def test_tag_overrides():
    """Manual overrides should add tags."""
    overrides = {"Random Card": {"combo_piece"}}
    ct = classify_card("Random Card", "No relevant text", "Creature", overrides=overrides)
    assert "combo_piece" in ct.tags

def test_tag_overrides_dont_remove():
    """Manual overrides should add to existing tags, not replace them."""
    overrides = {"Forest": {"combo_piece"}}
    ct = classify_card("Forest", "({T}: Add {G}.)", "Basic Land — Forest", overrides=overrides)
    assert "lands" in ct.tags
    assert "combo_piece" in ct.tags
    assert "ramp" not in ct.tags
