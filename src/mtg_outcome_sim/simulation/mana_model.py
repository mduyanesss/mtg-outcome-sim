"""Lightweight mana curve model: Monte Carlo simulation of land drops + ramp.

This is a probabilistic approximation, NOT a rules engine. It does not resolve
the stack, track colors, or model opponent interaction.
"""

import random


def expected_mana_by_turn(
    deck_size: int = 99,
    land_count: int = 37,
    ramp_count: int = 10,
    turn: int = 3,
    on_draw: bool = False,
) -> float:
    """Expected mana available by a given turn (closed-form approximation).

    - Lands: expected count drawn, capped at 1 per turn played
    - Ramp: expected count drawn, each producing +1 mana
    - Commander tax: ignored in MVP
    """
    draws = 7 + (turn - 1) + (1 if on_draw else 0)
    draw_fraction = min(draws / deck_size, 1.0)
    expected_lands_drawn = land_count * draw_fraction
    expected_lands_played = min(float(turn), expected_lands_drawn)
    expected_ramp = ramp_count * draw_fraction
    return expected_lands_played + expected_ramp


def simulate_mana_curve_mc(
    deck_size: int = 99,
    land_count: int = 37,
    ramp_count: int = 10,
    max_turns: int = 10,
    iterations: int = 10000,
    seed: int | None = 42,
) -> list[dict]:
    """Monte Carlo mana curve simulation.

    Each iteration shuffles a simplified deck of "land", "ramp", and "other"
    cards, draws an opening 7, then for each turn draws 1, plays a land if
    available, and plays any ramp drawn. Ramp adds +1 ongoing mana per card.

    Returns a list of dicts, one per turn, with keys:
        turn, mean_mana, median_mana, p10_mana, p90_mana
    """
    if land_count + ramp_count > deck_size:
        raise ValueError(
            f"land_count ({land_count}) + ramp_count ({ramp_count}) "
            f"must not exceed deck_size ({deck_size})"
        )

    rng = random.Random(seed)

    results_by_turn: dict[int, list[int]] = {t: [] for t in range(1, max_turns + 1)}

    for _ in range(iterations):
        deck = (
            ["land"] * land_count
            + ["ramp"] * ramp_count
            + ["other"] * (deck_size - land_count - ramp_count)
        )
        rng.shuffle(deck)

        hand: list[str] = deck[:7]
        library_idx = 7

        lands_played = 0
        extra_mana = 0  # ongoing mana from ramp

        for turn in range(1, max_turns + 1):
            # Draw for turn (skip turn 1 on the play; we simplify to always draw)
            if turn > 1 and library_idx < len(deck):
                hand.append(deck[library_idx])
                library_idx += 1

            # Play a land if possible
            if "land" in hand:
                hand.remove("land")
                lands_played += 1

            # Play all available ramp (simplified: no mana cost to cast ramp)
            while "ramp" in hand:
                hand.remove("ramp")
                extra_mana += 1

            mana = lands_played + extra_mana
            results_by_turn[turn].append(mana)

    # Compute statistics per turn
    output: list[dict] = []
    for turn in range(1, max_turns + 1):
        values = sorted(results_by_turn[turn])
        n = len(values)
        output.append(
            {
                "turn": turn,
                "mean_mana": sum(values) / n,
                "median_mana": values[n // 2],
                "p10_mana": values[n // 10],
                "p90_mana": values[9 * n // 10],
            }
        )

    return output
