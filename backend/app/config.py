from functools import lru_cache
import os
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class Settings:
    def __init__(self) -> None:
        _load_dotenv()
        self.app_name = os.getenv("APP_NAME", "Travel Planner API")
        self.database_path = os.getenv("DATABASE_PATH", "travel_planner.db")
        self.amap_key = os.getenv("AMAP_KEY", "")
        self.openai_api_key = self._clean_secret(os.getenv("OPENAI_API_KEY", ""))
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
        self.celery_broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        self.celery_result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
        self.push_provider = os.getenv("PUSH_PROVIDER", "mock")

    def _clean_secret(self, value: str) -> str:
        return "" if value in {"", "replace_me", "your_key_here"} else value


@lru_cache
def get_settings() -> Settings:
    return Settings()
