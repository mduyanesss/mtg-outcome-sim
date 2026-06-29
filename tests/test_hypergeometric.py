"""Tests for the hypergeometric probability calculator."""

from mtg_outcome_sim.simulation.hypergeometric import (
    prob_at_least,
    prob_exact,
    opening_hand_distribution,
    lands_by_turn,
)


def test_prob_at_least_one_land_opening():
    """37 lands in 99-card deck, 7-card opener: P(>=1 land) should be very high."""
    p = prob_at_least(99, 37, 7, 1)
    assert p > 0.90  # Should be ~96%


def test_prob_at_least_three_lands_opening():
    """P(>=3 lands in opening 7) with 37 lands in 99-card deck."""
    p = prob_at_least(99, 37, 7, 3)
    assert 0.30 < p < 0.60  # Should be ~44%


def test_prob_exact_two_lands():
    """P(exactly 2 lands in opening 7)."""
    p = prob_exact(99, 37, 7, 2)
    assert 0.20 < p < 0.35  # Should be ~27%


def test_prob_at_least_zero_always_1():
    """P(>=0) is always 1.0."""
    assert prob_at_least(99, 37, 7, 0) == 1.0


def test_prob_at_least_impossible():
    """Cannot draw 10 success cards when only 5 exist in deck."""
    assert prob_at_least(99, 5, 7, 10) == 0.0


def test_prob_at_least_minimum_exceeds_draws():
    """P(>=8 lands in 7-card hand) = 0."""
    assert prob_at_least(99, 37, 7, 8) == 0.0


def test_prob_exact_extreme():
    """P(exactly 0 lands in 7-card hand from 99/37 deck)."""
    p = prob_exact(99, 37, 7, 0)
    assert 0.02 < p < 0.10  # Should be ~4%


def test_opening_hand_distribution_sums_to_1():
    """The full probability distribution must sum to 1."""
    dist = opening_hand_distribution(99, 37, 7)
    total = sum(dist.values())
    assert abs(total - 1.0) < 0.001


def test_lands_by_turn_3():
    """P(>=3 lands by turn 3) with 37 lands in 99-card deck."""
    # Draws = 7 opening + 2 natural draws = 9 (turn 3, on the play)
    p = prob_at_least(99, 37, 9, 3)
    assert 0.65 < p < 0.90  # Should be ~82%


def test_lands_by_turn_function():
    """lands_by_turn returns reasonable distribution."""
    dist = lands_by_turn(99, 37, 3, on_draw=False)
    assert len(dist) > 0
    total = sum(p for _, p in dist)
    assert abs(total - 1.0) < 0.001


def test_lands_by_turn_on_draw_extra_card():
    """on_draw=True adds one extra card."""
    dist_play = lands_by_turn(99, 37, 3, on_draw=False)
    dist_draw = lands_by_turn(99, 37, 3, on_draw=True)
    # on_draw draws one more, so max possible lands is one higher
    max_play = max(k for k, _ in dist_play)
    max_draw = max(k for k, _ in dist_draw)
    assert max_draw == max_play + 1


def test_prob_exact_negative_count():
    """Exact count < 0 -> 0."""
    assert prob_exact(99, 37, 7, -1) == 0.0
