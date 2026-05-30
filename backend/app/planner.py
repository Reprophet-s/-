from typing import Any

from .local_city_data import (
    find_city_data,
    local_activities_for,
    local_activity_keywords_for,
    local_pois_for,
    local_restaurants_for,
)
from .poi_cache import get_cached_pois, set_cached_pois
from .schemas import TripCreate
from .services.ai_planner import AIPlanner
from .services.amap import AMapService
from .services.weather import AMapWeatherService


INTEREST_KEYWORDS = {
    "美食": "美食",
    "博物馆": "博物馆",
    "自然风光": "景区",
    "亲子": "亲子",
    "购物": "商圈",
    "历史文化": "历史文化",
    "夜景": "夜景",
    "咖啡": "咖啡",
    "徒步": "公园",
}

FOOD_KEYWORDS = ["餐厅", "美食", "小吃", "本地菜", "咖啡"]
ACTIVITY_INTERESTS = {"洗浴", "汗蒸", "温泉", "夜生活", "冰雪", "滑雪", "电影", "茶馆", "早茶", "夜宵"}


async def generate_plan(request: TripCreate) -> dict[str, Any]:
    weather_service = AMapWeatherService()
    amap_service = AMapService()
    planner = AIPlanner()

    weather = await weather_service.daily_forecast(request.destination, request.days)
    interests = _string_items(request.interests)
    keywords = [INTEREST_KEYWORDS.get(item, item) for item in interests] or ["景点", "美食", "博物馆"]

    pois: list[dict[str, Any]] = []
    seen_names: set[str] = set()

    for poi in local_pois_for(request.destination, interests):
        name = str(poi.get("name") or "")
        if name and name not in seen_names:
            seen_names.add(name)
            pois.append(poi)

    for restaurant in local_restaurants_for(request.destination):
        _append_or_merge_poi(pois, seen_names, restaurant)

    for activity in local_activities_for(request.destination, interests):
        _append_or_merge_poi(pois, seen_names, activity)

    await amap_service.enrich_local_pois(request.destination, pois)

    for keyword in keywords[:6]:
        for poi in await _cached_amap_search(amap_service, request.destination, keyword):
            _append_or_merge_poi(pois, seen_names, poi)

    for keyword in _food_keywords(request):
        for poi in await _cached_amap_search(amap_service, request.destination, keyword, limit=15):
            poi["category"] = "restaurant"
            _append_or_merge_poi(pois, seen_names, poi)

    for keyword in _activity_keywords(request):
        for poi in await _cached_amap_search(amap_service, request.destination, keyword, limit=10):
            poi["category"] = "activity"
            _append_or_merge_poi(pois, seen_names, poi)

    plan = await planner.generate(request, weather, pois)
    return await amap_service.enrich_plan_routes(plan)


async def _cached_amap_search(
    amap_service: AMapService,
    city: str,
    keyword: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    cached = get_cached_pois(city, keyword)
    if cached:
        return cached[:limit]
    pois = await amap_service.search_poi(city, keyword, limit=limit)
    if pois:
        set_cached_pois(city, keyword, pois)
    return pois


def _food_keywords(request: TripCreate) -> list[str]:
    city = find_city_data(request.destination) or {}
    city_foods = [str(item) for item in city.get("foods", [])]
    interest_foods = [item for item in _string_items(request.interests) if item in {"美食", "咖啡"}]
    return list(dict.fromkeys([*interest_foods, *city_foods, *FOOD_KEYWORDS]))[:8]


def _activity_keywords(request: TripCreate) -> list[str]:
    local_keywords = local_activity_keywords_for(request.destination)
    interest_keywords = [item for item in _string_items(request.interests) if item in ACTIVITY_INTERESTS]
    return list(dict.fromkeys([*interest_keywords, *local_keywords]))[:6]


def _append_or_merge_poi(pois: list[dict[str, Any]], seen_names: set[str], poi: dict[str, Any]) -> None:
    name = _safe_text(poi.get("name"))
    if name and name not in seen_names:
        seen_names.add(name)
        pois.append(poi)
    elif name:
        _merge_amap_fields(pois, name, poi)


def _merge_amap_fields(pois: list[dict[str, Any]], name: str, amap_poi: dict[str, Any]) -> None:
    for existing in pois:
        if existing.get("name") != name:
            continue
        for field in ("location", "adname", "rating", "cost", "tag", "photo_url", "typecode", "address", "category"):
            if amap_poi.get(field) and not existing.get(field):
                existing[field] = amap_poi[field]
        if existing.get("local"):
            existing["local"]["location"] = existing.get("location")
            existing["local"]["rating"] = existing.get("rating")
            if existing.get("adname") and not existing["local"].get("area"):
                existing["local"]["area"] = existing["adname"]
        return


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list | tuple | set):
        return " ".join(_safe_text(item) for item in value if _safe_text(item))
    return str(value)


def _string_items(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list | tuple | set):
        items: list[str] = []
        for item in value:
            items.extend(_string_items(item))
        return items
    return [str(value)]
