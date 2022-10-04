import functools 

from utils.check import check_configuration
import configuration 

config = configuration.Config() 
res = check_configuration(config, verbose=True)


# https://www.dazetechnology.com/how-long-does-it-take-to-charge-an-electric-vehicle/