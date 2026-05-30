# AI Travel Planner MVP

一个天气感知的 AI 旅行计划 App。用户输入目的地、出发日期、游玩天数、人数、预算、兴趣偏好和避雷点后，系统结合天气、地图 POI、预算和游玩节奏，生成按天展示的完整行程。

## 当前能力

- Flutter App：创建旅行需求、展示每日时间线、天气建议、预算估算和备选方案。
- FastAPI Backend：旅行计划创建、查询、重新生成。
- Local City Data：内置北京、广州、西双版纳、上海、长沙、武汉、杭州、苏州的景点、美食、区域、雨天备选和天气提示。
- Weather Planner：接入高德天气预报，按天展示天气、温度和风力，并影响雨天/高温行程安排。
- AMap Wrapper：支持高德 POI 详细资料、区县、坐标、评分/人均字段和相邻行程路线耗时估算。
- Restaurant Planner：午餐和晚餐会优先使用高德真实餐厅 POI，展示具体餐厅名、地址、评分、人均、图片和路线耗时。
- AMap Jump：每个景点/餐厅行程卡片会生成高德地图链接，有坐标时打开精确点位，没有坐标时打开高德搜索。
- AI Planner：有 OpenAI Key 时调用模型生成结构化 JSON；未配置 Key 时使用本地规则生成可演示行程。
- Push Wrapper：预留推送通道抽象。

## 规划逻辑

1. 收集用户需求：目的地、日期、天数、人数、预算、兴趣、节奏、住宿位置、避免事项。
2. 查询天气：识别降雨、高温等影响行程体验的因素。
3. 搜索 POI：根据兴趣偏好搜索景点、美食、博物馆、商圈、夜景等候选点。
4. 生成计划：优先同区域串联，减少跨城折返；雨天增加室内备选；高温减少正午户外活动。
5. 返回结构化结果：summary、weather_advice、budget_summary、days/items，便于前端稳定渲染。

## Run backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The MVP works without API keys by returning a rule-based fallback plan. Add `AMAP_KEY` and `OPENAI_API_KEY` in `backend/.env` to enable real services.

高德接入：

```powershell
cd backend
Copy-Item .env.example .env
notepad .env
```

在 `.env` 中填写高德 Web 服务 Key：

```env
AMAP_KEY=your_amap_web_service_key
```

重启后端后，系统会用高德补充真实 POI，并在有坐标时为相邻行程点生成路线耗时。
餐饮安排会额外搜索当地餐厅、小吃、咖啡和城市特色菜名，优先把午餐/晚餐落到具体餐厅，而不是泛泛写“附近餐厅”。

高德天气接入复用同一个 `AMAP_KEY`。配置后，系统会通过高德行政区查询获取 adcode，再调用高德天气预报。

测试天气接口：

```text
http://127.0.0.1:8000/api/weather/杭州?days=7
```

城市资料接口：

```text
GET /api/cities
GET /api/cities/{city_name}
```

示例：

```text
http://127.0.0.1:8000/api/cities
http://127.0.0.1:8000/api/cities/北京
```

## Run Flutter app

```powershell
cd flutter_app
flutter pub get
flutter run
```

移动端调试时，手机或模拟器不能直接访问电脑里的 `127.0.0.1`。运行时用 `--dart-define` 指定后端地址：

```powershell
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
```

Android 模拟器通常用 `10.0.2.2`；真机请改成电脑在同一局域网下的 IP，例如 `http://192.168.1.20:8000`。

## Next roadmap

- Add map route duration into each itinerary item.
- Add one-click item replacement: “这个景点不想去，换一个”。
- Add weather refresh and automatic rainy-day replan.
- Add saved trips, sharing, and PDF export.
- Replace JSON file storage with PostgreSQL for production.
