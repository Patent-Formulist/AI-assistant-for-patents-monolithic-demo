# AI Assistant for Patents

Backend-сервис на FastAPI для автоматизации работы с патентными заявками: поиск
аналогов, извлечение и сравнение признаков, оценка патентоспособности и генерация
проекта заявки с помощью LLM.

> Это демонстрационная версия репозитория: содержит исходный код бэкенда,
> архитектурные решения и инфраструктуру запуска.

## О демонстрационной версии

| Что | Состояние |
|---|---|
| `storage/prompts/` | заглушки с описанием переменных шаблона |
| `storage/legal/` | заглушки документов |
| `docs/` | заголовки разделов без содержимого |
| `test/` | скелеты тестов (все пропущены) |
| `app/service/{billing,payment,organization,legal, identify, statistics}` | сигнатуры и docstring'и есть, реализация скрыта |
| `compose.dev.yaml`, `compose.prod.yaml` | сокращённые конфигурации |

Приложение импортируется и запускается (97 маршрутов); функции с заглушками
отвечают `NotImplementedError`.

## Что умеет

| Возможность | Описание |
|---|---|
| **Поиск аналогов** | Поиск патентов-аналогов по Роспатенту и внешним источникам, сохранение метаданных |
| **Признаки и статистика** | Извлечение признаков из патента и аналогов, матрица совпадений, частотный анализ |
| **Идентичность прототипа** | Сопоставление признаков заявки с прототипом |
| **Генерация заявки** | Формирование текста заявки в формате, совместимом с требованиями Роспатента |
| **Чертежи** | Генерация перечня элементов и распределения фигур |
| **Экспорт** | Выгрузка таблиц и результатов в CSV/XLSX |
| **Аккаунты и организации** | JWT-аутентификация, подтверждение email, организации с ролями и приглашениями |
| **Биллинг** | Балансы, холды и списания за пайплайны, пополнение через ЮKassa, возвраты |
| **Правовые документы** | Версионированные политики и согласия пользователей |
| **Наблюдаемость** | Health-check, heartbeat воркера, Sentry, алерты в Telegram |

## Архитектура

```
Клиент ─── nginx ─── FastAPI (app/http)
                          │
                          ├── Бизнес-логика (app/service)
                          ├── Ядро: модели, DTO, домен (core/)
                          └── PostgreSQL (core/db)
                          │
                          └── Temporal (app/temporal)
                                └── worker: пайплайны поиска, статистики, генерации
```

Длинные операции (поиск аналогов, статистика, генерация заявки) выполняются
фоновыми пайплайнами во внешнем воркере Temporal. API только создаёт задачу и
стартует workflow — статус хранится в таблицах `jobs` и `tasks`.

Подробнее: [`docs/architecture/overview.md`](docs/architecture/overview.md) и
[`docs/adr/`](docs/adr/).

## Стек

- **Python 3.12**, FastAPI, Pydantic v2
- **SQLAlchemy 2.0** + Alembic (asyncpg), advanced-alchemy
- **Temporal** — фоновые пайплайны
- **uv** — управление зависимостями (`pyproject.toml` + `uv.lock`)
- **Docker Compose** — dev и prod стеки
- **pytest / ruff** — тесты и линтер

## Быстрый старт

Нужен Docker и Docker Compose.

```bash
cp .example.env.dev .env.dev
# заполнить POSTGRES_PASSWORD, JWT_SECRET_KEY, ROSPATENT_API_KEY (.env.dev)

docker compose -f compose.dev.yaml --env-file .env.dev up -d --build
```

После запуска:

| Адрес | Что это |
|---|---|
| http://localhost/ | API через nginx |
| http://localhost/docs | Swagger UI |
| http://localhost/health | Health-check: `{"status":"ok","checks":{"database":"ok","temporal":"ok"}}` |
| http://localhost:8233 | Temporal UI |

Миграции применяются автоматически контейнером `migrations`. Схема сведена в одну
начальную миграцию, поэтому базу от более старых версий нужно пересоздать:

```bash
docker compose -f compose.dev.yaml --env-file .env.dev down -v
```

Фронтенд — отдельный проект; путь к нему задаётся через `FRONTEND_PATH`
(по умолчанию `../Patent-Formulist-web-app`).

## Разработка без Docker

```bash
# установить uv: https://docs.astral.sh/uv/
uv sync                                        # зависимости + dev-группа
uv run pytest                                  # тесты (DAO-тестам нужен Postgres)
uv run ruff check . && uv run ruff format --check .
```

Настройки читаются один раз при старте процесса: `.env` + `config.yaml`
(валидация через pydantic-settings). После правки `.env.dev` контейнеры нужно
пересоздать (`up -d`), после правки `config.yaml` — достаточно `restart`.

## Структура

```
app/            HTTP-слой и бизнес-логика
  http/           роуты, request/response-модели
  service/        сервисы: анализы, статистика, LLM, биллинг
  temporal/       workflows, activities, воркер
core/           ядро: модели БД, домен, DTO, настройки, логирование
migrations/     Alembic
docs/           архитектура, ADR, гайды разработки
deploy/         nginx, postgres, temporal (конфиги для контейнеров)
scripts/        служебные скрипты (ключи, администраторы)
test/           тесты
```

## Документация

- [Обзор архитектуры](docs/architecture/overview.md)
- [Поток данных](docs/architecture/data-flow.md)
- [Обработка ошибок](docs/architecture/error-handling.md)
- [Шифрование данных](docs/architecture/data-encryption.md)
- [Архитектурные решения (ADR)](docs/adr/)
- [Стандарты кода](docs/development/coding-standards.md), [миграции](docs/development/migrations.md), [тестирование](docs/development/testing.md)
- [Деплой](deploy/README.md)

## Лицензия

См. [LICENSE](LICENSE).
