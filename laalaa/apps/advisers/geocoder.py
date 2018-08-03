import re
import postcodeinfo
import pc_fallback


class GeocoderError(Exception):
    pass


class PostcodeNotFound(GeocoderError):
    def __init__(self, postcode, *args, **kwargs):
        super(PostcodeNotFound, self).__init__(*args, **kwargs)
        self.postcode = postcode


def geocode(postcode):
    try:
        postcode_client = postcodeinfo.Client(timeout = 30)
        if len(postcode) < 5:
            result = postcode_client.lookup_partial_postcode(postcode)
        else:
            result = postcode_client.lookup_postcode(postcode)

        if not result.valid:
            result = pc_fallback.geocode(postcode)

            if not result:
                raise PostcodeNotFound(postcode)

        return result
    except postcodeinfo.PostcodeInfoException as e:
        raise GeocoderError(e)
