import re
import yaml
from pathlib import Path
from .schema import TagDefinition, CardTags, TagOverrides

_TAGS: list[TagDefinition] | None = None

# Ramp-effect patterns that justify the ramp tag even on lands (fetchlands, etc.).
# These match land-searching and land-putting effects, NOT basic mana abilities.
# Since these are only checked for cards already tagged as "lands", we can use
# broader patterns that catch named land types (Forest, Swamp, etc.).
_LAND_RAMP_PATTERNS = [
    re.compile(r"(?i)search your library for (?:a |an |basic )"),  # fetchland / land tutor
    re.compile(r"(?i)put (?:it|them|that) onto the battlefield"),  # put fetched land into play
]


def _load_tags() -> list[TagDefinition]:
    global _TAGS
    if _TAGS is not None:
        return _TAGS
    yaml_path = Path(__file__).parent / "default_tags.yaml"
    data = yaml.safe_load(yaml_path.read_text())
    _TAGS = [TagDefinition(**t) for t in data["tags"]]
    return _TAGS


def classify_card(
    name: str,
    oracle_text: str,
    type_line: str,
    overrides: dict[str, set[str]] | None = None,
) -> CardTags:
    """Classify a single card, returning its functional tags. Cards can have multiple tags."""
    tags: set[str] = set()
    for td in _load_tags():
        for pat in td.type_line_patterns:
            if re.search(pat, type_line):
                tags.add(td.name)
                break
        for pat in td.oracle_patterns:
            if re.search(pat, oracle_text):
                tags.add(td.name)
                break

    # Apply exclude_if_tags: remove a tag if the card already has one of the excluded tags.
    # Example: ramp exclude_if_tags ["lands"] removes ramp from basic lands that
    # matched via the "add {.*}" mana-ability pattern.
    for td in _load_tags():
        if td.exclude_if_tags and td.name in tags:
            if any(excluded in tags for excluded in td.exclude_if_tags):
                tags.discard(td.name)

    # Re-add ramp for lands that have true ramp effects (fetchlands, land-putting spells).
    if "lands" in tags and "ramp" not in tags:
        for pat in _LAND_RAMP_PATTERNS:
            if pat.search(oracle_text):
                tags.add("ramp")
                break

    if overrides and name in overrides:
        tags = tags | overrides[name]
    return CardTags(card_name=name, tags=tags)

def classify_cards(cards: list[tuple[str, str, str]], overrides: dict[str, set[str]] | None = None) -> list[CardTags]:
    """Classify multiple cards. cards = list of (name, oracle_text, type_line)."""
    return [classify_card(n, o, t, overrides) for n, o, t in cards]
