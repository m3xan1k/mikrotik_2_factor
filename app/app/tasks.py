from celery import shared_task

from timecheck import TimeChecker


@shared_task
def check_exceed_unconfirmed_connections():
    TimeChecker.run()
