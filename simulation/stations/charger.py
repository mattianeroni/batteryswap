import simpy 
#from simpy.core import BoundClass 
#from simpy.resources.store import Store, StoreGet, StorePut
from simpy.resources.store import FilterStore
from simpy.resources.container import Container

from simulation.utils.technical import charge_time, level_at_time, missing_time_to_charge

import functools 
import operator




class Charger:

    def __init__(self, env, capacity, power):
        """
        :param env: The simulation environment.
        :param capacity: The maximum number of batteries allowed.
        :param power: The power erogated by the charged (e.g., ~7Kw).

        :attr __spacekeeper: A space keeper (a sort of mutex lock) to prevent
                            weird behaviours due to simpy.
        :attr __filterstore: The actual store where batteries are kept.
        :attr charging_processes: A hashmap keeping track of all active 
                                charging processes.
        """
        self.env = env
        self.capacity = capacity  
        self.power = power 

        self.__spacekeeper = Container(env, capacity=capacity, init=0)
        self.__filterstore = FilterStore(env, capacity=capacity)
        self.charging_processes = {}

    @property 
    def items(self):
        """ Batteries stored """
        return self.__filterstore.items

    @property 
    def level (self):
        """ The number of batteries currently in charge """
        return len(self.items)

    @property 
    def incharge (self):
        """ The number of batteries on charge """
        return sum(1 for i in self.items if i.level < i.capacity)
    
    @property 
    def charged (self):
        """ The number of fully charged batteries """
        return sum(1 for i in self.items if i.level == i.capacity)

    @property 
    def ontheside (self):
        """ The number of batteries left to the station but with no 
        space to be charged """
        return len(self.__filterstore.put_queue)

    @property
    def put_queue (self):
        return self.__filterstore.put_queue


    def reset_put_queue (self):
        self.__filterstore.put_queue = []


    def __charge_process(self, battery):
        """ Charging process used to charge a battery.
        This process can be interrupted. """
        try:
            yield self.env.timeout( charge_time(battery, self.power) )
            battery.level = battery.capacity
            del self.charging_processes[battery]

        except simpy.Interrupt:
            battery.level = level_at_time(self.env.now, battery, self.power)
            del self.charging_processes[battery]


    def _get_process(self, waitcharge):
        """ Process used to retrieve an element from the charger """
        _now = self.env.now
        # In case a fully charged battery is required...
        if waitcharge:
            # If there is an already charged battery, it is retrieved.
            # Otherwise, we pick the battery with the minimum missing time to charge,
            # we wait for the charging process to be concluded, and then we retrieve it.
            toget = min( self.__filterstore.items, 
                key=lambda i: missing_time_to_charge(_now, i, self.power), 
                default=None 
            )
            
            if toget:
                battery = yield self.__filterstore.get(functools.partial(operator.eq, toget))
            
            else:
                battery = yield self.__filterstore.get()
            
            if (proc := self.charging_processes.get(battery)):
                yield proc            
        
        # Even partially charged batteries are accepted...
        else:
            # We simply pick the battery with the minimum missing time to charge,
            # we interrupt the charging process and we retrieve the battery.
            toget = min( self.__filterstore.items, 
                key=lambda i: missing_time_to_charge(_now, i, self.power), 
                default=None 
            )
            if toget:
                battery = yield self.__filterstore.get(functools.partial(operator.eq, toget))
            else:
                battery = yield self.__filterstore.get()
            
            if (proc := self.charging_processes.get(battery)):
                proc.interrupt()
        
        # Remove a space keeper to allow a a new put 
        yield self.__spacekeeper.get(1)

        # Return the retrieved battery
        return battery


    def _put_process(self, item):
        """ Process used to store an element into the charger """
        yield self.__spacekeeper.put(1)
        yield self.__filterstore.put(item)
        proc = self.env.process(self.__charge_process(item))
        self.charging_processes[item] = proc
        

    def get (self, waitcharge=True):
        """ Syntactic sugar on top of _get_process """
        return self.env.process(self._get_process(waitcharge))


    def put (self, item):
        """ Syntactic sugar on top of _put_process """
        return self.env.process(self._put_process(item))
