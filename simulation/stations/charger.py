import simpy 
from simpy.core import BoundClass 
from simpy.resources.store import Store, StoreGet, StorePut
from simpy.resources.store import FilterStore, FilterStoreGet

from simulation.utils.technical import charge_time, level_at_time, missing_time_to_charge

import functools 
import operator



class ChargerPut(StorePut):
    """ A request to store a battery into the Charger """
    pass

    
        
        
class ChargerGet(StoreGet):
    
    """ A request to get a battery from the Charger """
    
    def __init__(self, resource, waitcharge=True):
        self.filter = lambda i: 
        self.waitcharge = waitcharge
        """The filter function to filter items in the store."""
        super(FilterStoreGet, self).__init__(resource)

        
        
        
class Charger (Store):
    
    """ 
    This object represents the machine in charge of loading batteries.

    Its behaviour depends on the parameter <waitcharge>. If the parameter 
    is True, only fully charged batteries can be retrieved. 
    Otherwise, the most charged battery is returned. 

    """
    
    def __init__(self, env, capacity, power):
        """
        :param env: The simulation environment.
        :param capacity: The maximum number of batteries allowed.
        :param power: The power erogated by the charged (e.g., ~7Kw).
        """
        super().__init__(env, capacity)
        self.env = env 
        self.power = power 
        self.charging_processes = {}

        
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
        return len(self.put_queue)
    
        
    """ Method to store a battery """
    put = BoundClass(ChargerPut)

    """ Method to retrieve a battery """
    get = BoundClass(ChargerGet)

    
    def __charge_process(self, event):
        """
        Simulation process that emulates the charging of a battery.
        The duration of this process depends on the battery level and the
        power erogated by the charger.

        In the end, if a ChargerGet event is already waiting for the 
        charged battery, the ChargerGet event is triggered so that 
        the pending process can go on.

        :param event: The ChargerPut event used to store the battery.
        """
        battery = event.item 
        try:
            yield self.env.timeout( charge_time(battery, self.power) )
            battery.level = battery.capacity
            if event in self.get_queue:
                event.succeed(battery)
            print(int(self.env.now), "end charging")
        except simpy.Interrupt:
            battery.level = level_at_time(self.env.now, battery, self.power)
            if event in self.get_queue:
                event.succeed(battery)
        
    
    def _do_put(self, event):
        """ 
        Storage of a battery. 

        This method store the battery, trigger the ChargerPut event,
        and starts a charging process.

        :param event: The ChargerPut event.
        """
        if self.level < self._capacity:            
            self.items.append(event.item)           
            event.item.start_charging = self.env.now
            self.charging_processes[event.item] = self.env.process(self.__charge_process(event))
            event.succeed()
            


    def _do_get(self, event):
        """
        Retrieval of a battery. 

        This method retrieve a battery from the Charger, 
        and trigger the ChargerGet event.

        :param event: The ChargerGet event.

        """
        if event.waitcharge:
            battery = next((item for item in self.items if item.charged), None)
            if battery is not None:
                self.items.remove(battery)
                event.succeed(battery)
        else:
            _now = self.env.now
            battery = min( self.items, 
                key=lambda i: missing_time_to_charge(_now, i, self.power), 
                default=None 
            )
            if battery is not None:
                self.charging_processes[battery].interrupt()
                del self.charging_processes[battery]
                self.items.remove(battery)
                event.succeed(battery)
        
        return True



class ChangerBis:

    def __init__(self, env, capacity, power):
        """
        :param env: The simulation environment.
        :param capacity: The maximum number of batteries allowed.
        :param power: The power erogated by the charged (e.g., ~7Kw).
        """
        self.env = env
        self.capacity = capacity  
        self.power = power 
        self.__filterstore = FilterStore(env, capacity=capacity)
        self.charging_processes = {}

    @property 
    def items(self):
        return self.__filterstore.items


    def _get_process(self, waitcharge):
        battery = yield self.__filterstore.get(operator.attrgetter("charged"))
        return battery

    def _put_process(self, item):
        yield self.__filterstore.put(item)
        yield sel

    def get (self, waitcharge=True):
        return self.env.process(self._get_process(waitcharge))


    def put (self, item):
        return self.env.process(self._put_process(item))


        
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
        return len(self.put_queue)