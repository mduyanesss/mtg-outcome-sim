"""Tests for outcome definition loading and validation."""

import pytest
from pathlib import Path
from mtg_outcome_sim.simulation.outcome import (
    load_outcomes,
    OutcomeConfig,
    OutcomeDefinition,
)


def test_load_commander_consistency():
    """Load the example Commander consistency outcomes and validate structure."""
    path = Path("examples/outcomes/commander_consistency.yaml")
    config = load_outcomes(path)
    assert config.deck_format == "commander"
    assert config.commander == "Chatterfang, Squirrel General"
    assert config.turn_limit == 6
    assert config.iterations == 100000
    assert len(config.outcomes) == 3

    # First outcome: minimum_cards_seen
    assert config.outcomes[0].name == "Hit 3 lands by turn 3"
    assert config.outcomes[0].type == "minimum_cards_seen"
    assert config.outcomes[0].tag == "lands"
    assert config.outcomes[0].minimum == 3
    assert config.outcomes[0].by_turn == 3

    # Second outcome: has_tag
    assert config.outcomes[1].name == "Ramp by turn 2"
    assert config.outcomes[1].type == "has_tag"
    assert config.outcomes[1].tag == "ramp"
    assert config.outcomes[1].minimum == 1

    # Third outcome: all_groups_present
    assert config.outcomes[2].name == "Engine online by turn 6"
    assert config.outcomes[2].type == "all_groups_present"
    assert config.outcomes[2].groups is not None
    assert len(config.outcomes[2].groups) == 3


def test_outcome_type_validation():
    """All loaded outcomes should have valid types."""
    path = Path("examples/outcomes/commander_consistency.yaml")
    config = load_outcomes(path)
    for o in config.outcomes:
        assert o.type in ("minimum_cards_seen", "has_tag", "all_groups_present")


def test_invalid_outcome_type():
    """Invalid outcome type should raise ValueError."""
    with pytest.raises(ValueError, match="Outcome type must be one of"):
        OutcomeDefinition(
            name="bad",
            type="invalid_type",
            by_turn=3,
        )


def test_by_turn_must_be_positive():
    """by_turn must be >= 1."""
    with pytest.raises(ValueError):
        OutcomeDefinition(
            name="bad turn",
            type="has_tag",
            tag="lands",
            by_turn=0,
        )


def test_minimum_must_be_positive():
    """minimum must be >= 1."""
    with pytest.raises(ValueError):
        OutcomeDefinition(
            name="bad minimum",
            type="has_tag",
            tag="lands",
            minimum=0,
            by_turn=3,
        )
