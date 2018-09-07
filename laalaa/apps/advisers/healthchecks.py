from django.conf import settings
from moj_irat.healthchecks import HealthcheckResponse, UrlHealthcheck, registry

class CeleryWorkersHealthcheck(object):
    def __init__(self, name):
        self.name = name
    
    def __call__(self, *args, **kwargs):
        import os
        from celery import Celery
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laalaa.settings')
        from django.conf import settings
        
        try:
            app = Celery('laalaa')
            app.config_from_object('django.conf:settings')
            app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

            stats = app.control.inspect().stats()
            if not stats:
                return self.error_response('No running workers were found.')
            workers = stats.values()
            if not workers:
                return self.error_response('No workers running.')
        except IOError as e:
            msg = str(e)
            msg += '. Check that the message broker is running.'
            return self.error_response(msg)
        except ImportError as e:
            return self.error_response(str(e))
        return self.success_response()
        
    def error_response(self, error):
        return HealthcheckResponse(self.name, False, error=error)
    
    def success_response(self):
        return HealthcheckResponse(self.name, True)

registry.register_healthcheck(UrlHealthcheck(
    name='postcodes.io',
    url='%(base_url)s/postcodes/SW1A1AA' % {
        'base_url': settings.POSTCODES_IO_URL,
    },
))
        
registry.register_healthcheck(CeleryWorkersHealthcheck(
    name='workers'
))
