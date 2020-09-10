from celery.schedules import crontab
from application import celery
from .prediction import predict_machine_failure

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=0, hour=0),
        predict_machine_failure
    )