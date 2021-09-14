class AbortImportMixin(object):
    def abort_import(self, obj):
        obj.abort()
        self.cleanup_celery(obj)

    def cleanup_celery(self, obj):
        app = self.get_celery_app()
        app.control.revoke(obj.task_id, terminate=True)
        app.control.purge()
        stats = app.control.inspect()
        self.cancel_geocoding_tasks(app, stats.reserved())
        self.cancel_geocoding_tasks(app, stats.active())

    def cancel_geocoding_tasks(self, app, tasks):
        for worker in tasks:
            for task in tasks[worker]:
                if task["name"] == "advisers.tasks.GeocoderTask":
                    print("Cancelling task {} of {}".format(task["id"], task["name"]))
                    app.control.revoke(task["id"], terminate=True)

    def get_celery_app(self):
        from celery import Celery

        app = Celery("laalaa")
        app.config_from_object("django.conf:settings", namespace="CELERY")
        return app
