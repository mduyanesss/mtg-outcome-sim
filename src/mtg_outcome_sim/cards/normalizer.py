from .scryfall_client import ScryfallClient, CardData
from .mtgjson_cache import Cache

_client = ScryfallClient()
_cache = Cache()

def normalize(name: str) -> CardData | None:
    """Normalize a card name through cache then Scryfall fuzzy search."""
    cached = _cache.get(name)
    if cached:
        return CardData(**cached)

    result = _client.search_card(name)
    if result:
        _cache.put(name, result.model_dump())
    return result
