# API для испанских глаголов

## Endpoint

### GET `/verbs/{infinitive}`

Возвращает все формы глагола по его инфинитиву.

#### Параметры
- `infinitive` (path) - инфинитив глагола (например: `hablar`, `comer`, `vivir`)

#### Пример запроса
```bash
GET http://localhost:8000/verbs/hablar
```

#### Пример ответа (200 OK)
```json
{
  "infinitive": "hablar",
  "tenses": [
    {
      "tense": "Indicativo Presente",
      "forms": [
        {
          "person": "1s",
          "auxiliary_verb": null,
          "verb_form": "hablo"
        },
        {
          "person": "2s",
          "auxiliary_verb": null,
          "verb_form": "hablas"
        },
        ...
      ]
    },
    {
      "tense": "Indicativo Pretérito perfecto compuesto",
      "forms": [
        {
          "person": "1s",
          "auxiliary_verb": "he",
          "verb_form": "hablado"
        },
        ...
      ]
    },
    ...
  ]
}
```

#### Ошибки
- **404 Not Found** - глагол не найден в базе данных
```json
{
  "detail": "Глагол 'asdfasdf' не найден"
}
```

## Запуск проекта

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Применение миграций
```bash
alembic upgrade head
```

### 3. Импорт глаголов (если база пустая)
```bash
python app/scripts/import_verbs.py
```

### 4. Запуск сервера
```bash
uvicorn app.main:app --reload
```

### 5. Документация API
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

## База данных

В базу загружено **1000 испанских глаголов** со всеми формами (около 118 форм на глагол).

### Структура таблиц

#### `verbs`
- `id` - первичный ключ
- `infinitive` - инфинитив глагола (уникальный, индексирован)
- `created_at` - дата создания

#### `verb_forms`
- `id` - первичный ключ
- `verb_id` - внешний ключ на `verbs.id`
- `tense` - название времени (индексирован)
- `person` - лицо и число (1s, 2s, 3s, 1p, 2p, 3p)
- `auxiliary_verb` - вспомогательный глагол (nullable)
- `verb_form` - форма глагола
- `created_at` - дата создания

## Примеры использования

### Python
```python
import requests

response = requests.get("http://localhost:8000/verbs/hablar")
data = response.json()

print(f"Глагол: {data['infinitive']}")
for tense in data['tenses']:
    print(f"\n{tense['tense']}:")
    for form in tense['forms']:
        if form['auxiliary_verb']:
            print(f"  {form['person']}: {form['auxiliary_verb']} {form['verb_form']}")
        else:
            print(f"  {form['person']}: {form['verb_form']}")
```

### JavaScript
```javascript
fetch('http://localhost:8000/verbs/hablar')
  .then(response => response.json())
  .then(data => {
    console.log(`Глагол: ${data.infinitive}`);
    data.tenses.forEach(tense => {
      console.log(`\n${tense.tense}:`);
      tense.forms.forEach(form => {
        const fullForm = form.auxiliary_verb 
          ? `${form.auxiliary_verb} ${form.verb_form}` 
          : form.verb_form;
        console.log(`  ${form.person}: ${fullForm}`);
      });
    });
  });
```

