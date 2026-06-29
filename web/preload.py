import json
import sys
from pathlib import Path

# The mtg_outcome_sim source will be mounted at /src
sys.path.insert(0, "/src")

# Preload card data
_card_data = None


def load_card_data():
    """Load the pre-fetched Scryfall card data."""
    global _card_data
    if _card_data is None:
        with open("/app/deck_data.json", encoding="utf-8") as f:
            _card_data = json.load(f)
    return _card_data


def get_card_info(name):
    """Look up oracle text and type line for a card name.

    Tries exact match first, then case-insensitive, then fuzzy substring.
    """
    data = load_card_data()
    # Exact case-sensitive match
    for card in data:
        if card["name"] == name:
            return card
    # Case-insensitive match
    name_lower = name.lower()
    for card in data:
        if card["name"].lower() == name_lower:
            return card
    # Fuzzy match: substring in either direction
    for card in data:
        cl = card["name"].lower()
        if name_lower in cl or cl in name_lower:
            return card
    # Fallback: empty data
    return {"name": name, "oracle_text": "", "type_line": ""}


def run_simulation(deck_text, outcomes_yaml_text, iterations=50000, seed=42):
    """Run the full simulation pipeline and return results as a dict.

    Args:
        deck_text: Plain text decklist (one card per line, "1 Card Name" format).
        outcomes_yaml_text: YAML outcome definitions.
        iterations: Monte Carlo trial count.
        seed: Random seed for reproducibility.

    Returns:
        Dict with "deck", "outcomes", and "tagged_cards" keys.
    """
    from mtg_outcome_sim.decklist.parser import parse_decklist
    from mtg_outcome_sim.tags.classifier import classify_card
    from mtg_outcome_sim.simulation.monte_carlo import run_simulation as mc_run
    import yaml
    import random as py_random

    # ---------- Parse deck ----------
    deck = parse_decklist(deck_text)

    # ---------- Classify cards ----------
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

    # ---------- Build population (each card instance gets its own entry) ----------
    population_tags = {}
    idx = 0
    for card in deck.cards:
        for _ in range(card.quantity):
            population_tags[f"{card.name}_{idx}"] = set(
                tagged_cards.get(card.name, [])
            )
            idx += 1

    # ---------- Parse outcomes YAML ----------
    config = yaml.safe_load(outcomes_yaml_text)

    # ---------- Run simulations ----------
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

        result = mc_run(
            population_tags, outcome_dict, iterations=iterations, seed=seed
        )
        results.append(
            {
                "name": od["name"],
                "type": od["type"],
                "probability": round(result.probability, 4),
                "iterations": result.iterations,
                "by_turn": od["by_turn"],
            }
        )

    return {
        "deck": {
            "total_cards": deck.total_count,
            "format": deck.format,
            "tag_distribution": tag_counts,
        },
        "outcomes": results,
        "tagged_cards": tagged_cards,
    }
