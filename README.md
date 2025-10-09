# FastAPI Project

FastAPI приложение с PostgreSQL базой данных в Docker.

## Технологии

- FastAPI
- PostgreSQL
- SQLAlchemy 2.0 (async)
- Docker & Docker Compose
- Pydantic v2

## Структура проекта

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # Главный файл приложения
│   ├── config.py            # Конфигурация
│   ├── database.py          # Подключение к БД
│   ├── models/              # SQLAlchemy модели
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/             # Pydantic схемы
│   │   ├── __init__.py
│   │   └── user.py
│   └── routers/             # API роуты
│       ├── __init__.py
│       └── user_routes.py
├── docker-compose.yml       # Docker Compose конфигурация
├── Dockerfile              # Docker образ для приложения
├── requirements.txt        # Python зависимости
├── .env                    # Переменные окружения
└── README.md

```

## Установка и запуск

### Запуск через Docker Compose

1. Убедитесь, что Docker и Docker Compose установлены

2. Запустите контейнеры:
```bash
docker-compose up -d
```

3. Приложение будет доступно по адресу: http://localhost:8000

4. Документация API (Swagger): http://localhost:8000/docs

5. Альтернативная документация (ReDoc): http://localhost:8000/redoc

### Остановка контейнеров

```bash
docker-compose down
```

### Просмотр логов

```bash
docker-compose logs -f web
```

## API Endpoints

### Общие

- `GET /` - Корневой endpoint
- `GET /health` - Health check

### Пользователи

- `POST /users/` - Создание пользователя
- `GET /users/` - Получение списка пользователей (с пагинацией)
- `GET /users/{user_id}` - Получение пользователя по ID

## Переменные окружения

Настройте файл `.env`:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fastapi_db
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_db
```

## Разработка

Для локальной разработки без Docker:

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Убедитесь, что PostgreSQL запущен (можно через Docker Compose только для БД):
```bash
docker-compose up -d db
```

4. Запустите приложение:
```bash
uvicorn app.main:app --reload
```


