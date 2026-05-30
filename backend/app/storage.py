import json
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .config import get_settings
from .schemas import Trip, TripCreate, TripStatus


def utcnow() -> datetime:
    return datetime.now(UTC)


def _store_path() -> Path:
    configured = get_settings().database_path
    if configured.endswith(".json"):
        return Path(configured)
    return Path(configured).with_suffix(".json")


def _empty_store() -> dict[str, Any]:
    return {"trips": {}, "device_tokens": []}


@contextmanager
def _store():
    path = _store_path()
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = _empty_store()
    yield data
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def init_db() -> None:
    path = _store_path()
    if not path.exists():
        path.write_text(json.dumps(_empty_store(), ensure_ascii=False, indent=2), encoding="utf-8")


def _record_to_trip(record: dict[str, Any]) -> Trip:
    return Trip(
        id=record["id"],
        status=TripStatus(record["status"]),
        request=TripCreate.model_validate(record["request"]),
        plan=record.get("plan"),
        error=record.get("error"),
        created_at=datetime.fromisoformat(record["created_at"]),
        updated_at=datetime.fromisoformat(record["updated_at"]),
    )


def create_trip(trip_id: str, request: TripCreate) -> Trip:
    now = utcnow().isoformat()
    record = {
        "id": trip_id,
        "status": TripStatus.pending.value,
        "request": request.model_dump(mode="json"),
        "plan": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
    }
    with _store() as data:
        data["trips"][trip_id] = record
    return get_trip(trip_id)


def list_trips() -> list[Trip]:
    with _store() as data:
        records = list(data["trips"].values())
    records.sort(key=lambda item: item["created_at"], reverse=True)
    return [_record_to_trip(record) for record in records]


def get_trip(trip_id: str) -> Trip:
    with _store() as data:
        record = data["trips"].get(trip_id)
    if record is None:
        raise KeyError(trip_id)
    return _record_to_trip(record)


def update_trip_status(trip_id: str, status: TripStatus, error: str | None = None) -> None:
    with _store() as data:
        record = data["trips"][trip_id]
        record["status"] = status.value
        record["error"] = error
        record["updated_at"] = utcnow().isoformat()


def save_trip_plan(trip_id: str, plan: dict[str, Any]) -> None:
    with _store() as data:
        record = data["trips"][trip_id]
        record["status"] = TripStatus.ready.value
        record["plan"] = plan
        record["error"] = None
        record["updated_at"] = utcnow().isoformat()


def upsert_device_token(user_id: str, token: str, platform: str) -> None:
    now = utcnow().isoformat()
    with _store() as data:
        tokens = [
            item
            for item in data["device_tokens"]
            if not (item["user_id"] == user_id and item["token"] == token)
        ]
        tokens.append({"user_id": user_id, "token": token, "platform": platform, "created_at": now})
        data["device_tokens"] = tokens
