"""Exact hypergeometric probability calculations for MTG draw questions.

Uses scipy.stats.hypergeom for the underlying distribution.
Assumes drawing without replacement from a finite deck.
"""

from scipy.stats import hypergeom


def prob_at_least(
    population: int, successes: int, draws: int, minimum: int
) -> float:
    """Probability of drawing at least `minimum` success cards in `draws` draws.

    P(X >= minimum) = sf(minimum - 1) where sf is the survival function.

    Args:
        population: Total cards in deck (e.g. 99 for Commander).
        successes: Number of cards in deck that have the target tag.
        draws: Number of cards drawn (opening 7 + natural draws + extra).
        minimum: Minimum number of success cards wanted.

    Returns:
        Probability in [0.0, 1.0].

    Edge cases:
        minimum <= 0  -> 1.0 (zero or fewer is always satisfied)
        minimum > draws  -> 0.0 (cannot draw more than drawn)
        minimum > successes -> 0.0 (not enough in deck)
        draws > population -> draws clamped to population
    """
    if minimum <= 0:
        return 1.0
    if minimum > draws or minimum > successes:
        return 0.0
    if draws > population:
        draws = population

    # P(X >= minimum) = sf(minimum - 1)
    return float(hypergeom.sf(minimum - 1, population, successes, draws))


def prob_exact(
    population: int, successes: int, draws: int, count: int
) -> float:
    """Probability of drawing exactly `count` success cards.

    Args:
        population: Total cards in deck.
        successes: Number of cards in deck that have the target tag.
        draws: Number of cards drawn.
        count: Exact number of success cards wanted.

    Returns:
        Probability in [0.0, 1.0].
    """
    if count < 0:
        return 0.0
    if count > draws or count > successes or count > population:
        return 0.0
    if draws > population:
        draws = population

    return float(hypergeom.pmf(count, population, successes, draws))


def opening_hand_distribution(
    deck_size: int, land_count: int, draw_size: int = 7
) -> dict[int, float]:
    """Probability distribution for number of lands in an opening hand.

    Args:
        deck_size: Total cards in deck.
        land_count: Number of lands in the deck.
        draw_size: Cards drawn for opening hand (default 7).

    Returns:
        Dict mapping land_count -> probability.
    """
    dist = {}
    for k in range(draw_size + 1):
        p = prob_exact(deck_size, land_count, draw_size, k)
        if p > 0:
            dist[k] = p
    return dist


def lands_by_turn(
    deck_size: int, land_count: int, turn: int, on_draw: bool = False
) -> list[tuple[int, float]]:
    """Probability distribution of land counts by turn T.

    Draws = 7 (opening) + (turn - 1) natural draws (+ 1 if on the draw).

    Args:
        deck_size: Total cards in deck.
        land_count: Number of lands in the deck.
        turn: Which turn to evaluate (1-indexed).
        on_draw: If True, add one extra card (the player went second).

    Returns:
        List of (land_count, probability) for each possible land count.
    """
    draws = 7 + (turn - 1)
    if on_draw:
        draws += 1
    if draws > deck_size:
        draws = deck_size

    results = []
    for k in range(draws + 1):
        p = prob_exact(deck_size, land_count, draws, k)
        if p > 0:
            results.append((k, p))
    return results
