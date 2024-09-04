import json
import logging
import requests
from django.conf import settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


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


def normalise_postcode(postcode):
    formatted_pc = postcode.replace(" ", "")
    formatted_pc = formatted_pc.lower()
    return formatted_pc


def result_to_postcode(result):
    postcode = PostcodePlaceholder()
    postcode.postcode = normalise_postcode(result["postcode"])
    postcode.longitude = result["longitude"]
    postcode.latitude = result["latitude"]
    return postcode


def lookup_postcode(postcode):
    normalised_postcode = normalise_postcode(postcode)

    session = requests.Session()

    retry_strategy = Retry(total=5, backoff_factor=0.1)
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    raw = session.get(
        "{host}/postcodes/?q={postcode}&limit=1".format(host=settings.POSTCODES_IO_URL, postcode=normalised_postcode)
    )
    return json.loads(raw.text)


def geocode(postcode):
    logger = logging.getLogger(__name__)
    try:
        result = lookup_postcode(postcode)
        if result["status"] == 404:
            raise PostcodeNotFound(postcode)

        if result["status"] >= 400:
            logger.warn('Postcode lookup failed with response "{0}"'.format(result))
            raise GeocoderError(result)

        if not result["result"]:
            raise PostcodeNotFound(postcode)

        return result_to_postcode(result["result"][0])
    except requests.exceptions.RequestException as e:
        logger.error('Postcode lookup failed with error "{0}"'.format(repr(e)))
        raise GeocoderError("Caused by " + repr(e))
