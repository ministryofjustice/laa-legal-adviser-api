from django.conf import settings
from moj_irat.healthchecks import HealthcheckResponse, UrlHealthcheck, registry

from tasks import BrokerConnectionException, NoWorkersException, check_workers


class CeleryWorkersHealthcheck(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        try:
            check_workers()
        except NoWorkersException:
            return self.error_response("No running workers were found.")
        except BrokerConnectionException as e:
            msg = str(e)
            msg += ". Check that the message broker is running."
            return self.error_response(msg)
        except ImportError as e:
            return self.error_response(str(e))
        else:
            return self.success_response()

    def error_response(self, error):
        return HealthcheckResponse(self.name, False, error=error)

    def success_response(self):
        return HealthcheckResponse(self.name, True)


registry.register_healthcheck(
    UrlHealthcheck(name="postcodes.io", url="{}/postcodes/SW1A1AA".format(settings.POSTCODES_IO_URL))
)

registry.register_healthcheck(CeleryWorkersHealthcheck(name="workers"))
