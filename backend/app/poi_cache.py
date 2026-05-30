import json
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_KEYWORDS = ["景点", "美食", "餐厅", "博物馆", "商圈", "夜景", "公园", "咖啡"]


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


def cache_path() -> Path:
    return Path("amap_poi_cache.json")


def cache_key(city: str, keyword: str) -> str:
    return f"{city.strip()}::{keyword.strip()}"


@contextmanager
def _cache_store():
    path = cache_path()
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"entries": {}}
    yield data
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_cached_pois(city: str, keyword: str) -> list[dict[str, Any]]:
    key = cache_key(city, keyword)
    with _cache_store() as data:
        entry = data["entries"].get(key)
    if not entry:
        return []
    return entry.get("pois", [])


def set_cached_pois(city: str, keyword: str, pois: list[dict[str, Any]]) -> None:
    key = cache_key(city, keyword)
    with _cache_store() as data:
        data["entries"][key] = {
            "city": city,
            "keyword": keyword,
            "fetched_at": utcnow(),
            "count": len(pois),
            "pois": pois,
        }


def list_city_cached_pois(city: str) -> dict[str, Any]:
    normalized = city.strip()
    with _cache_store() as data:
        entries = [
            entry
            for entry in data["entries"].values()
            if entry.get("city", "").strip() == normalized
        ]
    pois_by_name: dict[str, dict[str, Any]] = {}
    keywords = []
    for entry in entries:
        keywords.append(entry.get("keyword"))
        for poi in entry.get("pois", []):
            name = str(poi.get("name") or "")
            if name and name not in pois_by_name:
                pois_by_name[name] = poi
    return {
        "city": normalized,
        "keywords": [item for item in keywords if item],
        "entry_count": len(entries),
        "poi_count": len(pois_by_name),
        "pois": list(pois_by_name.values()),
    }


def all_cached_pois_for_city(city: str) -> list[dict[str, Any]]:
    return list_city_cached_pois(city)["pois"]
