## Phone-Address Service

FastAPI сервис для хранения соответствия телефон → адрес с Redis.

### Стек
- FastAPI, redis.asyncio
- Pydantic v2, pydantic-settings
- Pytest + TestClient
- Docker, docker-compose

### Конфигурация
Переменные окружения (имеют дефолты):
- `REDIS_HOST` (localhost)
- `REDIS_PORT` (6379)
- `REDIS_DB` (0)
- `API_HOST` (0.0.0.0)
- `API_PORT` (8000)

### Локальный запуск
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Тесты
```bash
pytest
```

### Docker
```bash
docker compose up --build
```
API: http://localhost:8000

### API
- `POST /phones` — создать телефон/адрес (NX)
- `GET /phones/{phone}` — получить
- `PUT /phones/{phone}` — обновить (XX)
- `DELETE /phones/{phone}` — 204 при успехе
- `GET /health` — проверка Redis

### Структура
- `app/main.py` — создание приложения, lifecycle, роуты
- `app/routers.py` — endpoints, Depends
- `app/services.py` — бизнес-логика
- `app/storage/redis_repo.py` — работа с Redis
- `app/schemas.py` — Pydantic модели/валидация
- `app/config.py` — настройки из env

