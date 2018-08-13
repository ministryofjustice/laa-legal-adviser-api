import json
import logging
import requests


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


def lookup_postcode(postcode):
    raw = requests.get('http://api.postcodes.io/postcodes/?q={postcode}&limit=1'.format(postcode=postcode))
    return json.loads(raw.text)


def geocode(postcode):
    logger = logging.getLogger(__name__)
    try:
        result = lookup_postcode(postcode)
        if result['status'] == 404:
            raise PostcodeNotFound(postcode)

        if result['status'] >= 400:
            logger.warn('Postcode lookup failed with response "{0}"'.format(result))
            raise GeocoderError(result)

        return result_to_postcode(result['result'][0])
    except requests.exceptions.RequestException as e:
        logger.error('Postcode lookup failed with error "{0}"'.format(repr(e)))
        raise GeocoderError('Caused by ' + repr(e))
