"""Monte Carlo draw simulation for MTG outcome questions.

Uses random.Random with a fixed seed for reproducibility.
No mulligan decisions in MVP — always keep opener of 7.
On-the-play draw count: draws = 7 + (turn - 1).
"""

import random
from dataclasses import dataclass
from typing import Any


@dataclass
class MCResult:
    """Result of a single Monte Carlo simulation run."""

    probability: float
    iterations: int
    successes: int


def run_simulation(
    deck_tags: dict[str, set[str]],
    outcome_def: dict[str, Any],
    iterations: int = 100_000,
    seed: int | None = 42,
) -> MCResult:
    """Run Monte Carlo draw simulation for a single outcome question.

    Args:
        deck_tags: Mapping of card_name -> set of tag strings.
        outcome_def: Outcome definition dict with keys:
            - name (str): Human-readable name.
            - type (str): "minimum_cards_seen", "has_tag", or "all_groups_present".
            - tag (str | None): Target tag for single-tag outcomes.
            - minimum (int): Minimum number of tagged cards required.
            - by_turn (int): Turn number by which the condition must be met.
            - groups (list[dict] | None): List of {"tag": str, "minimum": int}
              for all_groups_present outcomes.
        iterations: Number of Monte Carlo trials.
        seed: Random seed for reproducibility (None for non-reproducible).

    Returns:
        MCResult with probability, iteration count, and success count.
    """
    rng = random.Random(seed)

    # Build the deck as a list of (name, tags) tuples.
    deck: list[tuple[str, set[str]]] = list(deck_tags.items())

    outcome_type = outcome_def["type"]
    by_turn = outcome_def["by_turn"]

    # Total draws = 7 opening + (turn - 1) natural draws (on the play).
    draws = 7 + (by_turn - 1)

    success_count = 0

    if outcome_type in ("minimum_cards_seen", "has_tag"):
        tag = outcome_def["tag"]
        minimum = outcome_def.get("minimum", 1)

        for _ in range(iterations):
            rng.shuffle(deck)
            # Draw the top `draws` cards.
            drawn = deck[:draws]
            # Count how many have the target tag.
            count = sum(1 for _, tags in drawn if tag in tags)
            if count >= minimum:
                success_count += 1

    elif outcome_type == "all_groups_present":
        groups = outcome_def.get("groups", [])
        if not groups:
            # No groups means trivially satisfied.
            return MCResult(probability=1.0, iterations=iterations, successes=iterations)

        for _ in range(iterations):
            rng.shuffle(deck)
            drawn = deck[:draws]
            # Get all drawn tags in a flat set for fast membership.
            drawn_tags: set[str] = set()
            for _, tags in drawn:
                drawn_tags.update(tags)

            # Every group must have at least one drawn card with its tag.
            all_present = True
            for group in groups:
                group_tag = group["tag"]
                group_min = group.get("minimum", 1)
                count = sum(1 for _, tags in drawn if group_tag in tags)
                if count < group_min:
                    all_present = False
                    break

            if all_present:
                success_count += 1

    probability = success_count / iterations if iterations > 0 else 0.0
    return MCResult(
        probability=probability, iterations=iterations, successes=success_count
    )


def run_all_outcomes(
    deck_tags: dict[str, set[str]],
    outcome_defs: list[dict[str, Any]],
    iterations: int = 100_000,
    seed: int | None = 42,
) -> list[MCResult]:
    """Run Monte Carlo simulations for all outcome definitions.

    Args:
        deck_tags: Mapping of card_name -> set of tag strings.
        outcome_defs: List of outcome definition dicts.
        iterations: Number of trials per outcome.
        seed: Random seed (shared across outcomes for comparability).

    Returns:
        List of MCResult, one per outcome definition.
    """
    results: list[MCResult] = []
    for outcome_def in outcome_defs:
        result = run_simulation(deck_tags, outcome_def, iterations, seed)
        results.append(result)
    return results
