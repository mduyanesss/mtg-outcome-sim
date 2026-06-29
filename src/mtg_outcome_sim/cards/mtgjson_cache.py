import json
from pathlib import Path

class Cache:
    def __init__(self, cache_dir: str | None = None):
        if cache_dir is None:
            cache_dir = Path.home() / ".mtg-outcome-sim" / "cache"
        self._dir = Path(cache_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _key(self, name: str) -> str:
        return name.lower().replace(" ", "_").replace(",", "").replace("'", "")

    def get(self, name: str) -> dict | None:
        p = self._dir / f"{self._key(name)}.json"
        if p.exists():
            return json.loads(p.read_text())
        return None

    def put(self, name: str, data: dict):
        p = self._dir / f"{self._key(name)}.json"
        p.write_text(json.dumps(data, indent=2))

    def has(self, name: str) -> bool:
        return (self._dir / f"{self._key(name)}.json").exists()
