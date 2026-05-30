from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .local_city_data import list_city_summaries, public_city_data
from .poi_cache import DEFAULT_KEYWORDS, list_city_cached_pois, set_cached_pois
from .planner import generate_plan
from .schemas import DeviceTokenCreate, Trip, TripCreate, TripStatus
from .services.amap import AMapService
from .services.push import PushService
from .services.weather import AMapWeatherService
from .storage import (
    create_trip,
    get_trip,
    init_db,
    list_trips,
    save_trip_plan,
    update_trip_status,
    upsert_device_token,
)

app = FastAPI(title="Travel Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/cities")
def list_cities_endpoint() -> list[dict[str, object]]:
    return list_city_summaries()


@app.get("/api/cities/{city_name}")
def get_city_endpoint(city_name: str) -> dict[str, object]:
    city = public_city_data(city_name)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@app.get("/api/cities/{city_name}/pois")
def get_city_pois_endpoint(city_name: str) -> dict[str, object]:
    return list_city_cached_pois(city_name)


@app.post("/api/cities/{city_name}/refresh-pois")
async def refresh_city_pois_endpoint(city_name: str, keywords: str | None = None) -> dict[str, object]:
    amap = AMapService()
    keyword_list = _parse_keywords(keywords)
    refreshed = []
    for keyword in keyword_list:
        pois = await amap.search_poi(city_name, keyword, limit=20)
        if pois:
            set_cached_pois(city_name, keyword, pois)
        refreshed.append({"keyword": keyword, "count": len(pois)})
    cached = list_city_cached_pois(city_name)
    return {"city": city_name, "refreshed": refreshed, "cache": cached}


@app.get("/api/weather/{city_name}")
async def get_weather_endpoint(city_name: str, days: int = 7) -> dict[str, object]:
    forecast = await AMapWeatherService().daily_forecast(city_name, max(1, min(days, 4)))
    return {
        "city": city_name,
        "enabled": bool(forecast),
        "forecast": forecast,
        "message": "ok" if forecast else "No weather data. Check AMAP_KEY in backend/.env.",
    }


def _parse_keywords(keywords: str | None) -> list[str]:
    if not keywords:
        return DEFAULT_KEYWORDS
    items = [item.strip() for item in keywords.replace("，", ",").split(",")]
    return [item for item in items if item]


@app.post("/api/trips", response_model=Trip)
async def create_trip_endpoint(payload: TripCreate, background_tasks: BackgroundTasks) -> Trip:
    trip = create_trip(str(uuid4()), payload)
    background_tasks.add_task(generate_trip_background, trip.id)
    return trip


@app.get("/api/trips", response_model=list[Trip])
def list_trips_endpoint() -> list[Trip]:
    return list_trips()


@app.get("/api/trips/{trip_id}", response_model=Trip)
def get_trip_endpoint(trip_id: str) -> Trip:
    try:
        return get_trip(trip_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Trip not found") from None


@app.post("/api/trips/{trip_id}/generate", response_model=Trip)
async def regenerate_trip_endpoint(trip_id: str, background_tasks: BackgroundTasks) -> Trip:
    try:
        get_trip(trip_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Trip not found") from None
    background_tasks.add_task(generate_trip_background, trip_id)
    return get_trip(trip_id)


@app.post("/api/device-token")
async def register_device_token(payload: DeviceTokenCreate) -> dict[str, str]:
    upsert_device_token(payload.user_id, payload.token, payload.platform)
    return {"status": "ok"}


@app.post("/api/push/test")
async def test_push(user_id: str) -> dict[str, str]:
    await PushService().send_to_user(user_id, "旅行提醒测试", "Push 通道已接入后端抽象。")
    return {"status": "sent"}


async def generate_trip_background(trip_id: str) -> None:
    update_trip_status(trip_id, TripStatus.generating)
    try:
        trip = get_trip(trip_id)
        plan = await generate_plan(trip.request)
        save_trip_plan(trip_id, plan)
    except Exception as exc:
        update_trip_status(trip_id, TripStatus.failed, str(exc))
