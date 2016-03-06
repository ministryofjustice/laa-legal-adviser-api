from postcodes import PostCoder
from advisers.models import TemporaryPostcodes


class PostcodePlaceholder:

    def __init__(self):
        self.postcode = None
        self.longitude = None
        self.latitude = None


def geocode(postcode):

    result = check_temp_table(postcode)

    if result:
        print '******GEOCODE - POSTCODE FOUND IN TEMPORARY TABLE*********'
        return result
    else:
        result = PostcodePlaceholder()
        print '******GEOCODE - POSTCODE NOT FOUND IN TEMPORARY TABLE*********'
        print '******CHECKING ' + postcode + 'AT POSTCODES.IO********'
        postcode_data = PostCoder().get(postcode)
        print '******POSTCODES.IO RESPONSE:'
        print result

        result.postcode = postcode_data['postcode']
        result.latitude = postcode_data['geo']['lat']
        result.longitude = postcode_data['geo']['lng']

        store_temp_pc(result)

    return result


def check_temp_table(postcode):

    result = PostcodePlaceholder()

    if TemporaryPostcodes.objects.filter(postcode_index=postcode):
        postcode_data = TemporaryPostcodes.objects.get(postcode_index=postcode)
        result.postcode = postcode_data.postcode_index
        result.longitude = postcode_data.longitude
        result.latitude = postcode_data.latitude
        print '*********DB FUNC - POSTCODE FOUND IN DATABASE**********'
        return result

    else:
        print '*********DB FUNC - POSTCODE NOT FOUND IN TEMPORARY TABLE*******'
        return None


def store_temp_pc(pc_placeholder):

    try:
        pc = TemporaryPostcodes(postcode_index=pc_placeholder.postcode, latitude=pc_placeholder.latitude,
                            longitude=pc_placeholder.longitude)
        pc.save()
        print '***********DATABASE WRITE SUCCESSFUL********'
    except:
        print '***********DATABASE WRITE FAILED************'


