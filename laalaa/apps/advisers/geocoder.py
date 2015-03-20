from django.conf import settings
from django.contrib.gis.geos import Point
import json
import requests


def geocode(postcode):
    try:
        response = requests.get(
            '{host}/postcodes/{postcode}'.format(
                host=settings.ADDRESSFINDER_API_HOST,
                postcode=postcode),
            headers={
                'Authorization': 'Token {0}'.format(
                    settings.ADDRESSFINDER_API_TOKEN)},
            timeout=(2.0, 5.0))
        data = json.loads(response.text)
        return Point(*data['coordinates'])
    except (requests.exceptions.ConnectionError,
            requests.exceptions.Timeout):
        return Point(0.0, 0.0)
