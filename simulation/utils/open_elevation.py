import requests
import pandas as pd


def get_elevation(latitude, longitude):
    """ Method to get the elevation of a node, using the Open Elevation API """
    
    # Request with a timeout for slow responses
    r = requests.get(f'https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longitude}', timeout = 20)

    # Only get the json response in case of 200 or 201
    if r.status_code == 200 or r.status_code == 201:
        #print(r.json())
        elevation = pd.json_normalize(r.json(), 'results')['elevation'].values[0]
    else: 
        raise Exception(r)
    return elevation
