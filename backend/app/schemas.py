from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class TripStatus(str, Enum):
    pending = "pending"
    generating = "generating"
    ready = "ready"
    failed = "failed"


class TravelPace(str, Enum):
    relaxed = "relaxed"
    balanced = "balanced"
    packed = "packed"


class TripCreate(BaseModel):
    destination: str = Field(min_length=1, examples=["杭州"])
    start_date: date
    days: int = Field(ge=1, le=30)
    travelers: int = Field(default=1, ge=1, le=20)
    budget_cny: int | None = Field(default=None, ge=0)
    interests: list[str] = Field(default_factory=list, examples=[["美食", "博物馆", "自然风光"]])
    pace: TravelPace = TravelPace.balanced
    hotel_address: str | None = None
    avoid: list[str] = Field(default_factory=list)
    notes: str | None = None

    @field_validator("interests", "avoid", mode="before")
    @classmethod
    def flatten_string_list(cls, value: Any) -> list[str]:
        return _string_items(value)


class Trip(BaseModel):
    id: str
    status: TripStatus
    request: TripCreate
    plan: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime


class DeviceTokenCreate(BaseModel):
    user_id: str
    token: str
    platform: str = Field(examples=["ios", "android"])


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
