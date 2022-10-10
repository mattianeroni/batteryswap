import simpy 
import functools 

from utils.check import check_configuration
from utils.configuration import export_configuration, read_configuration
import batteries 
import configuration 
import graph 



# https://www.dazetechnology.com/how-long-does-it-take-to-charge-an-electric-vehicle/



if __name__ == "__main__":

    env = simpy.Environment()

    config = configuration.Config() 

    assert check_configuration(config)


    export_configuration(config)
    read_configuration("config.json")


    #G = graph.Graph.from_file("./graphs/Test.graphml", env, config, elevation=False, elevation_provider="nationalmap")

    #G.plot()

    