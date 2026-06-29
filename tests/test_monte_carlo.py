"""Tests for the Monte Carlo draw engine."""

from mtg_outcome_sim.simulation.monte_carlo import run_simulation, MCResult
from mtg_outcome_sim.simulation.hypergeometric import prob_at_least


def make_deck_tags(land_count=37, ramp_count=10, draw_count=10):
    """Make a deck_tags dict with specified tag counts.

    Returns a dict where keys are unique card names and values are sets of tags.
    The total will be 99 cards (Commander-sized deck).
    """
    tags = {}
    for i in range(land_count):
        tags[f"Land_{i}"] = {"lands"}
    for i in range(ramp_count):
        tags[f"Ramp_{i}"] = {"ramp"}
    for i in range(draw_count):
        tags[f"Draw_{i}"] = {"draw"}
    remaining = 99 - land_count - ramp_count - draw_count
    for i in range(remaining):
        tags[f"Other_{i}"] = set()
    return tags


def test_mc_minimum_cards_seen_single_tag():
    """MC should converge to hypergeometric for simple land draw questions."""
    deck_tags = make_deck_tags(land_count=37, ramp_count=10, draw_count=10)
    outcome = {
        "name": "3 lands by turn 3",
        "type": "minimum_cards_seen",
        "tag": "lands",
        "minimum": 3,
        "by_turn": 3,
    }
    result = run_simulation(deck_tags, outcome, iterations=100000, seed=42)
    hg = prob_at_least(99, 37, 9, 3)  # 7 opening + 2 draws by turn 3 (on play)
    assert abs(result.probability - hg) < 0.01  # Within 1%


def test_mc_has_tag():
    """has_tag outcome type works like minimum_cards_seen."""
    deck_tags = make_deck_tags(land_count=37, ramp_count=10, draw_count=10)
    outcome = {
        "name": "ramp by turn 2",
        "type": "has_tag",
        "tag": "ramp",
        "minimum": 1,
        "by_turn": 2,
    }
    result = run_simulation(deck_tags, outcome, iterations=100000, seed=42)
    hg = prob_at_least(99, 10, 8, 1)  # 7 opening + 1 draw by turn 2
    assert abs(result.probability - hg) < 0.01


def test_mc_all_groups_present():
    """all_groups_present checks that all groups have minimum cards drawn."""
    deck_tags = make_deck_tags(land_count=37, ramp_count=10, draw_count=10)
    # Tag some cards with combo roles
    deck_tags["Combo_A_0"] = {"token_maker"}
    deck_tags["Combo_A_1"] = {"token_maker"}
    deck_tags["Combo_B_0"] = {"sac_outlet"}
    deck_tags["Combo_B_1"] = {"sac_outlet"}
    deck_tags["Combo_C_0"] = {"payoff"}
    deck_tags["Combo_C_1"] = {"payoff"}
    # Remove some "Other" entries to keep at 99
    keys_to_remove = [k for k in deck_tags if k.startswith("Other_")][:6]
    for k in keys_to_remove:
        del deck_tags[k]
    # Verify total is still 99
    assert len(deck_tags) == 99

    outcome = {
        "name": "engine online by turn 6",
        "type": "all_groups_present",
        "by_turn": 6,
        "groups": [
            {"tag": "token_maker", "minimum": 1},
            {"tag": "sac_outlet", "minimum": 1},
            {"tag": "payoff", "minimum": 1},
        ],
    }
    result = run_simulation(deck_tags, outcome, iterations=100000, seed=42)
    assert 0 < result.probability < 1
    assert result.iterations == 100000


def test_mc_reproducibility():
    """Same seed + same inputs = same result."""
    deck_tags = make_deck_tags()
    outcome = {
        "name": "3 lands by turn 3",
        "type": "minimum_cards_seen",
        "tag": "lands",
        "minimum": 3,
        "by_turn": 3,
    }
    r1 = run_simulation(deck_tags, outcome, iterations=50000, seed=42)
    r2 = run_simulation(deck_tags, outcome, iterations=50000, seed=42)
    assert r1.probability == r2.probability
    assert r1.successes == r2.successes


def test_mc_different_seeds_converge():
    """Different seeds should converge to similar values at high iterations."""
    deck_tags = make_deck_tags(land_count=37)
    outcome = {
        "name": "3 lands by turn 3",
        "type": "minimum_cards_seen",
        "tag": "lands",
        "minimum": 3,
        "by_turn": 3,
    }
    results = []
    for seed in [42, 123, 456, 789]:
        r = run_simulation(deck_tags, outcome, iterations=100000, seed=seed)
        results.append(r.probability)
    # All results within 0.5% of each other
    max_diff = max(results) - min(results)
    assert max_diff < 0.005


def test_mc_empty_outcome_groups():
    """Empty groups list in all_groups_present = trivially satisfied."""
    deck_tags = make_deck_tags(land_count=10)
    outcome = {
        "name": "no groups",
        "type": "all_groups_present",
        "by_turn": 3,
        "groups": [],
    }
    result = run_simulation(deck_tags, outcome, iterations=1000, seed=42)
    assert result.probability == 1.0
