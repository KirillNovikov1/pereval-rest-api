# Pereval REST API

Учебный проект ФСТР: REST API для добавления, просмотра и редактирования перевалов.

## Описание задачи

Нужно было реализовать REST API, через которое мобильное приложение может:

- отправить данные о новом перевале;
- получить данные о перевале по `id`;
- отредактировать перевал, если он ещё не ушёл в работу модератору;
- получить список всех перевалов пользователя по его email.

Дополнительно в проекте должно храниться поле `status` со статусом модерации.

## Что реализовано

- PostgreSQL как основная БД.
- Поддержка SQLite через `FSTR_DB_URL` для локального тестирования и запуска тестов.
- Нормализованная структура таблиц:
  - `users`
  - `coords`
  - `pereval_added`
  - `pereval_images`
- В таблицу `pereval_added` добавлено поле `status`.
- Допустимые статусы модерации:
  - `new`
  - `pending`
  - `accepted`
  - `rejected`
- Класс `Database` для работы с БД.
- REST API со следующими методами:
  - `POST /submitData`
  - `GET /submitData/<id>`
  - `PATCH /submitData/<id>`
  - `GET /submitData?user__email=<email>`
- Swagger-документация через Flasgger.
- Набор тестов для слоя БД и REST API.
- Подготовка к деплою на хостинг через `gunicorn`.

## Бизнес-правила

- Новая запись создаётся со статусом `new`.
- Редактирование записи разрешено только при статусе `new`.
- Нельзя изменять данные пользователя:
  - `fam`
  - `name`
  - `otc`
  - `email`
  - `phone`

## Структура проекта

```text
pereval_sprint_2_final/
├── app.py
├── config.py
├── database.py
├── models.py
├── requirements.txt
├── schema.sql
├── .env.example
├── .gitignore
├── README.md
├── render.yaml
├── pytest.ini
└── tests/
    ├── conftest.py
    ├── test_api.py
    └── test_db.py
```

## Используемые технологии

- Python 3.11+
- Flask
- SQLAlchemy
- PostgreSQL
- SQLite
- Flasgger (Swagger UI)
- pytest
- gunicorn

## Переменные окружения

Проект поддерживает два способа настройки подключения к БД.

### Вариант 1. Через отдельные переменные PostgreSQL

```env
FSTR_DB_HOST=localhost
FSTR_DB_PORT=5432
FSTR_LOGIN=pereval_user
FSTR_PASS=your_password
FSTR_DB_NAME=pereval_db
```

### Вариант 2. Через готовую строку подключения

```env
FSTR_DB_URL=sqlite:///pereval.db
```

Для локального тестирования и для `pytest` проще всего использовать второй вариант.

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone <URL_РЕПОЗИТОРИЯ>
cd pereval_sprint_2_final
```

### 2. Создать и активировать виртуальное окружение

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать `.env`

Скопируй `.env.example` в `.env` и заполни своими значениями.

### 5. Запустить приложение

```bash
python app.py
```

После запуска приложение будет доступно по адресу:

```text
http://127.0.0.1:5000
```

## Swagger / OpenAPI

После запуска приложения документация будет доступна по адресу:

```text
http://127.0.0.1:5000/apidocs/
```

Служебная проверка доступности приложения:

```text
GET /health
```

## Deploy

Production URL:
https://pereval-rest-api-yr5a.onrender.com/

UI URL:
https://pereval-rest-api-yr5a.onrender.com/ui

Healthcheck:
https://pereval-rest-api-yr5a.onrender.com/health

Swagger:
https://pereval-rest-api-yr5a.onrender.com/apidocs/

## REST API

### 1. POST `/submitData`

Добавляет новый перевал в БД.

Пример тела запроса:

```json
{
  "beautyTitle": "пер.",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "add_time": "2026-03-22 12:00:00",
  "user": {
    "email": "user@example.com",
    "phone": "+79990001122",
    "fam": "Иванов",
    "name": "Иван",
    "otc": "Иванович"
  },
  "coords": {
    "latitude": 45.3842,
    "longitude": 7.1525,
    "height": 1200
  },
  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  },
  "images": [
    {
      "title": "Вид на перевал",
      "data": "aGVsbG8="
    }
  ]
}
```

Успешный ответ:

```json
{
  "status": 200,
  "id": 1,
  "message": "Success"
}
```

### 2. GET `/submitData/<id>`

Возвращает одну запись о перевале по `id`.

Пример ответа:

```json
{
  "id": 1,
  "beautyTitle": "пер.",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "add_time": "2026-03-22 12:00:00",
  "status": "new",
  "user": {
    "email": "user@example.com",
    "phone": "+79990001122",
    "fam": "Иванов",
    "name": "Иван",
    "otc": "Иванович"
  },
  "coords": {
    "latitude": 45.3842,
    "longitude": 7.1525,
    "height": 1200
  },
  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  },
  "images": []
}
```

### 3. PATCH `/submitData/<id>`

Редактирует существующую запись, если её статус равен `new`.

Можно менять:
- данные перевала;
- координаты;
- уровни сложности;
- изображения.

Нельзя менять:
- `fam`
- `name`
- `otc`
- `email`
- `phone`

Успешный ответ:

```json
{
  "state": 1,
  "message": "The record was updated successfully"
}
```

Ошибка при попытке изменить данные пользователя:

```json
{
  "state": 0,
  "message": "Protected user field cannot be changed: phone"
}
```

Ошибка при попытке редактировать запись со статусом не `new`:

```json
{
  "state": 0,
  "message": "Pereval can only be edited in status 'new'. Current status: pending"
}
```

### 4. GET `/submitData?user__email=<email>`

Возвращает список всех перевалов, отправленных пользователем с указанной почтой.

## Примеры запросов через PowerShell

### Создание записи

```powershell
$body = @{
    beautyTitle = "пер."
    title = "Test pass"
    other_titles = ""
    connect = ""
    add_time = "2026-03-22 12:00:00"
    user = @{
        email = "test@example.com"
        phone = "+79990001122"
        fam = "Ivanov"
        name = "Ivan"
        otc = "Ivanovich"
    }
    coords = @{
        latitude = 50.11111
        longitude = 8.22222
        height = 1500
    }
    level = @{
        winter = ""
        summer = "1A"
        autumn = ""
        spring = ""
    }
    images = @()
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://127.0.0.1:5000/submitData" -Method Post -Body $body -ContentType "application/json"
```

### Получение списка по email

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/submitData?user__email=test@example.com" -Method Get
```

### Редактирование записи

```powershell
$current = Invoke-RestMethod -Uri "http://127.0.0.1:5000/submitData/1" -Method Get

$patchBody = @{
    beautyTitle = $current.beautyTitle
    title = "Updated pass title"
    other_titles = $current.other_titles
    connect = $current.connect
    add_time = $current.add_time
    user = @{
        email = [string]$current.user.email
        phone = [string]$current.user.phone
        fam   = [string]$current.user.fam
        name  = [string]$current.user.name
        otc   = [string]$current.user.otc
    }
    coords = @{
        latitude = $current.coords.latitude
        longitude = $current.coords.longitude
        height = $current.coords.height
    }
    level = @{
        winter = $current.level.winter
        summer = $current.level.summer
        autumn = $current.level.autumn
        spring = $current.level.spring
    }
    images = @()
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://127.0.0.1:5000/submitData/1" -Method Patch -Body $patchBody -ContentType "application/json"
```

## Тестирование

Запуск всех тестов:

```bash
pytest -v
```

Запуск тестов с покрытием:

```bash
pytest --cov=. --cov-report=term-missing
```

Что проверяют тесты:

- создание записи в БД;
- получение записи по `id`;
- получение списка по `email`;
- успешное редактирование записи в статусе `new`;
- запрет изменения полей пользователя;
- запрет редактирования, если статус не `new`;
- корректный ответ API для несуществующего `id`.

