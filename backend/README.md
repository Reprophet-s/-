# Travel Planner Backend

FastAPI backend for a weather-aware AI travel planner.

## Run locally

```powershell
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The MVP works without API keys by returning a rule-based fallback plan. Add `AMAP_KEY` and `OPENAI_API_KEY` in `.env` to enable real services.

`AMAP_KEY` should be a 高德开放平台 Web 服务 Key. Once configured, the backend enriches local city recommendations with real POI details and route duration estimates.
The same `AMAP_KEY` is also used for 高德天气预报.

City data endpoints:

```text
GET /api/cities
GET /api/cities/{city_name}
```

The local MVP uses a JSON file store (`travel_planner.json`) so it can run without database setup. For production, replace `app/storage.py` with PostgreSQL-backed repositories.

## Optional Celery worker

```powershell
celery -A app.tasks.celery_app worker --loglevel=info
```
