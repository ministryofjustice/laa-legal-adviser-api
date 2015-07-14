from django.conf import settings
from django.contrib.gis.geos import Point
import postcodeinfo


class GeocoderError(Exception):
    pass


class PostcodeNotFound(GeocoderError):
    def __init__(self, postcode, *args, **kwargs):
        super(PostcodeNotFound, self).__init__(*args, **kwargs)
        self.postcode = postcode


def geocode(postcode):
    try:
        return postcodeinfo.Client().lookup_postcode(postcode)
    except postcodeinfo.NoResults:
        raise PostcodeNotFound(postcode)
    except postcodeinfo.PostcodeInfoException as e:
        raise GeocoderError(e)
