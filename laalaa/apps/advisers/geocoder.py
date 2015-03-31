import requests
from django.conf import settings
from django.contrib.gis.geos import Point


class GeocoderError(Exception):
    pass


class PostcodeNotFound(GeocoderError):
    def __init__(self, postcode, *args, **kwargs):
        super(PostcodeNotFound, self).__init__(*args, **kwargs)
        self.postcode = postcode


def geocode(postcode):
    try:
        response = requests.get((
            '{host}/addresses/?postcode={postcode}&'
            'fields=postcode,point').format(
                host=settings.ADDRESSFINDER_API_HOST,
                postcode=postcode),
            headers={
                'Authorization': 'Token {0}'.format(
                    settings.ADDRESSFINDER_API_TOKEN)},
            timeout=5)
        try:
            return response.json()[0]
        except IndexError:
            raise PostcodeNotFound(postcode)
    except (requests.exceptions.ConnectionError,
            requests.exceptions.Timeout) as e:
        raise GeocoderError(e)
