"""Outcome definition loader with Pydantic validation."""

import yaml
from pathlib import Path
from pydantic import BaseModel, field_validator


class OutcomeDefinition(BaseModel):
    """A single outcome question to simulate."""

    name: str
    type: str  # "minimum_cards_seen", "has_tag", "all_groups_present"
    tag: str | None = None
    minimum: int = 1
    by_turn: int
    groups: list[dict] | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = {"minimum_cards_seen", "has_tag", "all_groups_present"}
        if v not in allowed:
            raise ValueError(
                f"Outcome type must be one of {allowed}, got '{v}'"
            )
        return v

    @field_validator("by_turn")
    @classmethod
    def validate_by_turn(cls, v: int) -> int:
        if v < 1:
            raise ValueError(f"by_turn must be >= 1, got {v}")
        return v

    @field_validator("minimum")
    @classmethod
    def validate_minimum(cls, v: int) -> int:
        if v < 1:
            raise ValueError(f"minimum must be >= 1, got {v}")
        return v


class OutcomeConfig(BaseModel):
    """Top-level configuration for a set of outcome simulations."""

    deck_format: str
    commander: str
    turn_limit: int
    iterations: int
    outcomes: list[OutcomeDefinition]


def load_outcomes(path: Path) -> OutcomeConfig:
    """Load outcome definitions from a YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        An OutcomeConfig with validated outcome definitions.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the YAML is malformed or validation fails.
    """
    data = yaml.safe_load(path.read_text())
    return OutcomeConfig(**data)
