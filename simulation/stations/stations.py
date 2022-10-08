import simpy 
from simpy.core import BoundClass
from simpy.resources.resource import Request, Release

from .charger import Charger


import collections 



class StationType:

    """ An instance of this class represents a type of charging station """
    
    def __init__(self, _id, capacity, power, chargers_capacities):
        """
        :param capacity: The number of vehicles the station can process together.
        :param chargers_capacities: The number of batteries for each type that can be chargeed together.
        :param power: The erogated electricity expressed in kW.
        """
        self.__id = _id 
        self.capacity = capacity 
        self.power = power 
        self.chargers_capacities = chargers_capacities

    def __repr__(self):
        return f"Station_{self.__id}"




class Station (simpy.Resource):

    """ An instance of this class represents a charging station """

    def __init__(self, env, stype, btypes, swaptime):
        """
        :param env: The simulation environment.
        :param stype: The station type.
        :param btypes: The managed batery types.
        :param swaptime: The operator time needed to swap batteries.
        """

        super().__init__(env, stype.capacity)
        
        self.env = env 
        self.stype = stype 
        self.swaptime = swaptime 
        self.power = stype.power  

        self.chargers = {
                btype: Charger(env, capacity=n, power=stype.power)
            for btype, n in zip(btypes, stype.chargers_capacities)
        }

        self.log_queue = {}
        self.log_times = collections.deque()