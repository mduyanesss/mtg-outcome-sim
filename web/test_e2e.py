"""End-to-end test simulating the Pyodide web app flow.

This script loads the sim_bundle.py, sets up the card data, and runs
the simulation just like the browser would. Run from the web/ directory.
"""

import json
import sys
import os

# 1. Load the simulation bundle (same as Pyodide running sim_bundle.py)
sys.path.insert(0, os.path.dirname(__file__))
with open(os.path.join(os.path.dirname(__file__), "sim_bundle.py"), encoding="utf-8") as f:
    exec(compile(f.read(), "sim_bundle.py", "exec"))

# 2. Load card data (same as Pyodide FS mounting)
with open(os.path.join(os.path.dirname(__file__), "deck_data.json"), encoding="utf-8") as f:
    _card_data = json.load(f)

# 3. Patch the preload module's load_card_data to use our data
#    (The preload.py uses /app/deck_data.json which won't exist locally)
#    We'll just inline the run_simulation logic here directly.

from mtg_outcome_sim.decklist.parser import parse_decklist
from mtg_outcome_sim.tags.classifier import classify_card
from mtg_outcome_sim.simulation.monte_carlo import run_simulation as mc_run
import yaml

# Normalize card data lookup
def get_card_info(name):
    for card in _card_data:
        if card["name"] == name:
            return card
    name_lower = name.lower()
    for card in _card_data:
        if card["name"].lower() == name_lower:
            return card
    for card in _card_data:
        cl = card["name"].lower()
        if name_lower in cl or cl in name_lower:
            return card
    return {"name": name, "oracle_text": "", "type_line": ""}

# Load sample deck
with open(os.path.join(os.path.dirname(__file__), "sample_deck.txt"), encoding="utf-8") as f:
    deck_text = f.read()

# Load default outcomes
with open(os.path.join(os.path.dirname(__file__), "default_outcomes.yaml"), encoding="utf-8") as f:
    outcomes_yaml_text = f.read()

# Parse deck
deck = parse_decklist(deck_text)
print(f"Deck: {len(deck.cards)} unique, {deck.total_count} total, format={deck.format}")

# Classify cards
tagged_cards = {}
tag_counts = {}
for card in deck.cards:
    info = get_card_info(card.name)
    ct = classify_card(
        card.name,
        info.get("oracle_text", ""),
        info.get("type_line", ""),
    )
    tagged_cards[card.name] = list(ct.tags)
    for tag in ct.tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + card.quantity

print("\nTag distribution:")
for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
    print(f"  {tag}: {count}")

# Build population
population_tags = {}
idx = 0
for card in deck.cards:
    for _ in range(card.quantity):
        population_tags[f"{card.name}_{idx}"] = set(tagged_cards.get(card.name, []))
        idx += 1

# Parse outcomes
config = yaml.safe_load(outcomes_yaml_text)
print(f"\nRunning {len(config['outcomes'])} outcomes on {len(population_tags)} cards...")

# Run simulations
results = []
for od in config["outcomes"]:
    outcome_dict = {
        "name": od["name"],
        "type": od["type"],
        "tag": od.get("tag"),
        "minimum": od.get("minimum", 1),
        "by_turn": od["by_turn"],
    }
    if "groups" in od:
        outcome_dict["groups"] = od["groups"]

    result = mc_run(population_tags, outcome_dict, iterations=50000, seed=42)
    pct = result.probability * 100
    print(f"  {od['name']}: {pct:.1f}% ({result.successes}/{result.iterations} successes)")
    results.append({
        "name": od["name"],
        "probability": round(result.probability, 4),
    })

print("\nAll outcomes completed successfully!")
