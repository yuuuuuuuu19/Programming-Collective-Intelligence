import math
api_key = ''

from xml.dom import minidom
from urllib.request import urlopen
from urllib.parse import quote_plus

loc_cashe = {}
base = 'http://api.local.yahoo.com/MapsService/V1/geocode?'

def get_location(address):
    if address in loc_cashe:
        return loc_cashe[address]

    url = base + f'appid={api_key}&location={quote_plus(address)}'
    print(url)
    data = urlopen(url).read()

    doc = minidom.parseString(data)
    lat = doc.getElementsByTagName('Latitude')[0].firstChid.nodeValue
    long = doc.getElementsByTagName('Longitude')[0].firstChid.nodeValue
    loc_cashe[address] = (float(lat), float(long))

    return loc_cashe[address]

def distance_miles(a1, a2):
    lat1, long1 = get_location(a1)
    lat2, long2 = get_location(a2)

    lat_diff = (lat1 - lat2) * 69.1
    long_diff = (long1 - long2) * 53.0
    d = math.sqrt(lat_diff ** 2 + long1 ** 2)
    return d

