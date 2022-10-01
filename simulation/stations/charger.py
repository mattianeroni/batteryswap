from simpy.core import BoundClass 
from simpy.resources.store import Store, StoreGet, StorePut

from utils.technical import charge_time


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

        :param event: The ChargerPut event used to store the battery.
        """
        battery = event.item 
        yield self.env.timeout( charge_time(battery, self.power) )
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
            event.succeed()
            self.env.process(self.__charge_process(event))


    def _do_get(self, event):
        """
        Retrieval of a battery. 

        This method retrieve a battery from the Charger, 
        and trigger the ChargerGet event.

        :param event: The ChargerGet event.

        """
        #for item in self.items:
        #    if item.charged:
        #        self.items.remove(item)
        #        event.succeed(item)
        #        break
        #return True