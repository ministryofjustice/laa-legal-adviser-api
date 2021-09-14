from django.core.management.base import BaseCommand
from advisers.models import Import


class Command(BaseCommand):
    help = "Abort last Import job"

    def handle(self, *args, **options):
        last = Import.objects.abort_last()
        app = self.get_celery_app()
        app.control.revoke(last.task_id, terminate=True)
        app.control.purge()

    def get_celery_app(self):
        from celery import Celery

        app = Celery("laalaa")
        app.config_from_object("django.conf:settings", namespace="CELERY")
        return app
