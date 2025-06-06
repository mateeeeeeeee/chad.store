import os
from celery import Celery, shared_task

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# run celery with
# celery -A config worker -P threads --loglevel=info

@shared_task
def debug_task(x,y):
    return x + y

