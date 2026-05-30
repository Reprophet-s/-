import asyncio

from celery import Celery

from .config import get_settings
from .planner import generate_plan
from .schemas import TripStatus
from .storage import get_trip, save_trip_plan, update_trip_status

settings = get_settings()
celery_app = Celery(
    "travel_planner",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


@celery_app.task(name="generate_trip_plan")
def generate_trip_plan_task(trip_id: str) -> None:
    asyncio.run(_generate_and_store(trip_id))


async def _generate_and_store(trip_id: str) -> None:
    update_trip_status(trip_id, TripStatus.generating)
    try:
        trip = get_trip(trip_id)
        plan = await generate_plan(trip.request)
        save_trip_plan(trip_id, plan)
    except Exception as exc:
        update_trip_status(trip_id, TripStatus.failed, str(exc))
        raise

