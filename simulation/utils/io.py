import json 
import functools

from simulation.configuration import Config 
from vehicles import VehicleType
from batteries import BatteryType 
from stations import StationType
from utils.selection import OPTIONS



def export_configuration (config, filename="config.json"):
    """ Method to export a configuration """
    for v in config.VEHICLE_TYPES:
        v.btype = None 
    c = dict(config.__dict__)
    c["BATTERY_SELECTOR"] = {"function": config.BATTERY_SELECTOR.func.__name__, "args": config.BATTERY_SELECTOR.keywords}
    c["VEHICLE_SELECTOR"] = {"function": config.VEHICLE_SELECTOR.func.__name__, "args": config.VEHICLE_SELECTOR.keywords}
    c["STATION_SELECTOR"] = {"function": config.STATION_SELECTOR.func.__name__, "args": config.STATION_SELECTOR.keywords}
    with open(filename, 'w') as file:
        file.write(json.dumps(c, default=lambda i: i.__dict__, indent=4, sort_keys=True))




def read_configuration (filename):
    """ Method to read a configuration exported to json """
    with open(filename, 'r') as file:
        d = json.load(file)
    
    d["BATTERY_SELECTOR"] = functools.partial(OPTIONS[d["BATTERY_SELECTOR"]["function"]], **d["BATTERY_SELECTOR"]["args"])
    d["VEHICLE_SELECTOR"] = functools.partial(OPTIONS[d["VEHICLE_SELECTOR"]["function"]], **d["VEHICLE_SELECTOR"]["args"])
    d["STATION_SELECTOR"] = functools.partial(OPTIONS[d["STATION_SELECTOR"]["function"]], **d["STATION_SELECTOR"]["args"])
    
    for i in d["VEHICLE_TYPES"]:
        del i["btype"]
    
    d["STATION_TYPES"] = tuple(StationType(**i) for i in d["STATION_TYPES"])
    d["BATTERY_TYPES"] = tuple(BatteryType(**i) for i in d["BATTERY_TYPES"])
    d["VEHICLE_TYPES"] = tuple(VehicleType(**i, btypes=d["BATTERY_TYPES"]) for i in d["VEHICLE_TYPES"])
   
    
    return Config(**d)