import simpy 
import functools 

from utils.check import check_configuration
import batteries 
import configuration 
import graph 



# https://www.dazetechnology.com/how-long-does-it-take-to-charge-an-electric-vehicle/



if __name__ == "__main__":

    env = simpy.Environment()

    config = configuration.Config() 

    assert check_configuration(config)

    #bgen = batteries.BatteriesGenerator(config)


    #G = graph.Graph.from_file("./graphs/Test.graphml", env, bgen.btypes, config)

    