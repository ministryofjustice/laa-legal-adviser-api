from postcodes import PostCoder
from advisers.models import TemporaryPostcodes


class PostcodePlaceholder:

    def __init__(self):
        self.postcode = None
        self.longitude = None
        self.latitude = None


def format_postcode(postcode):
    formatted_pc = postcode.replace(' ','')
    formatted_pc = formatted_pc.lower()
    return formatted_pc


def geocode(postcode):

    formatted_pc = format_postcode(postcode)

    result = check_temp_table(formatted_pc)

    if result:
        print '******GEOCODE - POSTCODE FOUND IN TEMPORARY TABLE*********'
        return result
    else:

        print '******GEOCODE - POSTCODE NOT FOUND IN TEMPORARY TABLE*********'
        print '******GEOCODE - CHECKING ' + formatted_pc + ' AT POSTCODES.IO********'
        postcode_data = PostCoder().get(formatted_pc)
        print '******GEOCCODE - POSTCODES.IO RESPONSE:'
        print postcode_data

        if postcode_data:
            result = PostcodePlaceholder()
            result.postcode = format_postcode(postcode_data['postcode'])
            result.latitude = postcode_data['geo']['lat']
            result.longitude = postcode_data['geo']['lng']
            store_temp_pc(result)
        else:
            print '******Postcode Not Found Exception Placeholder********'

    return result


def check_temp_table(formatted_pc):

    result = PostcodePlaceholder()

    if TemporaryPostcodes.objects.filter(postcode_index=formatted_pc):
        postcode_data = TemporaryPostcodes.objects.get(postcode_index=formatted_pc)
        result.postcode = postcode_data.postcode_index
        result.longitude = postcode_data.longitude
        result.latitude = postcode_data.latitude
        print '*********DB CHECK - POSTCODE FOUND IN DATABASE**********'
        print '*********DB CHECK - FOUND DATA:'
        print result.postcode
        return result

    else:
        print '*********DB CHECK - POSTCODE NOT FOUND IN TEMPORARY TABLE*******'
        return None


def store_temp_pc(pc_placeholder):

    #try:
    pc = TemporaryPostcodes(postcode_index=pc_placeholder.postcode, latitude=pc_placeholder.latitude,
                            longitude=pc_placeholder.longitude)
    print '***********DB WRITE - RECORD CREATED:'
    print pc.postcode_index
    pc.save()
    print '***********DB WRITE - DATABASE WRITE SUCCESSFUL********'
    #except:
    #    print '***********DB WRITE - DATABASE WRITE FAILED************'


