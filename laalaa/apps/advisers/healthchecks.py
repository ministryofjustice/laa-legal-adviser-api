from django.conf import settings
from moj_irat.healthchecks import HealthcheckResponse, UrlHealthcheck, registry


def get_stats():
    from celery import Celery

    app = Celery("laalaa")
    app.config_from_object("django.conf:settings")
    return app.control.inspect().stats()


class CeleryWorkersHealthcheck(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):

        try:
            stats = get_stats()

            if not stats:
                return self.error_response("No running workers were found.")

            workers = stats.values()
            if not workers:
                return self.error_response("No workers running.")

        except IOError as e:
            msg = str(e)
            msg += ". Check that the message broker is running."
            return self.error_response(msg)

        except ImportError as e:
            return self.error_response(str(e))

        return self.success_response()

    def error_response(self, error):
        return HealthcheckResponse(self.name, False, error=error)

    def success_response(self):
        return HealthcheckResponse(self.name, True)


registry.register_healthcheck(
    UrlHealthcheck(name="postcodes.io", url="{}/postcodes/SW1A1AA".format(settings.POSTCODES_IO_URL))
)

registry.register_healthcheck(CeleryWorkersHealthcheck(name="workers"))
