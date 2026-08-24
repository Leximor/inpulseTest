
## Задание 1 — `01_django_process_transactions/`

Нужно атомарно:
1. перевести все транзакции пользователя в `processed`;
2. выставить `profile.has_processed_transactions = True`;
3. при ошибке откатить всё;
4. **без** `bulk_update`, только `save()` и ORM.

Модели в `models.py`
Сама логика в `services.py`:

- `@transaction.atomic` — одна транзакция БД. Любой exception (нет профиля, ошибка `save()`) даёт rollback и статусов, и флага.
- `select_for_update()` блокирует строки профиля и транзакций до COMMIT. Иначе два воркера могут одновременно проставить статусы и получить гонку.
- Цикл + `save()` — как просили, без `bulk_update` / `QuerySet.update()`.
- `update_fields` сужает UPDATE до нужных колонок. У `updated_at` стоит `auto_now=True`, поэтому timestamp обновится.

Сначала лочится профиль, потом транзакции — одинаковый порядок блокировок, меньше шанс deadlock.

## Задание 2 — `02_celery_location_update/`

Падение:

```text
TypeError: Object of type Decimal is not JSON serializable
```

**Причина.** `json.dumps(location_data)` использует стандартный encoder. Он умеет только `str`, `int`, `float`, `bool`, `None`, `list`, `dict`. `Decimal` из Django `DecimalField` (координаты, суммы) в этот набор не входит. То же самое с `datetime` и `UUID` — поэтому ошибка «иногда», только когда в словаре есть такие объекты.

Сигнатуру таска менять нельзя, ручные `isinstance` на входе тоже нельзя.

**Исправление** — отдать сериализацию `DjangoJSONEncoder`. Он сам рекурсивно обходит вложенный dict и кодирует `Decimal`, `datetime`/`date`/`time`, `UUID`, lazy `Promise`. На входе ничего не проверяем:

```

`Decimal` уходит строкой, не `float` — точность не теряется. Ключ как в задании: `user:{user_id}:last_loc`.

---

## Задание 3 — `03_nginx_https_dynamic_domain/`

Nginx **не читает** `ENV` в `server_name` и путях сертификатов. Если зашить домен в image, смена `DOMAIN` потребует rebuild. Поэтому `nginx.conf` — это шаблон: `${DOMAIN}` подставляется **при старте контейнера**.

В конфиге:
- `:80` → redirect на HTTPS, плюс `/.well-known/acme-challenge/` для Let's Encrypt;
- `:443` → SSL из `/etc/letsencrypt/live/${DOMAIN}/...` (стандартный путь certbot);
- `proxy_pass` на Gunicorn `web:8000` с заголовками `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`.

Подстановка в `docker-entrypoint.sh`:

```sh
envsubst '${DOMAIN}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
```
 `envsubst` ограничен `'${DOMAIN}'`. Иначе он снесёт nginx-переменные `$host`, `$scheme`, `$request_uri`.

Скрипт кладётся в `/docker-entrypoint.d/` официального образа nginx — entrypoint сам выполнит его до старта. Image не пересобирается: меняется только `DOMAIN=app.example.com` в compose.

Сертификаты монтируются с хоста целиком (`/etc/letsencrypt`), а не только `live/`: certbot держит там симлинки в `archive/`.

Смена домена: новый `DOMAIN`, сертификат уже лежит по пути certbot, `docker compose up -d nginx`.

---
