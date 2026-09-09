# RudenskGNS

Система автоматизации производственного процесса обслуживания и учёта газовых баллонов (ГНС Руденск).

Стек: Django / Daphne (ASGI), PostgreSQL, Redis, Celery, DRF, JWT.

Основные приложения: `core`, `filling_station`, `carousel`, `ttn`, `mobile`.

## Установка и запуск

Зависимости управляются через **[uv](https://docs.astral.sh/uv/)** (`pyproject.toml` + `uv.lock`). Требуется **Python 3.12**.

1. Клонировать репозиторий и перейти в корень.
2. Установить uv и выполнить `uv sync` (для разработки: `uv sync --group dev`).
3. Активировать окружение: `.venv\Scripts\activate` (Windows) или `source .venv/bin/activate`.
4. Создать `GNS/.env` (`SECRET_KEY`, `DEBUG`, параметры БД, Miriada и т.д.).
5. Из каталога `GNS`:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   daphne GNS.asgi:application --bind 0.0.0.0 -p 8000 --application-close-timeout 10
   ```
6. UI: `http://localhost:8000`, Swagger: `http://localhost:8000/api/swagger/`.

## Redis

- **DB 0** (`CELERY_BROKER_URL`): брокер Celery.
- **DB 1** (Django `CACHES`): кэш приложения, FIFO-очереди баллонов для карусели `reader_<N>_balloon_queue`, метрики `carousel_<N>_metric_<name>`.

## Celery

Из каталога `GNS`:

```bash
celery -A GNS worker --loglevel=info --concurrency=8
celery -A GNS beat --loglevel=info
```

### Периодические задачи

- **fetch_current_ttn_from_miriada** (`ttn.tasks.fetch_current_ttn_from_miriada`) — синхронизация текущих ТТН из Мириады; ежедневно в 22:00.

При закрытии партии баллонов вызывается `ttn.services.close_ttn_in_miriada`.

## RFID (FEIG Notification Mode)

Процесс RFID стартует из ASGI (`GNS/GNS/asgi.py`) как subprocess:

```bash
python -m filling_station.management.commands.rfid_utils.feig_protocol
```

Также: `python manage.py rfid_process`.

- Слушатель TCP (по умолчанию `0.0.0.0:8002`, env `RFID_NOTIFICATION_LISTEN_HOST` / `RFID_NOTIFICATION_LISTEN_PORT`).
- Конфигурация ридеров — таблица `ReaderSettings` (IP/порт).
- Обработка меток и оптики — прямые вызовы `filling_station.services` через `sync_to_async`.
- Индикация на ридере: FEIG `SET_OUTPUT` (зелёный свет / мигание), без OPC.
- Статусы в Мириаду: считыватели партий `{2,3,4,5,6}`, наполнение `{8}` (ридер 5 — склад / `balloontosklad`).

## Карусель наполнения (NPort TCP)

Один subprocess на все активные карусели:

```bash
python manage.py carousel_process
# или
python -m carousel.management.commands.carousel.main
```

Запускается также из ASGI вместе с RFID.

Один asyncio-процесс читает активные записи `CarouselSettings` (`is_active`, заполненные `tcp_host` и `rfid_reader`). Каждая карусель — TCP-клиент к своему NPort W2150A (режим TCP Server). COM/pyserial не используются.

**Настройки NPort (web console):**

| Параметр | Значение |
|---|---|
| Operation Mode | `TCP Server` |
| TCP port | тот же, что в `CarouselSettings.tcp_port` (часто `4001`) |
| Max connection | `1` |
| Serial | `9600 8N1` (+ RS-485) |
| Inactivity time | `0` |

**`CarouselSettings`** (admin / UI `/carousel/settings/`):

| Поле | Назначение |
|---|---|
| `number` | номер карусели (1..3, unique) |
| `name` | название в UI |
| `tcp_host` / `tcp_port` | IP и порт NPort |
| `rfid_reader` | FK на `ReaderSettings` (очередь паспортов) |
| `is_active` | включать в listener |
| весовые диапазоны / корректоры | политика постов |

После смены NPort / `is_active` / `number` перезапустите listener. Seed трёх записей (number 1..3) — data-миграция `carousel.0006`.

Паспорта баллонов передаются от RFID через Redis FIFO `reader_<N>_balloon_queue`.

## ТТН

Только баллонные документы: `BalloonTtn` и кэш текущих ТТН Мириады `MiriadaTtn`. Нет Auto/Railway TTN.

Веб: `/ttn/balloons/…`.

## Партии баллонов

Единая модель `BalloonsBatch` (`batch_type` `l`/`u`). Legacy `BalloonsLoadingBatch` / `BalloonsUnloadingBatch` оставлены в БД для миграций, в коде не используются.
