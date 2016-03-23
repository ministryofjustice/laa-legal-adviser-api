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
        'postcodeinfo': {
            'status': 'DOWN',
            'endpoint': settings.POSTCODEINFO_API_URL
        }
    }

    # Test postcodeinfo
    try:
        headers = {'Authorization': 'Token {0}'.format(
            settings.POSTCODEINFO_AUTH_TOKEN)}
        req = requests.get(
            '{0}/addresses/?postcode=sw1a1aa'.format(
                settings.POSTCODEINFO_API_URL),
            headers=headers)
        if req.status_code == 200:
            health['postcodeinfo']['status'] = 'UP'
    except:
        pass

    if health['postcodeinfo']['status'] == 'UP':
        return JsonResponse(health, status=200)
    else:
        return JsonResponse(health, status=503)
