from mtg_outcome_sim.simulation.mana_model import (
    simulate_mana_curve_mc,
    expected_mana_by_turn,
)


def test_mana_curve_basic():
    result = simulate_mana_curve_mc(
        deck_size=99, land_count=37, ramp_count=10, max_turns=6, iterations=5000, seed=42
    )
    assert len(result) == 6
    # Turn 1: ~1-2 mana (land drop + any ramp in opening hand)
    assert 0.5 < result[0]["mean_mana"] < 2.5
    # Turn 6: more mana than turn 1
    assert result[5]["mean_mana"] > result[0]["mean_mana"]
    # Should not exceed ~12 (max one land per turn + ramp + variance)
    assert result[5]["mean_mana"] < 14


def test_mana_curve_no_ramp():
    result = simulate_mana_curve_mc(
        deck_size=99, land_count=37, ramp_count=0, max_turns=6, iterations=5000, seed=42
    )
    # Without ramp, mana is approximately 1 per turn (capped by land drops)
    for t in range(1, 7):
        assert result[t - 1]["mean_mana"] <= t + 1  # at most t lands + 1 for variance


def test_mana_curve_deterministic():
    r1 = simulate_mana_curve_mc(seed=42)
    r2 = simulate_mana_curve_mc(seed=42)
    for a, b in zip(r1, r2):
        assert a["mean_mana"] == b["mean_mana"]


def test_expected_mana_by_turn():
    # At turn 3 with 37 lands in 99-card deck
    m = expected_mana_by_turn(deck_size=99, land_count=37, ramp_count=0, turn=3)
    # ~7+2=9 draws, 37/99 * 9 ≈ 3.36 expected lands drawn, capped at 3 played
    assert 2.0 < m < 5.0


def test_mana_curve_includes_all_keys():
    result = simulate_mana_curve_mc(max_turns=3, iterations=100, seed=1)
    for row in result:
        for key in ("turn", "mean_mana", "median_mana", "p10_mana", "p90_mana"):
            assert key in row


def test_mana_curve_raises_on_invalid_input():
    """land_count + ramp_count > deck_size should raise ValueError."""
    try:
        simulate_mana_curve_mc(deck_size=99, land_count=60, ramp_count=50)
        assert False, "Expected ValueError"
    except ValueError:
        pass
