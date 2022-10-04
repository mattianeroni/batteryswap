import dataclasses 
import functools 
import random 

from typing import Tuple, Union, Callable 

from utils.selection import biased_randomised_selection 


@dataclasses.dataclass
class Config:

    """ This class define the parameters of a simulation """
    

    # General
    SIM_TIME : int = 140_000                            # Simulation time 
    GRAPH_FILE : str = "./graphs/Test.graphml"          # Previously extracted graph to use 



    # Vehicles
    N_VEHICLES : int = 40                               # Number of travelling vehicles 
    
    
    
    # Stations
    PERCENTAGE_STATIONS : float = 0.2                   # Percentage of nodes with a charging station
    STATIONS_CAPACITY : Tuple[int, ...] = (
        2, 4, 6,
    )                                                   # The possible sizes of station (n° of vehicles they can process at the same time)
    CHARGERS : Tuple[Tuple[int,...], ...] = (
        (20, 15, 10), (30, 25, 25), (40, 35, 30),
    )                                                   # The size of chargers inside stations (n° of batteries they can charge for each type)
    STATIONS_POWER : Tuple[int,...] = (
        11, 20, 50
    )                                                   # The power in kW erogated by stations (which defines how fast they charge batteries)
    STATION_SELECTION : Callable = random.choice        # Function used to select the size of the charging stations
    CHARGER_SELECTION : Callable = None                 # Function used to select the size of the charger in a station 
                                                        # (if None, the respective of the STATION_SELECTION is used)
    POWER_SELECTION : Callable = None                   # Function used to select the power erogated by a station
                                                        # (if None, the respective of the STATION_SELECTION is used)


    # Batteries
    N_BATTERIES : int = 3                               # The number of managed batteries types
    BATTERIES_CAPACITY : Union[Tuple[int, ...], int] = (
        10, 20, 30
    )                                                   # The capacity of batteries types in kWh (an indicator of size of batteries)
    BATTERIES_CONSUMPTION_RATE: Union[Tuple[float,...], float] = (
        0.2, 0.1, 0.35
    )                                                   # The consumption rates of batteries types
    BATTERY_SELECTOR : Callable = functools.partial(biased_randomised_selection, beta=0.4)
                                                        # The function used to select a battery type instead of the other


    # Times
    SWAP_TIME : int = 30                                # The time (in seconds) required to swap batteries



