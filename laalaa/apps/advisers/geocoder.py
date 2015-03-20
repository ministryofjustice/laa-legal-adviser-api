from django.conf import settings
from django.contrib.gis.geos import Point
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
            timeout=5)
        try:
            data = response.json()
            return Point(*data['coordinates'])
        except ValueError:
            print 'WARNING: failed to geocode postcode %s' % postcode
            return Point(0.0, 0.0)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.Timeout):
        return Point(0.0, 0.0)
