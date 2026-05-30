import json
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import quote

import httpx

from ..config import get_settings
from ..local_city_data import find_city_data
from ..schemas import TravelPace, TripCreate


PACE_LABELS = {
    TravelPace.relaxed: "轻松",
    TravelPace.balanced: "均衡",
    TravelPace.packed: "充实",
}


class AIPlanner:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate(
        self,
        request: TripCreate,
        weather: list[dict[str, Any]],
        pois: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not self.settings.openai_api_key:
            return self._fallback_plan(request, weather, pois)

        prompt = self._build_prompt(request, weather, pois)
        payload = {
            "model": self.settings.openai_model,
            "input": prompt,
            "text": {"format": {"type": "json_object"}},
        }
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers={
                        "Authorization": f"Bearer {self.settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            plan = self._fallback_plan(request, weather, pois)
            plan["ai_error"] = str(exc)
            return plan

        text = data.get("output_text") or self._extract_output_text(data)
        try:
            plan = json.loads(text)
        except json.JSONDecodeError:
            plan = self._fallback_plan(request, weather, pois)
            plan["ai_raw_text"] = text
        return self._normalize_plan(plan, request, weather)

    def _build_prompt(self, request: TripCreate, weather: list[dict[str, Any]], pois: list[dict[str, Any]]) -> str:
        city_data = find_city_data(request.destination)
        return json.dumps(
            {
                "task": "Generate a complete Chinese travel itinerary as strict JSON.",
                "schema": {
                    "destination": "string",
                    "summary": "string",
                    "weather_advice": ["string"],
                    "budget_summary": {
                        "total_estimated_cny": 0,
                        "food_cny": 0,
                        "transport_cny": 0,
                        "tickets_cny": 0,
                        "notes": "string",
                    },
                    "days": [
                        {
                            "day": 1,
                            "date": "YYYY-MM-DD",
                            "theme": "string",
                            "weather": "string",
                            "items": [
                                {
                                    "time": "HH:mm",
                                    "type": "attraction|food|transfer|rest|shopping",
                                    "title": "string",
                                    "place": "string",
                                    "address": "string",
                                    "rating": "string",
                                    "restaurant_cost_cny": 0,
                                    "duration_minutes": 90,
                                    "transport": "string",
                                    "estimated_cost_cny": 0,
                                    "reason": "string",
                                    "backup": "string",
                                }
                            ],
                        }
                    ],
                },
                "constraints": {
                    "language": "zh-CN",
                    "avoid_fake_specific_prices": True,
                    "prefer_weather_aware_plan": True,
                    "group_places_by_nearby_area": True,
                    "pace": request.pace.value,
                    "hotel_address": request.hotel_address,
                    "avoid": request.avoid,
                    "notes": request.notes,
                },
                "trip_request": request.model_dump(mode="json"),
                "city_profile": city_data,
                "weather": weather,
                "candidate_pois": [
                    {
                        "name": poi.get("name"),
                        "type": poi.get("type"),
                        "address": poi.get("address"),
                        "location": poi.get("location"),
                        "adname": poi.get("adname"),
                        "rating": poi.get("rating"),
                        "cost": poi.get("cost"),
                        "tag": poi.get("tag"),
                        "category": poi.get("category"),
                        "photo_url": poi.get("photo_url"),
                        "local": poi.get("local"),
                    }
                    for poi in pois[:50]
                ],
            },
            ensure_ascii=False,
        )

    def _extract_output_text(self, data: dict[str, Any]) -> str:
        chunks: list[str] = []
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"}:
                    chunks.append(content.get("text", ""))
        return "".join(chunks)

    def _fallback_plan(
        self,
        request: TripCreate,
        weather: list[dict[str, Any]],
        pois: list[dict[str, Any]],
    ) -> dict[str, Any]:
        city_data = find_city_data(request.destination)
        local_pois = [poi.get("local") for poi in pois if poi.get("local")]
        amap_pois = [poi for poi in pois if poi.get("source") == "amap"]
        restaurants = self._restaurant_pois(pois, city_data)
        activities = self._activity_pois(pois)
        attraction_amap_pois = [poi for poi in amap_pois if not self._is_restaurant_poi(poi)]
        if not local_pois:
            local_pois = self._generic_local_pois(attraction_amap_pois or pois)
        elif attraction_amap_pois:
            known_names = {self._safe_text(poi.get("name")) for poi in local_pois}
            local_pois.extend(
                poi for poi in self._generic_local_pois(attraction_amap_pois) if self._safe_text(poi.get("name")) not in known_names
            )

        pace_label = PACE_LABELS[request.pace]
        days = []
        daily_budget = self._daily_budget(request)
        rainy_backups = self._rainy_backups(city_data)
        foods = self._foods(city_data)
        used_restaurant_names: set[str] = set()

        for index in range(request.days):
            current_date = request.start_date + timedelta(days=index)
            day_weather = weather[index] if index < len(weather) else {}
            weather_text = self._weather_text(day_weather)
            rainy = self._is_rainy(day_weather)
            hot = self._is_hot(day_weather)
            day_pois = self._pois_for_day(local_pois, index, request.pace)

            morning_poi = self._weather_fit_poi(day_pois, rainy, hot, 0)
            afternoon_poi = self._weather_fit_poi(day_pois, rainy or hot, hot, 1)
            evening_poi = self._evening_poi(local_pois, index)
            lunch_food = foods[index % len(foods)]
            dinner_food = foods[(index + 2) % len(foods)]
            lunch_restaurant = self._restaurant_for_meal(restaurants, index * 2, morning_poi, used_restaurant_names)
            used_restaurant_names.add(str(lunch_restaurant.get("name")))
            dinner_restaurant = self._restaurant_for_meal(restaurants, index * 2 + 1, evening_poi, used_restaurant_names)
            used_restaurant_names.add(str(dinner_restaurant.get("name")))
            activity = self._activity_for_day(activities, index)

            items = [
                self._attraction_item(
                    time="09:30",
                    title="上午核心游览",
                    poi=morning_poi,
                    cost=max(30, round(daily_budget * 0.18)),
                    reason_suffix="上午体力较好，适合安排当天最重要的体验。",
                    backup=self._backup(rainy_backups, index),
                ),
                self._food_item(
                    time="12:30",
                    title=f"午餐：{lunch_food}",
                    restaurant=lunch_restaurant,
                    nearby=morning_poi,
                    cost=max(50, round(daily_budget * 0.22)),
                    food_name=lunch_food,
                ),
                self._attraction_item(
                    time="14:30",
                    title="下午深度体验",
                    poi=afternoon_poi,
                    cost=max(40, round(daily_budget * 0.2)),
                    reason_suffix="下午安排同区域或室内友好点，减少折返和天气影响。",
                    backup=self._backup(rainy_backups, index + 1),
                ),
                self._food_item(
                    time="18:30",
                    title=f"晚餐与夜间活动：{dinner_food}",
                    restaurant=dinner_restaurant,
                    nearby=evening_poi,
                    cost=max(70, round(daily_budget * 0.24)),
                    food_name=dinner_food,
                    backup=self._backup(rainy_backups, index + 2),
                ),
            ]
            if activity:
                items.append(
                    self._activity_item(
                        time="20:30",
                        activity=activity,
                        cost=max(60, round(daily_budget * 0.16)),
                    )
                )
            if request.pace == TravelPace.relaxed:
                items = items[:3] if not activity else [*items[:3], items[-1]]
            elif request.pace == TravelPace.packed:
                extra_poi = day_pois[2 % len(day_pois)]
                items.insert(
                    3,
                    self._attraction_item(
                        time="16:45",
                        title="顺路加一站",
                        poi=extra_poi,
                        cost=max(30, round(daily_budget * 0.1)),
                        reason_suffix="充实节奏下增加一个轻量点，但不打乱当天主线。",
                        backup="体力不足时直接跳过，提前晚餐。",
                    ),
                )

            days.append(
                {
                    "day": index + 1,
                    "date": current_date.isoformat(),
                    "theme": self._theme(index, rainy, request, city_data),
                    "weather": weather_text,
                    "weather_detail": self._weather_detail(day_weather),
                    "items": items,
                }
            )

        plan = {
            "destination": city_data["name"] if city_data else request.destination,
            "summary": f"{request.days} 天{request.destination}{pace_label}旅行计划",
            "weather_advice": self._weather_advice(weather, request.days, city_data),
            "budget_summary": self._budget_summary(request, days),
            "city_profile": city_data.get("profile") if city_data else None,
            "days": days,
        }
        return self._normalize_plan(plan, request, weather)

    def _generic_local_pois(self, pois: list[dict[str, Any]]) -> list[dict[str, Any]]:
        source_pois = [poi for poi in pois if poi.get("name")]
        if not source_pois:
            source_pois = [
                {"name": "城市地标景区", "type": "综合推荐", "cost": 60},
                {"name": "本地博物馆", "type": "博物馆", "cost": 40},
                {"name": "特色街区", "type": "街区", "cost": 80},
                {"name": "城市公园", "type": "公园", "cost": 20},
                {"name": "美食街区", "type": "美食", "cost": 90},
            ]
        return [
            {
                "name": name,
                "type": "综合推荐",
                "area": poi.get("adname") or poi.get("address") or "目的地附近",
                "tags": [],
                "indoor": index == 1,
                "cost": self._safe_int(poi.get("cost"), 60),
                "duration": 120,
                "location": poi.get("location"),
                "amap_url": self._amap_url(name, poi.get("location"), poi.get("address") or poi.get("adname")),
                "rating": poi.get("rating"),
                "photo_url": poi.get("photo_url"),
                "reason": self._amap_reason(poi),
            }
            for index, poi in enumerate(source_pois[:12])
            if (name := str(poi.get("name") or ""))
        ]

    def _pois_for_day(self, pois: list[dict[str, Any]], day_index: int, pace: TravelPace) -> list[dict[str, Any]]:
        count = 4 if pace == TravelPace.packed else 3
        return [pois[(day_index * 2 + offset) % len(pois)] for offset in range(count)]

    def _weather_fit_poi(
        self,
        pois: list[dict[str, Any]],
        prefer_indoor: bool,
        hot: bool,
        fallback_index: int,
    ) -> dict[str, Any]:
        if prefer_indoor:
            for poi in pois:
                if poi.get("indoor"):
                    return poi
        if hot:
            for poi in pois:
                if poi.get("indoor") or "咖啡" in self._string_items(poi.get("tags", [])):
                    return poi
        return pois[fallback_index % len(pois)]

    def _evening_poi(self, pois: list[dict[str, Any]], day_index: int) -> dict[str, Any]:
        for offset in range(len(pois)):
            poi = pois[(day_index + offset) % len(pois)]
            tags = set(self._string_items(poi.get("tags", [])))
            if tags.intersection({"夜景", "美食", "购物", "咖啡"}):
                return poi
        return pois[day_index % len(pois)]

    def _restaurant_pois(
        self,
        pois: list[dict[str, Any]],
        city_data: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        restaurants = [self._normalize_restaurant(poi) for poi in pois if self._is_restaurant_poi(poi)]
        if restaurants:
            return restaurants
        return []

    def _activity_pois(self, pois: list[dict[str, Any]]) -> list[dict[str, Any]]:
        activities = [self._normalize_activity(poi) for poi in pois if self._is_activity_poi(poi)]
        seen: set[str] = set()
        unique = []
        for activity in activities:
            name = self._safe_text(activity.get("name"))
            if name and name not in seen:
                seen.add(name)
                unique.append(activity)
        return unique

    def _is_activity_poi(self, poi: dict[str, Any]) -> bool:
        if poi.get("category") == "activity" or poi.get("local_activity"):
            return True
        if poi.get("source") != "amap":
            return False
        text = f"{poi.get('type', '')}{poi.get('tag', '')}{poi.get('keyword', '')}{poi.get('name', '')}"
        return any(word in text for word in ["洗浴", "汗蒸", "温泉", "滑雪", "冰雪", "电影", "茶馆", "剧场", "演出", "夜宵"])

    def _normalize_activity(self, poi: dict[str, Any]) -> dict[str, Any]:
        local = poi.get("local_activity") or {}
        return {
            "name": poi.get("name") or local.get("name") or "本地特色活动",
            "type": poi.get("type") or local.get("type") or "特色活动",
            "address": poi.get("address") or local.get("area"),
            "area": poi.get("adname") or local.get("area") or poi.get("address") or "目的地附近",
            "location": poi.get("location"),
            "rating": poi.get("rating"),
            "photo_url": poi.get("photo_url"),
            "cost": self._safe_int(poi.get("cost") or local.get("cost"), 100),
            "duration": local.get("duration", 120),
            "reason": poi.get("reason") or local.get("reason") or self._activity_reason(poi),
            "amap_url": self._amap_url(poi.get("name") or local.get("name"), poi.get("location"), poi.get("address") or local.get("area")),
        }

    def _activity_for_day(self, activities: list[dict[str, Any]], index: int) -> dict[str, Any] | None:
        if not activities:
            return None
        return activities[index % len(activities)]

    def _is_restaurant_poi(self, poi: dict[str, Any]) -> bool:
        if poi.get("local_activity") or poi.get("category") == "activity":
            return False
        if poi.get("category") == "restaurant" or poi.get("local_restaurant"):
            return True
        if poi.get("source") != "amap":
            return False
        text = f"{poi.get('type', '')}{poi.get('tag', '')}{poi.get('keyword', '')}{poi.get('name', '')}"
        return any(word in text for word in ["餐饮", "餐厅", "小吃", "咖啡", "茶饮", "火锅", "烧烤", "面馆", "酒楼"])

    def _normalize_restaurant(self, poi: dict[str, Any]) -> dict[str, Any]:
        return {
            "name": poi.get("name") or "本地餐厅",
            "type": poi.get("type") or "餐饮服务",
            "address": poi.get("address"),
            "area": poi.get("adname") or poi.get("address") or "目的地附近",
            "location": poi.get("location"),
            "amap_url": self._amap_url(poi.get("name"), poi.get("location"), poi.get("address") or poi.get("adname")),
            "rating": poi.get("rating"),
            "photo_url": poi.get("photo_url"),
            "cost": self._safe_int(poi.get("cost"), 90),
            "duration": 75,
            "reason": self._restaurant_reason(poi),
        }

    def _restaurant_for_meal(
        self,
        restaurants: list[dict[str, Any]],
        index: int,
        nearby: dict[str, Any],
        used_names: set[str],
    ) -> dict[str, Any]:
        if not restaurants:
            return {
                "name": "请配置高德 Key 获取具体餐厅",
                "type": "餐饮提示",
                "address": "当前城市暂无内置餐厅数据",
                "area": nearby.get("area") or "目的地附近",
                "cost": 80,
                "duration": 75,
                "reason": "当前目的地没有内置具体餐厅，配置高德 Key 后会返回真实餐厅。",
            }
        nearby_area = nearby.get("area")
        if nearby_area:
            for offset in range(len(restaurants)):
                restaurant = restaurants[(index + offset) % len(restaurants)]
                if restaurant.get("name") in used_names:
                    continue
                if nearby_area in str(restaurant.get("area") or restaurant.get("address") or ""):
                    return restaurant
        for offset in range(len(restaurants)):
            restaurant = restaurants[(index + offset) % len(restaurants)]
            if restaurant.get("name") not in used_names:
                return restaurant
        return restaurants[index % len(restaurants)]

    def _food_item(
        self,
        time: str,
        title: str,
        restaurant: dict[str, Any],
        nearby: dict[str, Any],
        cost: int,
        food_name: str,
        backup: str | None = None,
    ) -> dict[str, Any]:
        restaurant_cost = self._safe_int(restaurant.get("cost"), cost)
        return {
            "time": time,
            "type": "food",
            "title": title,
            "place": restaurant.get("name") or "待补充具体餐厅",
            "address": restaurant.get("address"),
            "location": restaurant.get("location"),
            "amap_url": self._amap_url(restaurant.get("name"), restaurant.get("location"), restaurant.get("address") or restaurant.get("area")),
            "rating": restaurant.get("rating"),
            "photo_url": restaurant.get("photo_url"),
            "duration_minutes": restaurant.get("duration", 75),
            "transport": f"尽量选择{nearby.get('area', '上一站')}附近用餐，步行或短途打车",
            "estimated_cost_cny": max(cost, restaurant_cost),
            "restaurant_cost_cny": restaurant_cost,
            "reason": f"{restaurant.get('reason', '')} 这餐重点匹配{food_name}。".strip(),
            "details": [
                f"推荐重点：{food_name}，优先点店内招牌或当地常见做法。",
                f"用餐区域：{restaurant.get('area') or nearby.get('area') or '当日行程附近'}，减少跨区往返。",
                "建议预留 60-90 分钟；热门餐厅饭点可能排队，可以提前半小时到达。",
            ],
            "tips": [
                "如果排队超过 30 分钟，直接换同区域备选餐厅。",
                "东北菜、湘菜等分量通常偏大，2 人点 2-3 个菜更稳。",
            ],
            "backup": backup or "若排队过久，改去同区域评分较高的餐厅或商场餐饮区。",
        }

    def _activity_item(self, time: str, activity: dict[str, Any], cost: int) -> dict[str, Any]:
        activity_cost = self._safe_int(activity.get("cost"), cost)
        return {
            "time": time,
            "type": "activity",
            "title": "本地特色活动",
            "place": activity.get("name") or "本地特色活动",
            "address": activity.get("address"),
            "location": activity.get("location"),
            "amap_url": activity.get("amap_url") or self._amap_url(activity.get("name"), activity.get("location"), activity.get("address")),
            "rating": activity.get("rating"),
            "photo_url": activity.get("photo_url"),
            "duration_minutes": activity.get("duration", 120),
            "transport": f"建议安排在{activity.get('area', '当日活动区域')}，晚间打车更省心",
            "estimated_cost_cny": max(cost, activity_cost),
            "reason": activity.get("reason") or "这是结合目的地生活方式加入的本地特色体验。",
            "details": [
                "这项安排用于补足当地生活方式体验，不只是景点打卡。",
                f"建议预留 {activity.get('duration', 120)} 分钟，结束后直接回酒店更轻松。",
                "如果是洗浴/汗蒸/温泉类活动，建议自带常用洗护用品并确认营业时间。",
            ],
            "tips": [
                "晚间活动以舒适为主，不建议再叠加远距离景点。",
                "如同行者有老人或儿童，提前确认场馆规则和休息区条件。",
            ],
            "backup": "如果当天体力不足，可以改为酒店休整或附近咖啡/茶馆。",
        }

    def _attraction_item(
        self,
        time: str,
        title: str,
        poi: dict[str, Any],
        cost: int,
        reason_suffix: str,
        backup: str,
    ) -> dict[str, Any]:
        return {
            "time": time,
            "type": "attraction",
            "title": title,
            "place": poi["name"],
            "location": poi.get("location"),
            "amap_url": self._amap_url(poi.get("name"), poi.get("location"), poi.get("area")),
            "rating": poi.get("rating"),
            "photo_url": poi.get("photo_url"),
            "duration_minutes": poi.get("duration", 120),
            "transport": f"建议围绕{poi.get('area', '同区域')}游玩，优先地铁/公交，跨区再打车",
            "estimated_cost_cny": max(cost, self._safe_int(poi.get("cost"), 0)),
            "reason": f"{poi.get('reason', '')} {reason_suffix}".strip(),
            "details": self._attraction_details(poi),
            "tips": self._attraction_tips(poi),
            "backup": backup,
        }

    def _attraction_details(self, poi: dict[str, Any]) -> list[str]:
        place_type = self._safe_text(poi.get("type")) or "景点"
        area = self._safe_text(poi.get("area")) or "当日区域"
        duration = poi.get("duration", 120)
        return [
            f"游玩重点：这是{place_type}类安排，建议围绕主要展区、核心景观或代表性街区体验。",
            f"区域策略：安排在{area}，尽量和同区域餐厅/活动串联，减少路上时间。",
            f"时间控制：建议预留 {duration} 分钟，拍照、休息和排队都要留余量。",
        ]

    def _attraction_tips(self, poi: dict[str, Any]) -> list[str]:
        tips = ["出发前确认开放时间、预约要求和临时闭馆信息。"]
        if poi.get("indoor"):
            tips.append("这是室内友好点，雨天或高温天可以优先保留。")
        else:
            tips.append("户外停留较多，注意天气、补水和防晒/保暖。")
        if self._safe_int(poi.get("cost"), 0) > 0:
            tips.append("涉及门票或项目费用，建议提前查看线上购票渠道。")
        return tips

    def _amap_reason(self, poi: dict[str, Any]) -> str:
        parts = ["来自高德地图 POI 数据"]
        if poi.get("rating"):
            parts.append(f"评分约 {poi['rating']}")
        if poi.get("adname"):
            parts.append(f"位于{poi['adname']}")
        if poi.get("type"):
            parts.append(f"类型为{poi['type']}")
        return "，".join(parts) + "。"

    def _restaurant_reason(self, poi: dict[str, Any]) -> str:
        parts = ["来自高德地图餐饮 POI" if poi.get("source") == "amap" else "来自本地具体餐厅库"]
        if poi.get("rating"):
            parts.append(f"评分约 {poi['rating']}")
        if poi.get("cost"):
            parts.append(f"人均约 ¥{poi['cost']}")
        if poi.get("adname"):
            parts.append(f"位于{poi['adname']}")
        if poi.get("type"):
            parts.append(f"类型为{poi['type']}")
        return "，".join(parts) + "。"

    def _activity_reason(self, poi: dict[str, Any]) -> str:
        parts = ["来自高德地图特色活动 POI" if poi.get("source") == "amap" else "来自本地特色活动库"]
        if poi.get("rating"):
            parts.append(f"评分约 {poi['rating']}")
        if poi.get("adname"):
            parts.append(f"位于{poi['adname']}")
        if poi.get("type"):
            parts.append(f"类型为{poi['type']}")
        return "，".join(parts) + "。"

    def _amap_url(self, name: Any, location: Any, address: Any = None) -> str:
        label = quote(str(name or "目的地"))
        if location:
            return f"https://uri.amap.com/marker?position={location}&name={label}&coordinate=gaode&callnative=1"
        keyword = quote(" ".join(str(part) for part in [name, address] if part))
        return f"https://uri.amap.com/search?keyword={keyword or label}&callnative=1"

    def _safe_int(self, value: Any, default: int) -> int:
        try:
            if value is None:
                return default
            return round(float(value))
        except (TypeError, ValueError):
            return default

    def _safe_text(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, list | tuple | set):
            return " ".join(self._safe_text(item) for item in value if self._safe_text(item))
        return str(value)

    def _string_items(self, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list | tuple | set):
            items: list[str] = []
            for item in value:
                items.extend(self._string_items(item))
            return items
        return [str(value)]

    def _daily_budget(self, request: TripCreate) -> int:
        if request.budget_cny:
            return max(120, round(request.budget_cny / max(1, request.days)))
        return 450 * request.travelers

    def _weather_text(self, day_weather: dict[str, Any]) -> str:
        if not day_weather:
            return "暂无天气数据，建议出发前再次刷新"
        text = day_weather.get("textDay") or day_weather.get("textNight") or "天气待确认"
        temp_min = day_weather.get("tempMin")
        temp_max = day_weather.get("tempMax")
        pop = day_weather.get("pop")
        if temp_min and temp_max:
            suffix = f"，降水概率 {pop}%" if pop is not None and pop != "" else ""
            return f"{text}，{temp_min}-{temp_max}℃{suffix}"
        return str(text)

    def _weather_detail(self, day_weather: dict[str, Any]) -> dict[str, Any] | None:
        if not day_weather:
            return None
        return {
            "date": day_weather.get("date"),
            "day": day_weather.get("textDay"),
            "night": day_weather.get("textNight"),
            "temp_min": day_weather.get("tempMin"),
            "temp_max": day_weather.get("tempMax"),
            "humidity": day_weather.get("humidity"),
            "precip": day_weather.get("precip"),
            "pop": day_weather.get("pop"),
            "uv_index": day_weather.get("uvIndex"),
            "wind_day": self._wind_text(day_weather, "Day"),
            "wind_night": self._wind_text(day_weather, "Night"),
            "source": day_weather.get("source"),
            "week": day_weather.get("week"),
        }

    def _wind_text(self, day_weather: dict[str, Any], suffix: str) -> str | None:
        direction = day_weather.get(f"windDir{suffix}")
        scale = day_weather.get(f"windScale{suffix}")
        if direction and scale:
            return f"{direction}{scale}级"
        return direction or scale

    def _is_rainy(self, day_weather: dict[str, Any]) -> bool:
        text = f"{day_weather.get('textDay', '')}{day_weather.get('textNight', '')}"
        return any(word in text for word in ["雨", "雪", "雷阵雨", "阵雨"])

    def _is_hot(self, day_weather: dict[str, Any]) -> bool:
        try:
            return int(day_weather.get("tempMax", 0)) >= 32
        except (TypeError, ValueError):
            return False

    def _theme(
        self,
        index: int,
        rainy: bool,
        request: TripCreate,
        city_data: dict[str, Any] | None,
    ) -> str:
        if rainy:
            return "雨天友好的室内与美食路线"
        if city_data and index == 0:
            return f"{city_data['name']}经典初印象"
        if index == request.days - 1:
            return "轻松收尾与返程友好安排"
        return "同区域串联的深度体验"

    def _weather_advice(
        self,
        weather: list[dict[str, Any]],
        days: int,
        city_data: dict[str, Any] | None,
    ) -> list[str]:
        advice = []
        if city_data:
            advice.extend(city_data.get("weather_tips", []))
        if not weather:
            advice.append("当前未配置天气 Key，已按常规舒适节奏生成；出发前建议刷新天气。")
            return advice
        if any(self._is_rainy(day) for day in weather[:days]):
            advice.append("行程中可能有雨，已为户外活动配置室内备选。")
        if any(self._is_hot(day) for day in weather[:days]):
            advice.append("部分日期温度偏高，建议把户外活动放在上午或傍晚。")
        if any(self._is_cold(day) for day in weather[:days]):
            advice.append("部分日期温度偏低，建议减少夜间长时间户外停留。")
        if any(self._high_uv(day) for day in weather[:days]):
            advice.append("紫外线偏强，户外景点请准备防晒用品。")
        advice.append("天气、预约和营业时间可能变化，出发当天请再次确认。")
        return advice

    def _is_cold(self, day_weather: dict[str, Any]) -> bool:
        try:
            return int(day_weather.get("tempMin", 99)) <= 5
        except (TypeError, ValueError):
            return False

    def _high_uv(self, day_weather: dict[str, Any]) -> bool:
        try:
            return int(day_weather.get("uvIndex", 0)) >= 7
        except (TypeError, ValueError):
            return False

    def _budget_summary(self, request: TripCreate, days: list[dict[str, Any]]) -> dict[str, Any]:
        total = sum(
            int(item.get("estimated_cost_cny") or 0)
            for day in days
            for item in day.get("items", [])
        )
        return {
            "total_estimated_cny": total,
            "food_cny": round(total * 0.42),
            "transport_cny": round(total * 0.2),
            "tickets_cny": round(total * 0.25),
            "notes": "估算不含大交通和酒店；真实价格、预约和开放时间以平台和现场为准。",
        }

    def _foods(self, city_data: dict[str, Any] | None) -> list[str]:
        if city_data and city_data.get("foods"):
            return city_data["foods"]
        return ["本地特色菜", "当地小吃", "人气餐厅"]

    def _rainy_backups(self, city_data: dict[str, Any] | None) -> list[str]:
        if city_data and city_data.get("rainy_backups"):
            return city_data["rainy_backups"]
        return ["附近博物馆", "室内商场", "咖啡馆或茶馆"]

    def _backup(self, backups: list[str], index: int) -> str:
        return backups[index % len(backups)]

    def _normalize_plan(
        self,
        plan: dict[str, Any],
        request: TripCreate,
        weather: list[dict[str, Any]],
    ) -> dict[str, Any]:
        city_data = find_city_data(request.destination)
        plan.setdefault("destination", city_data["name"] if city_data else request.destination)
        plan.setdefault("summary", f"{request.days} 天{request.destination}旅行计划")
        plan.setdefault("weather_advice", self._weather_advice(weather, request.days, city_data))
        plan.setdefault("budget_summary", {"notes": "预算待估算"})
        plan.setdefault("days", [])
        self._enrich_timing(plan)
        return plan

    def _enrich_timing(self, plan: dict[str, Any]) -> None:
        for day in plan.get("days", []):
            if not isinstance(day, dict):
                continue
            previous_end: datetime | None = None
            for item in day.get("items", []):
                if not isinstance(item, dict):
                    continue
                duration = max(30, self._safe_int(item.get("duration_minutes"), self._default_duration(item)))
                buffer_minutes = self._buffer_minutes(item)
                start = self._parse_time(item.get("time"))
                if start is None:
                    start = (previous_end + timedelta(minutes=buffer_minutes)) if previous_end else self._parse_time("09:30")
                if previous_end and start < previous_end:
                    start = previous_end + timedelta(minutes=buffer_minutes)
                end = start + timedelta(minutes=duration)
                item["time"] = start.strftime("%H:%M")
                item["end_time"] = end.strftime("%H:%M")
                item["time_range"] = f"{item['time']}-{item['end_time']}"
                item["duration_minutes"] = duration
                item["buffer_minutes"] = buffer_minutes
                item["schedule_note"] = self._schedule_note(item, duration, buffer_minutes)
                item["time_blocks"] = self._time_blocks(item, start, duration)
                previous_end = end

    def _parse_time(self, value: Any) -> datetime | None:
        try:
            return datetime.strptime(str(value), "%H:%M")
        except (TypeError, ValueError):
            return None

    def _default_duration(self, item: dict[str, Any]) -> int:
        item_type = item.get("type")
        if item_type == "food":
            return 75
        if item_type == "activity":
            return 120
        if item_type == "shopping":
            return 90
        if item_type == "rest":
            return 45
        return 120

    def _buffer_minutes(self, item: dict[str, Any]) -> int:
        item_type = item.get("type")
        if item_type == "food":
            return 30
        if item_type == "activity":
            return 20
        if item_type == "transfer":
            return 10
        return 25

    def _schedule_note(self, item: dict[str, Any], duration: int, buffer_minutes: int) -> str:
        item_type = item.get("type")
        if item_type == "food":
            return f"用餐约 {duration} 分钟，前后预留 {buffer_minutes} 分钟用于排队、找座和去下一站。"
        if item_type == "activity":
            return f"体验约 {duration} 分钟，结束后预留 {buffer_minutes} 分钟整理、打车或返回酒店。"
        return f"停留约 {duration} 分钟，额外预留 {buffer_minutes} 分钟用于入场、拍照、休息和换乘。"

    def _time_blocks(self, item: dict[str, Any], start: datetime, duration: int) -> list[str]:
        item_type = item.get("type")
        if item_type == "food":
            blocks = [
                ("到店/排队/点餐", 15),
                ("正式用餐", max(35, duration - 30)),
                ("结账和短休息", 15),
            ]
        elif item_type == "activity":
            blocks = [
                ("入场和准备", 15),
                ("核心体验", max(60, duration - 35)),
                ("收尾整理/返程准备", 20),
            ]
        else:
            blocks = [
                ("到达、入场和路线确认", 15),
                ("核心游览", max(45, duration - 45)),
                ("拍照、休息和补水", 20),
                ("离场前往下一站", 10),
            ]
        result = []
        cursor = start
        remaining = duration
        for index, (label, minutes) in enumerate(blocks):
            block_minutes = min(minutes, remaining) if index < len(blocks) - 1 else remaining
            if block_minutes <= 0:
                continue
            end = cursor + timedelta(minutes=block_minutes)
            result.append(f"{cursor.strftime('%H:%M')}-{end.strftime('%H:%M')} {label}")
            cursor = end
            remaining -= block_minutes
        return result
