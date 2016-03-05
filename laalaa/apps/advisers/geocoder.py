import re
import postcodeinfo
from postcodes import PostCoder


class GeocoderError(Exception):
    pass


class PostcodePlaceholder:

    def __init__(self):
        self.longitude = None
        self.latitude = None


class PostcodeNotFound(GeocoderError):
    def __init__(self, postcode, *args, **kwargs):
        super(PostcodeNotFound, self).__init__(*args, **kwargs)
        self.postcode = postcode


def geocode_fallback(postcode):

    result = PostcodePlaceholder()

    print '******CHECKING ' + postcode + 'AT POSTCODES.IO********'
    postcode_data = PostCoder().get(postcode)
    print '******RESPONSE:'
    print result

    result.latitude = postcode_data['geo']['lat']
    result.longitude = postcode_data['geo']['lng']

    return result


def geocode(postcode):
    try:
        if len(postcode) < 5:
            result = postcodeinfo.Client().lookup_partial_postcode(postcode)
        else:
            result = postcodeinfo.Client().lookup_postcode(postcode)

        if not result.valid:
            print '******Result not valid********'
            result = geocode_fallback(postcode)

            if not result.latitude:
                raise PostcodeNotFound(postcode)

        return result
    except postcodeinfo.PostcodeInfoException as e:
        raise GeocoderError(e)
