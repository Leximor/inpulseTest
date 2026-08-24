from celery import Celery

celery_app = Celery("location")
celery_app.conf.update(
    broker_url="redis://localhost:6379/1",
    result_backend="redis://localhost:6379/1",
)
