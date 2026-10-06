# API испанских глаголов

Спряжения 1000 испанских глаголов в 24 временах. Данные статичные, поэтому
раздаются как JSON-файлы с GitHub Pages; FastAPI-приложение с PostgreSQL
(описано ниже) отдаёт те же данные через базу.

## Статические данные

Сборка из `data/verbs_seed.sql` в папку `dist/` (нужен только Python, без зависимостей):

```bash
python scripts/build_static.py
```

При пуше в `main` то же самое делает workflow `.github/workflows/pages.yml` и выкладывает результат на GitHub Pages.

| Файл | Что внутри |
|---|---|
| `index.json` | Список глаголов, времён (`id`, `name`, `personal`) и лиц |
| `verbs/{infinitive}.json` | Все времена одного глагола |
| `tenses/{id}.json` | Одно время для всех глаголов |

Личные времена — объект `{лицо: форма}`, неличные формы (герундий, инфинитив, причастие) — строка.
Вспомогательный глагол уже входит в форму:

```json
{
  "infinitive": "hablar",
  "tenses": {
    "indicativo-presente": {"1s": "hablo", "2s": "hablas", "3s": "habla", "1p": "hablamos", "2p": "habláis", "3p": "hablan"},
    "indicativo-preterito-perfecto-compuesto": {"1s": "he hablado", "2s": "has hablado", "...": "..."},
    "imperativo": {"2s": "habla", "3s": "hable", "1p": "hablemos", "2p": "hablad", "3p": "hablen"},
    "gerundio": "hablando"
  }
}
```

У недостаточных глаголов (`llover`, `acontecer`, `atañer`, `concernir`) есть только формы третьего лица.

# FastAPI-приложение

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


