import simpy 
from simpy.core import BoundClass
from simpy.resources.resource import Request, Release

from .charger import Charger
from simulation.utils.technical import charge_time


import collections 



class StationType:

    """ An instance of this class represents a type of charging station """
    
    def __init__(self, _id, capacity, power, chargers_capacities):
        """
        :param capacity: The number of vehicles the station can process together.
        :param chargers_capacities: The number of batteries for each type that can be chargeed together.
        :param power: The erogated electricity expressed in kW.
        """
        self._id = _id 
        self.capacity = capacity 
        self.power = power 
        self.chargers_capacities = chargers_capacities

    def __repr__(self):
        return f"StationType_{self._id}"





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

    @property
    def chargers_level (self):
        """ the overall level of the station including all the chargers """
        return sum(i.level for i in self.chargers.values())

    @property
    def chargers_capacity (self):
        """ the overall level of the station including all the chargers """
        return sum(i.capacity for i in self.chargers.values())

    @property 
    def chargers_ontheside (self):
        """ The number of batteries that need to be charged but are not in charge """
        return sum(i.ontheside  for i in self.chargers.values())


    def charge (self, req, vehicle, sharing, waitcharge):
        """
        Process that simulates the vehicle charging.

        :param req: The request to occupy the station.
        :param vehicle: The vehicle to charge.
        :param sharing: True if batteries sharing is used.
        :param waitcharge: False if even partially charged batteries can be retrieved.  
        """
        env, charger, power = self.env, self.chargers[vehicle.btype], self.power

        # Logs for queue status
        _start_waiting = env.now 
        self.log_queue[env.now] = len(self.queue)
            
        # Wait for a free charging place
        yield req 

        # Logs for queue status
        self.log_times.append(env.now - _start_waiting)
        self.log_queue[env.now] = len(self.queue)

        if sharing: 
            # Remove current batteries
            for battery in vehicle.batteries:
                charger.put(battery)
                
            yield env.timeout(self.swaptime)


            # Take new ones 
            new_batteries = [None] * vehicle.n_batteries
            for i in range(vehicle.n_batteries):
                battery = yield charger.get(waitcharge=waitcharge)
                new_batteries[i] = battery 
            vehicle.batteries = tuple(new_batteries)
           
        else:
            # Charge current batteries
            for battery in vehicle.batteries:
                yield env.timeout(charge_time(battery, power))
                battery.level = battery.capacity

