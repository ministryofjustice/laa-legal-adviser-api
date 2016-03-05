from postcodes import PostCoder


class PostcodePlaceholder:

    def __init__(self):
        self.longitude = None
        self.latitude = None


def geocode(postcode):

    result = PostcodePlaceholder()

    print '******CHECKING ' + postcode + 'AT POSTCODES.IO********'
    postcode_data = PostCoder().get(postcode)
    print '******RESPONSE:'
    print result

    result.latitude = postcode_data['geo']['lat']
    result.longitude = postcode_data['geo']['lng']

    return result

