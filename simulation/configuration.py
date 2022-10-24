import dataclasses 
import functools 
import random 

from typing import Tuple, Callable

from simulation.utils.selection import biased_randomised_selection 
from simulation.vehicles import VehicleType 
from simulation.batteries import BatteryType 
from simulation.stations import StationType



@dataclasses.dataclass
class Config:

    """ This class define the parameters of a simulation """
    

    # GENERAL
    # --------------------------------------------------------------------------------------------------------
    SIM_TIME : int = 14_000                             # Simulation time [seconds]
    GRAPH_FILE : str = "./graphs/Modena.graphml"        # Previously extracted graph to use 
    N_VEHICLES : int = 40                               # Number of travelling vehicles during the simulation
    N_REDISTRIBUTORS : int = 10                         # Number of vehicles in charge of redistristributing batteries
    DISTRIBUTION_STARTUP : int = 500                    # The simulation time before that the redistribution of batteries starts
    SHARING : bool = True                               # If True batteries are shared otherwise not
    WAIT_CHARGE : bool = True                           # If False vehicles can retrieve partially charged batteries too,
                                                        # otherwise only fully charged batteries can be retrieved.
    
    # --------------------------------------------------------------------------------------------------------

    
    
    # STATIONS
    # --------------------------------------------------------------------------------------------------------
    PERCENTAGE_STATIONS : float = 0.05                   # Percentage of nodes with a charging station [%]


    # The station type used in the simulation 
    # :param _id: A unique id 
    # :param capacity: The size of station type (n° of vehicles they can process at the same time)
    # :param power: The power in kW erogated by stations (which defines how fast they charge batteries)
    # :param chargers_capacities: The size of chargers inside stations (n° of batteries they can charge for each type)
    #                             Be careful the order of these capacities corresponds to the battery types order.
    STATION_TYPES : Tuple[StationType, ...] = (
        StationType(
            _id = 0,
            capacity = 2,
            power = 11,
            chargers_capacities = (20, 15, 10)
        ),
        StationType(
            _id = 1,
            capacity = 4,
            power = 20,
            chargers_capacities = (30, 25, 25)
        ),
        StationType(
            _id = 2,
            capacity = 6,
            power = 50,
            chargers_capacities = (40, 35, 30)
        ),
    )

    STATION_SELECTOR : Callable = functools.partial(random.choice)
                                                        # Function used to select the size of the charging stations
    # --------------------------------------------------------------------------------------------------------


    # BATTERIES
    # --------------------------------------------------------------------------------------------------------

    #  The battery types considered in the simulation 
    # :param _id: A unique id to identify the battery type
    # :param capacity: The capacity of batteries types in kWh (an indicator of size of batteries)
    BATTERY_TYPES : Tuple[BatteryType, ...] = (
        BatteryType(_id = 0, capacity = 10),
        BatteryType(_id = 1, capacity = 20),
        BatteryType(_id = 2, capacity = 20),
    )

    BATTERY_SELECTOR : Callable = functools.partial(biased_randomised_selection, beta=0.4)
                                                        # The function used to select a battery type instead of the other
    # --------------------------------------------------------------------------------------------------------


    # VEHICLES
    # --------------------------------------------------------------------------------------------------------

    VEHICLES_SPEED : int = 16                           # The vehicles speed in [m/s]

    # The possible vehicle types considered
    # :param _id: A unique id to identify the vehicle type 
    # :param n_batteries: The size of the vehicle expressed in number of batteries used
    # :param consumption: The consumption of the vehicle type [kWh / km]
    # :param positive_slope_rate: Percentage increase of consumption for each grade of positive slope [% / °grade]
    # :param negative_slope_rate: Percentage decrease of consumption for each grade of negative slope [% / °grade]
    VEHICLE_TYPES : Tuple[VehicleType,...] = (
        VehicleType(
            _id = 0,
            btype = BATTERY_TYPES[0],
            n_batteries = 1,
            consumption = 0.2,
            positive_slope_rate = 0.1,
            negative_slope_rate = -0.05
        ),        

    )                                                   

    VEHICLE_SELECTOR : Callable = functools.partial(biased_randomised_selection, beta=0.4)
                                                        # The function used to select a vehicle type

    # --------------------------------------------------------------------------------------------------------


    # TIMES 
    # --------------------------------------------------------------------------------------------------------
    SWAP_TIME : int = 30                                # The time (in seconds) required to swap batteries
    DISTRIBUTOR_LOADING_TIME : int = 60                 # The time (in seconds) required by the distributors 
                                                        # to load and unload batteries.
    # --------------------------------------------------------------------------------------------------------


