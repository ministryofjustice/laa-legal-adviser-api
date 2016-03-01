import re
import postcodeinfo


class GeocoderError(Exception):
    pass


class PostcodeNotFound(GeocoderError):
    def __init__(self, postcode, *args, **kwargs):
        super(PostcodeNotFound, self).__init__(*args, **kwargs)
        self.postcode = postcode


def geocode(postcode):
    try:
        if len(postcode) < 5:
            result = postcodeinfo.Client().lookup_partial_postcode(postcode)
        else:
            result = postcodeinfo.Client().lookup_postcode(postcode)

        if not result.valid:
            raise PostcodeNotFound(postcode)
        return result
    except postcodeinfo.PostcodeInfoException as e:
        raise GeocoderError(e)
