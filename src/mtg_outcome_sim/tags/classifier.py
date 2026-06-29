import re
import yaml
from pathlib import Path
from .schema import TagDefinition, CardTags, TagOverrides

_TAGS: list[TagDefinition] | None = None

def _load_tags() -> list[TagDefinition]:
    global _TAGS
    if _TAGS is not None:
        return _TAGS
    yaml_path = Path(__file__).parent / "default_tags.yaml"
    data = yaml.safe_load(yaml_path.read_text())
    _TAGS = [TagDefinition(**t) for t in data["tags"]]
    return _TAGS

def classify_card(name: str, oracle_text: str, type_line: str, overrides: dict[str, set[str]] | None = None) -> CardTags:
    """Classify a single card, returning its functional tags. Cards can have multiple tags."""
    tags = set()
    for td in _load_tags():
        for pat in td.type_line_patterns:
            if re.search(pat, type_line):
                tags.add(td.name)
                break
        for pat in td.oracle_patterns:
            if re.search(pat, oracle_text):
                tags.add(td.name)
                break
    if overrides and name in overrides:
        tags = tags | overrides[name]
    return CardTags(card_name=name, tags=tags)

def classify_cards(cards: list[tuple[str, str, str]], overrides: dict[str, set[str]] | None = None) -> list[CardTags]:
    """Classify multiple cards. cards = list of (name, oracle_text, type_line)."""
    return [classify_card(n, o, t, overrides) for n, o, t in cards]
