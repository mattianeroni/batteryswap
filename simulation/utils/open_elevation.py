import requests
import urllib
import pandas as pd




def _get_elevation_open_elevation(latitude, longitude, timeout=20):
    """ Method to get the elevation of a node, using the Open Elevation API """
    
    # Request with a timeout for slow responses
    r = requests.get(f'https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longitude}', timeout = timeout)

    # Only get the json response in case of 200 or 201
    if r.status_code == 200 or r.status_code == 201:
        #print(r.json())
        elevation = pd.json_normalize(r.json(), 'results')['elevation'].values[0]
    else: 
        raise Exception(r)
    return elevation



def _get_elevation_nationalmap(latitude, longitude, timeout=20):
    # USGS Elevation Point Query Service
    url = r"https://nationalmap.gov/epqs/pqs.php?"

    params = {
        'output': 'json',
        'x': longitude,
        'y': latitude,
        'units': 'Meters'
    }
    
    r = requests.get( url + urllib.parse.urlencode(params), timeout=timeout )
    if r.status_code == 200 or r.status_code == 201:
        return r.json()['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation']
    else:
        raise Exception(r)




funcs = {
    "open_elevation" : _get_elevation_open_elevation,
    "nationalmap" : _get_elevation_nationalmap,
}


def get_elevation(latitude, longitude, provider="open_elevation", timeout=20):
    func = funcs[provider]
    return func(latitude, longitude, timeout=timeout)