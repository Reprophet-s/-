from typing import Any

import httpx

from ..config import get_settings


class AMapService:
    base_url = "https://restapi.amap.com/v3"

    def __init__(self) -> None:
        self.key = get_settings().amap_key

    async def search_poi(self, city: str, keyword: str, limit: int = 20) -> list[dict[str, Any]]:
        if not self.key:
            return []
        params = {
            "key": self.key,
            "city": city,
            "keywords": keyword,
            "offset": min(max(limit, 1), 25),
            "page": 1,
            "extensions": "all",
            "children": 0,
            "citylimit": "false",
        }
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                response = await client.get(f"{self.base_url}/place/text", params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError:
            return []
        if data.get("status") != "1":
            return []
        return [self._normalize_poi(poi, keyword) for poi in data.get("pois", [])]

    async def find_best_poi(self, city: str, name: str) -> dict[str, Any] | None:
        candidates = await self.search_poi(city, name, limit=8)
        if not candidates:
            return None
        exact = [poi for poi in candidates if poi.get("name") == name]
        if exact:
            return exact[0]
        contains = [poi for poi in candidates if name in str(poi.get("name") or "")]
        if contains:
            return contains[0]
        return candidates[0]

    async def enrich_local_pois(self, city: str, pois: list[dict[str, Any]], max_items: int = 10) -> None:
        if not self.key:
            return
        for poi in pois[:max_items]:
            name = str(poi.get("name") or "")
            if not name or poi.get("location"):
                continue
            amap_poi = await self.find_best_poi(city, name)
            if not amap_poi:
                continue
            for field in ("location", "adname", "rating", "cost", "tag", "photo_url", "typecode"):
                if amap_poi.get(field) and not poi.get(field):
                    poi[field] = amap_poi[field]
            if poi.get("local"):
                for field in ("location", "rating", "photo_url"):
                    if poi.get(field):
                        poi["local"][field] = poi[field]
                if poi.get("adname"):
                    poi["local"]["area"] = poi.get("local", {}).get("area") or poi["adname"]

    async def route_duration_minutes(self, origin: str, destination: str, mode: str = "driving") -> int | None:
        if not self.key or not origin or not destination:
            return None
        endpoint = "direction/driving" if mode == "driving" else "direction/walking"
        params = {"key": self.key, "origin": origin, "destination": destination}
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                response = await client.get(f"{self.base_url}/{endpoint}", params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError:
            return None
        paths = data.get("route", {}).get("paths", [])
        if not paths:
            return None
        try:
            seconds = int(paths[0].get("duration", 0))
        except (TypeError, ValueError):
            return None
        return max(1, round(seconds / 60))

    async def enrich_plan_routes(self, plan: dict[str, Any]) -> dict[str, Any]:
        if not self.key:
            return plan
        for day in plan.get("days", []):
            previous_location = ""
            previous_place = ""
            for item in day.get("items", []):
                location = item.get("location") or ""
                if previous_location and location:
                    mode = "walking" if item.get("type") in {"food", "shopping"} else "driving"
                    minutes = await self.route_duration_minutes(previous_location, location, mode=mode)
                    if minutes:
                        mode_label = "步行" if mode == "walking" else "驾车/打车"
                        item["route_info"] = f"从{previous_place}到这里约{minutes}分钟（{mode_label}估算）"
                if location:
                    previous_location = location
                    previous_place = item.get("place") or item.get("title") or "上一站"
        return plan

    def _normalize_poi(self, poi: dict[str, Any], keyword: str) -> dict[str, Any]:
        biz_ext = poi.get("biz_ext") if isinstance(poi.get("biz_ext"), dict) else {}
        photos = poi.get("photos") if isinstance(poi.get("photos"), list) else []
        return {
            "name": poi.get("name"),
            "type": poi.get("type"),
            "typecode": poi.get("typecode"),
            "address": poi.get("address"),
            "location": poi.get("location"),
            "pname": poi.get("pname"),
            "cityname": poi.get("cityname"),
            "adname": poi.get("adname"),
            "rating": self._clean_empty(biz_ext.get("rating")),
            "cost": self._clean_empty(biz_ext.get("cost")),
            "tag": poi.get("tag"),
            "photo_url": photos[0].get("url") if photos and isinstance(photos[0], dict) else None,
            "source": "amap",
            "keyword": keyword,
        }

    def _clean_empty(self, value: Any) -> Any:
        if value is None or value == "" or value == "[]":
            return None
        if isinstance(value, list | tuple | dict | set) and not value:
            return None
        return value
