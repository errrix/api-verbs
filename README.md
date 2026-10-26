# API испанских глаголов

Спряжения 2500 самых частых испанских глаголов в 24 временах. Данные статичные, поэтому
раздаются как JSON-файлы с GitHub Pages.

## Откуда данные

| Что | Источник | Лицензия |
|---|---|---|
| Спряжения и список существующих глаголов | [conjugate-esp](https://github.com/jirimracek/conjugate-esp) — 14 456 глаголов, признанных RAE | MIT |
| Какие глаголы брать (частота) | [wordfreq](https://github.com/rspeer/wordfreq) | данные CC BY-SA 4.0 |
| Переводы на русский, английский, португальский, французский, немецкий и итальянский | `data/translations_{lang}.json`, свои | — |

Частоты wordfreq требуют атрибуции: в приложении, которое использует эти данные, нужно упомянуть wordfreq.

## Как устроено

```
data/verbs.json          какие глаголы есть в API (список инфинитивов)
data/conjugations.json   их спряжения — генерируются из conjugate-esp
data/translations_*.json  переводы: ru — эталон, остальные языки переводят те же значения
data/themes.json         глаголы по 30 темам (дом, кухня, работа, путешествия...)
data/frequency.json      все глаголы от частых к редким (python scripts/rank_verbs.py)
dist/                    результат сборки, выкладывается на GitHub Pages
```

1. **Список глаголов** дополняется до нужного размера самыми частыми глаголами (нужны node и `pip install wordfreq`):

   ```bash
   python scripts/select_verbs.py 2500
   ```

   Глаголы, которые уже есть в списке, остаются всегда: по ним у пользователей может быть прогресс.
   Омонимы вроде `militar`, только возвратные глаголы и грубые слова отсекаются, подробности в начале скрипта.

2. **Спряжения** генерируются заново для всего списка:

   ```bash
   npm install
   npm run generate
   ```

   Логика — в `scripts/conjugate.mjs`. Если у формы несколько допустимых вариантов, они идут через слэш,
   первый — основной: `freído/frito`. Принимаются обе орфографии, 2010 года и старая: `guiais/guiáis`.
   Там же ручные поправки (`OVERRIDES`) и выбор модели спряжения для глаголов, у которых их в conjugate-esp
   несколько (`MODELS`). Глагол с несколькими моделями, для которого выбор не сделан, останавливает генерацию.

3. **Новым глаголам нужны переводы** во всех `data/translations_{lang}.json`, иначе сборка упадёт со списком недостающих.

Темы в `data/themes.json` размечены по значениям глаголов: глагол в 0–3 темах, внутри темы — от частых к редким.
Сборка падает, если в теме есть глагол не из списка или тема пустая.

После изменения списка глаголов пересчитай частотный порядок: `python scripts/rank_verbs.py` (тоже нужен wordfreq).
Сборка падает, если `data/frequency.json` не совпадает со списком.

4. **Сборка** в `dist/` (нужен только Python, без зависимостей):

   ```bash
   python scripts/build_static.py
   ```

   При пуше в `main` то же самое делает workflow `.github/workflows/pages.yml` и выкладывает результат на GitHub Pages.

## Формат

| Файл | Что внутри |
|---|---|
| `index.json` | Список глаголов, времён (`id`, `name`, `personal`) и лиц; `translations` — список доступных языков перевода (`["ru", "en", "pt", "fr", "de", "it"]`) |
| `verbs/{infinitive}.json` | Все времена одного глагола; `translations` — его переводы по языкам (`{"ru": [...]}`) |
| `tenses/{id}.json` | Одно время для всех глаголов |
| `translations/{lang}.json` | Переводы инфинитивов всех глаголов на один язык: `{инфинитив: [значения]}` |
| `frequency.json` | Все глаголы от частых к редким, по wordfreq |
| `themes.json` | Глаголы по темам: `{тема: [глаголы от частых к редким]}`. Один глагол может быть в нескольких темах, у части глаголов темы нет |

Личные времена — объект `{лицо: форма}`, неличные формы (герундий, инфинитив, причастие) — строка.
Вспомогательный глагол уже входит в форму. Несколько вариантов — через слэш, в составных формах
слэш относится к последнему слову: `he freído/frito`.

```json
{
  "infinitive": "hablar",
  "translations": {"ru": ["говорить", "разговаривать"]},
  "tenses": {
    "indicativo-presente": {"1s": "hablo", "2s": "hablas", "3s": "habla", "1p": "hablamos", "2p": "habláis", "3p": "hablan"},
    "indicativo-preterito-perfecto-compuesto": {"1s": "he hablado", "2s": "has hablado", "...": "..."},
    "imperativo": {"2s": "habla", "3s": "hable", "1p": "hablemos", "2p": "hablad", "3p": "hablen"},
    "gerundio": "hablando"
  }
}
```

У недостаточных глаголов (`soler`) нет форм, которых не бывает: времени или лица просто нет в данных.

Переводы — объект `{инфинитив: [значения]}`, от одного до трёх значений, первое — основное. Сборка
падает с описанием ошибки, если у какого-то глагола нет перевода, в файле есть лишние ключи или
значения — не непустые строки.

# FastAPI-приложение

> Устарело: приложение и база берут данные из `data/verbs_seed.sql` — это старые 1000 глаголов,
> они больше не обновляются. Актуальные данные — только в статической сборке выше.

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


