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


