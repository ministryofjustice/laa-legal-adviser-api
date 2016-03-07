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

    # Format postcode as lower-case, without spaces
    formatted_pc = format_postcode(postcode)

    # Check whether the postcode has a record in the temporary table
    result = check_temp_table(formatted_pc)

    # Has the temporary table yielded a result?
    if result:
        print '******Postcode provided by temporary table*******'
        return result
    else:
        # Read from Postcodes.io API
        postcode_data = PostCoder().get(formatted_pc)
        # Has Postcodes.io yielded a result?
        if postcode_data:
            print '********Postcode provided by Postcodes.io*********'
            result = PostcodePlaceholder()
            result.postcode = format_postcode(postcode_data['postcode'])
            result.latitude = postcode_data['geo']['lat']
            result.longitude = postcode_data['geo']['lng']
            store_temp_pc(result)
            return result
    print '**********No postcode provided***********'
    return None


def check_temp_table(formatted_pc):

    # Check whether the postcode exists in the temp table
    if TemporaryPostcodes.objects.filter(postcode=formatted_pc):
        # Get the record
        result = TemporaryPostcodes.objects.get(postcode=formatted_pc)
        return result

    else:
        return None


def store_temp_pc(pc_placeholder):

    pc = TemporaryPostcodes(postcode=pc_placeholder.postcode, latitude=pc_placeholder.latitude,
                            longitude=pc_placeholder.longitude)
    pc.save()




