import functools 

import utils 



# Simulation variables
GRAPH_FILE = "./graphs/Test.graphml"            # Previously extracted graph to use 
SIM_TIME = 144_000                              # Simulation time 
N_VEHICLES = 30                                 # Number of travelling vehicles 
PERCENTAGE_STATIONS = 0.2                       # Percentage of nodes with a charging station
N_BATTERIES = 3                                 # Number of battery types           



# https://www.dazetechnology.com/how-long-does-it-take-to-charge-an-electric-vehicle/