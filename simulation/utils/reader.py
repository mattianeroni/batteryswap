import json 



def read_config (filename):
    """ Method used to read the json configuration file """
    with open(filename, 'r') as f:
        config = json.load(f)
    return config 