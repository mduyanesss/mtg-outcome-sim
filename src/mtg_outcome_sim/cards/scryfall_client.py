import time
import httpx
from pydantic import BaseModel

class CardData(BaseModel):
    name: str
    oracle_text: str = ""
    type_line: str = ""
    mana_cost: str = ""
    cmc: float = 0.0
    scryfall_id: str = ""
    image_url: str = ""

class ScryfallClient:
    BASE = "https://api.scryfall.com"

    def __init__(self):
        self._last_request = 0.0
        self._delay = 0.1  # 100ms between requests

    def search_card(self, name: str) -> CardData | None:
        """Fuzzy search for a card by name. Returns None if not found."""
        now = time.monotonic()
        if now - self._last_request < self._delay:
            time.sleep(self._delay - (now - self._last_request))
        try:
            r = httpx.get(
                f"{self.BASE}/cards/named",
                params={"fuzzy": name},
                timeout=10,
            )
            self._last_request = time.monotonic()
            if r.status_code == 404:
                return None
            r.raise_for_status()
            data = r.json()
            return CardData(
                name=data["name"],
                oracle_text=data.get("oracle_text", ""),
                type_line=data.get("type_line", ""),
                mana_cost=data.get("mana_cost", ""),
                cmc=float(data.get("cmc", 0)),
                scryfall_id=data.get("id", ""),
                image_url=data.get("image_uris", {}).get("normal", ""),
            )
        except Exception:
            return None
