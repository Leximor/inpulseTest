import json

from django.core.serializers.json import DjangoJSONEncoder
from redis import Redis

from .celery_app import celery_app

redis_client = Redis.from_url("redis://localhost:6379/0", decode_responses=True)


@celery_app.task
def send_location_update(user_id: int, location_data: dict):
    """Сохранить последнюю локацию пользователя в Redis.

    Причина ошибки в проде: json.dumps() по умолчанию сериализует только
    str/int/float/bool/None/list/dict. Decimal (и datetime, UUID) в этот
    набор не входят — отсюда TypeError.

    Исправление: cls=DjangoJSONEncoder. Он рекурсивно обходит любой
    вложенный словарь и сам обрабатывает Decimal, datetime, date, time,
    UUID, Promise. Сигнатура таска не меняется, ручных проверок типов
    на входе нет.
    """
    redis_client.set(
        f"user:{user_id}:last_loc",
        json.dumps(location_data, cls=DjangoJSONEncoder),
    )
