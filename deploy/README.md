# Деплой

Стек описан в двух compose-файлах в корне репозитория:

| Файл               | Назначение | Запуск |
| ------------------ | ---------- | ------ |
| `compose.dev.yaml`  | локальная разработка: бэкенд и фронтенд собираются из исходников, код смонтирован в контейнеры | `docker compose -f compose.dev.yaml --env-file .env.dev up -d` |
| `compose.prod.yaml` | сервер: готовые образы из реестра, HTTPS и certbot | `docker compose -f compose.prod.yaml --env-file .env.prod up -d` |

Переменные стека и секреты — в двух файлах в корне: `.env.dev` и `.env.prod`
(шаблоны `.example.env.dev` и `.example.env.prod`, подробно — `README.md`).

В этом каталоге — то, что монтируется в контейнеры или участвует в их сборке:

```
deploy/
├── nginx/
│   ├── nginx.conf                       главный конфиг (CORS-whitelist, gzip, логи)
│   ├── Dockerfile.dev, Dockerfile.prod  образы nginx
│   ├── sites/00-monolith.dev.conf       dev: прокси на backend:8000 и frontend:3000
│   ├── sites/00-monolith.prod.conf      prod: HTTPS, прокси на контейнеры по именам
│   ├── snippets/proxy.conf              общие proxy_set_header для всех локаций
│   ├── sites_old/                       конфиги микросервисной схемы, отключены
│   └── copies_of_external/              копии внешних конфигов, справочно
├── temporal/
│   ├── setup-schema.sh                  создаёт базы temporal и накатывает схемы
│   ├── create-namespace.sh              регистрирует namespace default
│   └── dynamicconfig/docker.yaml        dynamic config сервера Temporal
├── postgres/init/                       SQL для инициализации (сейчас не монтируется)
└── deploy.yml.disabled                  черновик GitHub Actions, НЕ включён (см. ниже)
```

---

## Локальный запуск

Нужен `.env.dev` в корне репозитория (пароль Postgres и ключи, шаблон — `.example.env.dev`)
и репозиторий фронтенда рядом:

```
~/projects/formulist/
├── AI-assistant-for-patents-monolithic/   ← этот репозиторий, отсюда запускается compose
└── Patent-Formulist-web-app/              ← фронтенд, путь меняется через FRONTEND_PATH
```

```bash
cp .example.env.dev .env.dev     # один раз, заполнить пароль и ключи
docker compose -f compose.dev.yaml --env-file .env.dev up -d --build
```

Миграции сведены в одну (`migrations/versions/cc266eb797f0_initial_schema.py`).
База, созданная старыми миграциями, с ней несовместима: сервис `migrations` упадёт
с `Can't locate revision`. Пересоздайте её вместе с данными:

```bash
docker compose -f compose.dev.yaml --env-file .env.dev down -v
docker compose -f compose.dev.yaml --env-file .env.dev up -d --build
```

После запуска:

| Сервис        | URL                   |
| ------------- | --------------------- |
| Фронтенд      | http://localhost      |
| Swagger (API) | http://localhost/docs |
| Temporal UI   | http://localhost:8233 |

### Повседневные команды

```bash
export COMPOSE_FILE=compose.dev.yaml COMPOSE_ENV_FILES=.env.dev   # один раз на сессию терминала

docker compose up -d --build backend     # пересобрать только бэкенд
docker compose up -d --build frontend    # только фронтенд
docker compose up -d backend worker      # после правки .env.dev: пересоздать
docker compose restart backend worker    # после правки config.yaml (смонтирован)
docker compose restart worker            # код смонтирован, но воркер сам не перезагружается
docker compose logs -f backend           # логи: backend | worker | frontend | nginx
docker compose logs --tail 50 backend
docker compose down                      # остановить
docker compose down -v                   # остановить и удалить данные БД
docker compose build --no-cache && docker compose up -d   # полная пересборка
```

Фронтенд в dev — это vite dev server (`Dockerfile.dev` фронтенда, порт 3000),
nginx проксирует на него `/`. Собранный `dist` используется только в prod.

---

## Как это работает

```
браузер
  │
  ▼ :80
nginx (formulinked-nginx)
  ├── /api/*  →  backend:8000  (formulinked-backend, FastAPI)
  └── /*      →  frontend:3000 (formulinked-frontend, vite dev server)

backend ──► postgres:5432 (formulinked-postgres)
   │
   └─ старт workflow ──► temporal:7233 (formulinked-temporal) ──► postgres: базы temporal, temporal_visibility
                                 ▲
worker (formulinked-worker) ─────┘ выполняет пайплайны: Роспатент, LLM, запись в postgres
```

### Лимиты запросов

nginx ограничивает по IP клиента вход и регистрацию (`limit_req`, зоны в начале
`sites/00-monolith.*.conf`). Сверх лимита отвечает `429`, до бэкенда запрос не доходит.

| Путь | В среднем | Подряд |
| --- | --- | --- |
| `POST /api/v2/users/registration` | 3 в минуту | 4 |
| `POST /api/v2/users/login` | 10 в минуту | 6 |

Конфиги сайтов смонтированы, поэтому после правки достаточно `restart nginx`.
Лимиты на запуск генерации и поиска — на уровне приложения, по пользователю.

### Сети

Контейнеры разделены по сетям: сервис видит только тех, с кем делит сеть.
Внутренние сети (`internal`) не имеют выхода в интернет, и порт из них
опубликовать нельзя: снаружи до таких контейнеров не достучаться, даже если
ошибиться в `ports:`. Поэтому блокировки на уровне Linux для них не нужны.

| Сеть | Тип | Кто в ней |
| --- | --- | --- |
| `edge` | обычная | nginx, frontend, backend/monolith |
| `database` | internal (в dev обычная) | postgres, backend, worker, temporal, temporal-setup, migrations |
| `temporal` | internal | temporal, backend, worker, temporal-namespace, temporal-ui |
| `worker` | обычная | worker: выход в интернет к Rospatent и LLM |
| `temporal-ui` | обычная | temporal-ui: только чтобы опубликовать порт на 127.0.0.1 |
| `certbot` | обычная, только prod | certbot: выход к Let's Encrypt, с nginx общие только тома |

Что из этого следует:
- nginx и frontend не видят postgres и Temporal;
- certbot не видит ни один контейнер;
- postgres и Temporal не ходят в интернет;
- снаружи открыты только порты nginx (80, 443). Порты API (8000), Temporal UI (8233)
  и в dev postgres (5432) открыты только на 127.0.0.1.

В dev `database` обычная, чтобы postgres был доступен с хоста на 127.0.0.1:5432
(DBeaver, DAO-тесты). Контейнеры находят друг друга по имени сервиса (`postgres`,
`backend`) или по `container_name` (`formulinked-monolith` в prod-конфиге nginx).

### Temporal

Фоновые пайплайны выполняет Temporal: см. `docs/adr/0005-background-pipelines-on-temporal.md`.

| Контейнер | Что делает |
| --- | --- |
| `temporal-setup` | один раз при старте: создаёт базы `temporal`, `temporal_visibility` и обновляет их схемы |
| `temporal` | сервер Temporal (`temporalio/server`) |
| `temporal-namespace` | один раз при старте: регистрирует namespace `default` |
| `temporal-ui` | веб-интерфейс, только на `127.0.0.1:8233` — авторизации нет |
| `worker` | воркер монолита: `python -m app.temporal.worker` |

- Сервер держит ~12 соединений к Postgres (пулы урезаны в `SQL_*_MAX_CONNS`), поэтому
  `max_connections` Postgres поднят до 50.
- На сервере UI открывается через туннель, см. [Служебные интерфейсы](#служебные-интерфейсы).
- Обновление Temporal: сменить теги образов `temporalio/*` — `temporal-setup` сам
  накатит новые версии схем при следующем запуске.

---

## Сервер

```bash
cd <каталог репозитория на сервере>
git pull origin prod
docker compose -f compose.prod.yaml --env-file .env.prod pull
docker compose -f compose.prod.yaml --env-file .env.prod up -d
```

В `.env.prod` должны быть заполнены `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`
(не короче 32 символов) и `ROSPATENT_API_KEY`. У них нет значений по умолчанию:
в `compose.prod.yaml` они записаны как `${VAR:?сообщение}`, и если переменная
пуста, Compose не запустит стек и выведет это сообщение.

`POSTGRES_PASSWORD` Postgres применяет только при создании тома. На сервере
с существующей базой укажите текущий пароль, а не новый.

Раньше файл лежал в `deploy/.env.prod`. На сервере перенесите его один раз:
`mv deploy/.env.prod .env.prod`.

Раньше все контейнеры были в общей сети `infrastructure-network`. После перехода
на отдельные сети `up -d` пересоздаст все контейнеры (короткий простой), а старую
сеть удалите вручную: `docker network rm infrastructure-network`.
Переменная `NETWORK_NAME` из `.env.prod` больше не используется.

Чтобы не повторять флаги: `export COMPOSE_FILE=compose.prod.yaml COMPOSE_ENV_FILES=.env.prod`.

### Служебные интерфейсы

Temporal UI и Swagger наружу не публикуются: их порты открыты только на
`127.0.0.1` сервера. Temporal UI без авторизации, а Swagger раскрывает схему API.
Доступ — через SSH-туннель с вашей машины:

```bash
ssh -N -L 8233:127.0.0.1:8233 -L 8000:127.0.0.1:8000 <пользователь>@<сервер>
```

Пока команда работает, открыты:

| Что | Адрес |
| --- | --- |
| Temporal UI | http://localhost:8233 |
| Swagger | http://localhost:8000/docs |

`-N` — только туннель, без оболочки; выход — Ctrl+C. Если локальный порт занят
(например, локальным dev-стеком), выберите другой:
`-L 18000:127.0.0.1:8000` → http://localhost:18000/docs.

Чтобы не вводить флаги, добавьте в `~/.ssh/config`:

```
Host formulist
    HostName <сервер>
    User <пользователь>
    LocalForward 8233 127.0.0.1:8233
    LocalForward 8000 127.0.0.1:8000
```

и подключайтесь `ssh -N formulist`.

### Имена томов

Compose больше не выводит префикс томов из имени папки: он задан явно
(`name: formulinked` + `*_VOLUME_NAME` в compose-файлах). При первом запуске
после переезда нужно указать в `.env.prod` фактические имена
существующих томов, иначе Compose создаст новые пустые — база и сертификаты
окажутся "потеряны":

```bash
docker volume ls | grep -e postgres -e certbot
```

### Что ещё не сделано

Эти пункты остались от репозитория-оркестратора и требуют отдельной работы:

1. **Миграции в prod.** В `compose.dev.yaml` есть сервис `migrations`
   (`alembic upgrade head` перед стартом бэкенда), в `compose.prod.yaml` его нет —
   на сервере миграции накатываются руками.
2. **CI деплоя.** `deploy.yml.disabled` — нерабочий черновик: потерян `#` в строке
   `git pull origin prod  Обновляем код`, фильтр `paths: ['app/', 'core/']` задан
   неверным шаблоном, используется `docker-compose` без `-f`/`--env-file`,
   а `docker system prune -af` сносит все образы на хосте. Перед включением
   (перенос в `.github/workflows/`) всё это нужно починить.
3. **Теги образов.** Prod тянет `muschketl/formulinked-*:latest` — непонятно,
   что развёрнуто, и нечем откатиться. Нужны теги по git sha.
