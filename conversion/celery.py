import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conversion.settings')

app = Celery('conversion')
# app.conf.broker_url = 'amqp://guest:guest@localhost:5672//'
app.conf.broker_url = 'amqp://guest:guest@rabbitmq:5672//'
app.conf.result_backend = 'rpc://'
app.autodiscover_tasks()