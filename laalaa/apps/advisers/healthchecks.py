from django.conf import settings

from moj_irat.healthchecks import HealthcheckResponse, JsonUrlHealthcheck, \
    UrlHealthcheck, registry

registry.register_healthcheck(UrlHealthcheck(
    name='postcodes.io',
    url='%(base_url)s/postcxodes/SW1A1AA' % {
        'base_url': settings.POSTCODES_IO_URL,
    },
    headers={'Content-Type': 'application/json'},
))