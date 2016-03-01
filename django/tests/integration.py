import sys
import json
import requests


try:
    url = sys.argv[1]
    req = requests.get('{0}/legal-advisers/?postcode=sw1h9aj'.format(url))

    '''
    Check response code is 200
    '''
    if req.status_code is not 200:
        print '[ERROR] Response code not 200: {0}'.format(req.status_code)
        sys.exit(1)

    '''
    Check response is valid JSON
    '''
    try:
        json.loads(req.text)
    except ValueError:
        print '[ERROR] Response not valid JSON'
        sys.exit(1)

    '''
    Check response has coordinates within the first result
    '''
    data = json.loads(req.text)
    if len(data['results'][0]['location']['point']['coordinates']) != 2:
        print '[ERROR] Response does not have coordinates'
        sys.exit(1)

except requests.exceptions.ConnectionError:
    print '[ERROR] Failed to connect to: {0}'.format(url)
    sys.exit(1)
except IndexError:
    print '[ERROR] No URL argument set, example: integration.py https://my.domain.com'
    sys.exit(1)

