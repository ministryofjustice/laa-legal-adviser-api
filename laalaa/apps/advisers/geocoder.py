import json
import logging
import requests

from lib import PostCodeClient


class PostcodePlaceholder:

    def __init__(self):
        self.postcode = None
        self.longitude = None
        self.latitude = None


class GeocoderError(Exception):
    pass


class PostcodeNotFound(GeocoderError):
    def __init__(self, postcode, *args, **kwargs):
        super(PostcodeNotFound, self).__init__(*args, **kwargs)
        self.postcode = postcode


def format_postcode(postcode):
    formatted_pc = postcode.replace(' ', '')
    formatted_pc = formatted_pc.lower()
    return formatted_pc


def result_to_postcode(result):
    postcode = PostcodePlaceholder()
    postcode.postcode = format_postcode(result['postcode'])
    postcode.longitude = result['longitude']
    postcode.latitude = result['latitude']
    return postcode


def lookup_postcode(logger, postcode):
    # Partial lookup: http://api.postcodes.io/postcodes?q=SW1A1&limit=30
    client = PostCodeClient()
    result = json.loads(client.getLookupPostCode(postcode))

    if result['status'] == 404:
        raise PostcodeNotFound(postcode)

    if result['status'] >= 400:
        logger.warn('Postcode lookup failed with response "{0}"'.format(result))
        raise GeocoderError(result)

    return result_to_postcode(result['result'])


def geocode(postcode):
    logger = logging.getLogger(__name__)
    try:
        return lookup_postcode(logger, postcode)
    except requests.exceptions.RequestException as e:
        logger.error('Postcode lookup failed with error "{0}"'.format(repr(e)))
        raise GeocoderError('Caused by ' + repr(e))
