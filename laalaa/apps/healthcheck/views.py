import requests
from django.http import JsonResponse
from django.conf import settings
from django.db import connections


def ping(request):

    res = {
        "version_number": None,
        "build_date": None,
        "commit_id": None,
        "build_tag": None
    }

    # Get version details
    try:
        res['version_number'] = str(open("{0}/../VERSION".format(settings.PROJECT_ROOT)).read().strip())
        res['commit_id'] = res['version_number']
        res['build'] = res['version_number']
    except IOError:
        pass

    # Get build tag
    try:
        res['build_tag'] = str(open("{0}/../BUILD_TAG".format(settings.PROJECT_ROOT)).read().strip())
    except IOError:
        pass

    # Get build date
    try:
        res['build_date'] = str(open("{0}/../BUILD_DATE".format(settings.PROJECT_ROOT)).read().strip())
    except IOError:
        pass

    return JsonResponse(res)


def healthcheck(request):

    # Default status is `DOWN` for all services
    health = {
        'addressfinder': {
            'status': 'DOWN',
            'endpoint': settings.ADDRESSFINDER_API_HOST
        },
        'database': {
            'status': 'DOWN'
        }
    }

    # Test address finder
    try:
        headers = {'Authorization': 'Token {0}'.format(settings.ADDRESSFINDER_API_TOKEN)}
        req = requests.get('{0}/addresses/?postcode=sw1a1aa'.format(settings.ADDRESSFINDER_API_HOST), headers=headers)
        if req.status_code == 200:
            health['addressfinder']['status'] = 'UP'
    except:
        pass

    # Test database connection
    try:
        conn = connections['default']
        conn.cursor()
        health['database']['status'] = 'UP'
    except OperationalError:
        pass

    if health['database']['status'] == 'UP' and health['addressfinder']['status'] == 'UP':
        return JsonResponse(health, status=200)
    else:
        return JsonResponse(health, status=503)