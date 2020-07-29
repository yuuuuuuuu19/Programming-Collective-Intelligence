from xml.dom import minidom
import urllib.request


# Zillow API Network: https://www.zillow.com/howto/api/GetSearchResults.htm
zwskey = ''
base = 'https://www.zillow.com/webservice/GetDeepSearchResults.htm?'


def get_address_data(address, city):
    escad = address.replace(' ', '+')

    # build url
    url = base + f'zws-id={zwskey}&address={escad}&citystatezip={city}'
    # parse xml
    response = urllib.request.urlopen(url)

    print(f'Request: {address}')
    doc = minidom.parseString(response.read())
    print(doc.getElementsByTagName('code')[0].firstChild.data)
    code = doc.getElementsByTagName('code')[0].firstChild.data

    # if code equals to 0, success
    # otherwise failure

    if code != '0':
        return None

    # get estate info
    try:
        zip_code = doc.getElementsByTagName('zipcode')[0].firstChild.data
        use = doc.getElementsByTagName('useCode')[0].firstChild.data
        year = doc.getElementsByTagName('yearBuild')[0].firstChild.data
        bath = doc.getElementsByTagName('bathrooms')[0].firstChild.data
        bed = doc.getElementsByTagName('bedrooms')[0].firstChild.data
        rooms = doc.getElementsByTagName('totalRooms')[0].firstChild.data
        price = doc.getElementsByTagName('amount')[0].firstChild.data
    except Exception as e:
        print(e)
        return None

    return (zip_code, use, int(year), float(bath), int(bed), int(rooms), price)


def get_pricelist(filename='addresslist.txt'):
    res = []
    with open(filename, 'r') as file:
        for address in file:
            data = get_address_data(address.strip(), 'Cambridge,MA')
            if data:
                res += data
    return res
