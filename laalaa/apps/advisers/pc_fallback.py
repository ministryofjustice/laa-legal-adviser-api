from postcodes import PostCoder


class PostcodePlaceholder:

    def __init__(self):
        self.postcode = None
        self.longitude = None
        self.latitude = None


def format_postcode(postcode):
    formatted_pc = postcode.replace(' ', '')
    formatted_pc = formatted_pc.lower()
    return formatted_pc


def geocode(postcode):

    # Format postcode as lower-case, without spaces
    formatted_pc = format_postcode(postcode)

    # Read from Postcodes.io API
    postcode_data = PostCoder().get(formatted_pc)

    # Has Postcodes.io yielded a result?
    if postcode_data:
        result = PostcodePlaceholder()
        result.postcode = format_postcode(postcode_data['postcode'])
        result.latitude = postcode_data['geo']['lat']
        result.longitude = postcode_data['geo']['lng']
        return result

    return None






