import os
import requests
from django.http import JsonResponse
from django.conf import settings


def ping(request):

    res = {
        "version_number": os.environ.get('APPVERSION'),
        "build_date": os.environ.get('APP_BUILD_DATE'),
        "commit_id": os.environ.get('APP_GIT_COMMIT'),
        "build_tag": os.environ.get('APP_BUILD_TAG')
    }

    return JsonResponse(res)


def healthcheck(request):

    # Default status is `DOWN` for all services
    health = {
        'postcodes.io': {
            'status': 'DOWN',
            'endpoint': settings.POSTCODES_IO_URL
        }
    }

    # Test postcodeinfo
    try:
        req = requests.get('{0}/postcodes/SW1A1AA'.format(settings.POSTCODES_IO_URL))
        if req.status_code == 200:
            health['postcodes.io']['status'] = 'UP'
    except:
        pass

    if health['postcodes.io']['status'] == 'UP':
        return JsonResponse(health, status=200)
    else:
        return JsonResponse(health, status=503)
