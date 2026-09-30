# Document Search API

Простой полнотекстовый поисковик по документам на базе **FastAPI**, **PostgreSQL** и **Elasticsearch**.

## Стек

- Python 3.12
- FastAPI (async)
- PostgreSQL 16
- Elasticsearch 8.11.0
- Docker & Docker Compose

## Структура проекта

```text
document-search/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Точки входа, эндпоинты
│   ├── config.py                # Настройки из .env (pydantic-settings)
│   ├── database.py              # SQLAlchemy async engine + сессии
│   ├── models.py                # ORM-модели (PostgreSQL)
│   ├── schemas.py               # Pydantic-схемы (запросы/ответы)
│   └── elasticsearch_client.py  # Работа с Elasticsearch
├── scripts/
│   ├── __init__.py
│   ├── load_data.py             # Загрузка данных из CSV в БД и ES
│   ├── check_db.py              # Проверка подключения к PostgreSQL
│   └── check_es.py              # Проверка подключения к Elasticsearch
├── tests/
│   ├── __init__.py
│   └── test_api.py              # Функциональные тесты (pytest + httpx)
├── data/
│   └── posts.csv                # Исходные данные (1500 документов)
├── docker-compose.yml           # Оркестрация app + db + elasticsearch
├── Dockerfile                   # Сборка образа приложения
├── requirements.txt             # Python-зависимости
├── pytest.ini                   # Конфигурация pytest
├── .env.example                 # Шаблон переменных окружения
├── .gitignore                   # Игнорируемые файлы для Git
├── .dockerignore                # Игнорируемые файлы для Docker-сборки
├── docs.json                    # OpenAPI-спецификация
└── README.md
```

## Быстрый старт

### 1. Клонирование и настройка

```bash
git clone https://github.com/sh0egaaze/document-search
cd document-search
cp .env.example .env
```

Отредактируйте файл `.env`, указав ваши параметры подключения к БД.

### 2. Запуск сервисов

```bash
docker compose up -d --build
```

Дождитесь, пока все контейнеры перейдут в статус healthy:

- **PostgreSQL** (~5 сек)
- **Elasticsearch** (~20 сек)
- **App** (запускается после готовности БД и ES)

### 3. Загрузка данных

```bash
docker compose exec app python -m scripts.load_data
```

Скрипт прочитает `data/posts.csv`, создаст таблицы в PostgreSQL, индекс в Elasticsearch и загрузит 1500 документов.

### 4. Проверка работы

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## API

### POST /search

Поиск документов по тексту с поддержкой русской морфологии и опечаток.

**Пример запроса:**
```json
{
  "query": "bmw"
}
```

**Пример ответа:**
```json
{
  "total": 3,
  "results": [
    {
      "id": 42,
      "rubrics": ["Авто", "Технологии"],
      "text": "...",
      "created_date": "2023-10-15T14:30:00"
    }
  ]
}
```

### DELETE /documents/{id}

Удаление документа из БД и поискового индекса по его `id`.

**Пример:** `DELETE /documents/42`

## Тесты

```bash
docker compose exec app pytest tests/test_api.py -v
```

## Остановка

```bash
docker compose down
```

Для полного удаления данных (тома БД и ES):
```bash
docker compose down -v
```