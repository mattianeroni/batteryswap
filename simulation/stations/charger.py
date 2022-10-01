from simpy.core import BoundClass 
from simpy.resources.store import Store, StoreGet, StorePut

from utils.technical import charge_time, level_at_time, missing_time_to_charge

import functools 



class ChargerPut(StorePut):
    """ A request to store a battery into the Charger """
    pass

        
        
class ChargerGet(StoreGet):
    
    """ A request to get a battery from the Charger """
    
    def __init__(self, store, waitcharge=True):
        """

        :param waitcharge: True if only fully charged batteries 
                            can be retrieved, False otherwise.

        """
        self.waitcharge = waitcharge
        super(ChargerGet, self).__init__(store)

        
        
        
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

        
    @property 
    def level (self):
        """ The number of batteries currently in charge """
        return len(self.items)

    @property 
    def incharge (self):
        """ The bnumber of batteries on charge """
        return sum(1 for i in self.items if i.level < i.capacity)
    
    @property 
    def charged (self):
        """ The number of fully charged batteries """
        return sum(1 for i in self.items if i.level == i.capacity)
    
        
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
        yield self.env.timeout( charge_time(battery, self.power) )
        battery.level = battery.capacity
        battery.charged = True
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
            event.succeed()
            self.env.process(self.__charge_process(event))


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
                self.items.remove(item)
                event.succeed(battery)
        else:
            _now = self.env.now
            battery = min( self.items, key=functools.partial(missing_time_to_charge, ctime=_now, power=self.power) , default=None )
            assert battery is not None 
            self.items.remove(battery)
            battery.level = level_at_time(_now, battery, self.power)
            event.succeed(battery)
        
        return True