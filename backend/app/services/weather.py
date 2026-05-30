from typing import Any

import httpx

from ..config import get_settings


class AMapWeatherService:
    base_url = "https://restapi.amap.com/v3"

    def __init__(self) -> None:
        self.key = get_settings().amap_key

    async def lookup_adcode(self, destination: str) -> str | None:
        if not self._enabled():
            return None
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                response = await client.get(
                    f"{self.base_url}/config/district",
                    params={
                        "key": self.key,
                        "keywords": destination,
                        "subdistrict": 0,
                        "extensions": "base",
                    },
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError:
            return None
        if data.get("status") != "1":
            return None
        districts = data.get("districts", [])
        return districts[0].get("adcode") if districts else None

    async def daily_forecast(self, destination: str, days: int) -> list[dict[str, Any]]:
        adcode = await self.lookup_adcode(destination)
        if not adcode:
            return []
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                response = await client.get(
                    f"{self.base_url}/weather/weatherInfo",
                    params={
                        "key": self.key,
                        "city": adcode,
                        "extensions": "all",
                    },
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError:
            return []
        if data.get("status") != "1":
            return []
        forecasts = data.get("forecasts", [])
        if not forecasts:
            return []
        casts = forecasts[0].get("casts", [])
        return [self._normalize_daily(item) for item in casts[:days]]

    def _normalize_daily(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "date": item.get("date"),
            "week": item.get("week"),
            "textDay": item.get("dayweather"),
            "textNight": item.get("nightweather"),
            "tempMin": item.get("nighttemp"),
            "tempMax": item.get("daytemp"),
            "humidity": None,
            "precip": None,
            "pop": None,
            "uvIndex": None,
            "windDirDay": item.get("daywind"),
            "windScaleDay": item.get("daypower"),
            "windDirNight": item.get("nightwind"),
            "windScaleNight": item.get("nightpower"),
            "source": "amap_weather",
            "raw": item,
        }

    def _enabled(self) -> bool:
        return bool(self.key and self.key != "replace_me")
