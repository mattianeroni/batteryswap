class BatteryType:

    """ An instance of this class represents a battery type """

    def __init__(self, _id, capacity, consumption_rate):
        """
        :param _id: A unique id to identify the battery type.
        :param capacity: The maximum charge in kWh.
        
        :param consumption_rate: A value in (0, 1) representing how fast the battery is consumed.
                                 According to literature, this value is indicatively around 0.24 kWh/mile 
                                 or 0.15 kWh/km.

        """
        self.__id = _id 
        self.capacity = capacity 
        self.consumption_rate = consumption_rate
    
    def __repr__(self):
        return f"{self.__id}"



class Battery:
    
    """ An instance of this class represents a single battery """

    def __init__(self, btype, level=None):
        """
        
        :param btype: The type of battery.
        :param level: The current level of charge in kWh.

        :attr start_charging: The simulation time when the battery started charging.
        
        """
        self.btype = btype 
        self.level = level or btype.capacity
        self.start_charging = 0 

    @property 
    def capacity (self):
        return self.btype.capacity 

    @property
    def consumption_rate (self):
        return self.btype.consumption_rate

    @property 
    def charged (self):
        return self.level == self.capacity


class BatteriesGenerator:

    """ An instance of this class represents a generator of batteries """

    def __init__(self, func, capacity, consumption_rate, n=None):
        """
        :param func: The function used to select a battery type.

        :param n: The number of batteries type considered (if None the __len__ of 
                    <capacity> and <consumption_rate> arguments is observed).

        :param capacity: The capacity of batteries types. 
                         It can be a sequence or an int. If it is an int, the indicated 
                         capacity is assigned to all batteries and the number of batteries is 
                         indicated by the __len__ of <consumption_rate> or <n>.

        :param consumption_rate: A value in (0, 1) saying how fast batteries of this type 
                                are consumed. It can be a sequence or an int. If it is an int, 
                                the indicated rate is assigned to all batteries and the number 
                                of batteries is indicated by the __len__ of <consumption_rate> or <n>.

        """

        if hasattr(capacity, "__len__") and hasattr(consumption_rate, "__len__"):
            
            i, j = len(capacity), len(consumption_rate)

            if i != j:
                raise Exception("Undefined number of batteries. Check capacity and consumption_rate length.")
            
            _n = i 
            _capacities = capacity
            _consumption_rates = consumption_rate
        
        elif hasattr(capacity, "__len__"):
            _n = len(capacity)
            _capacities = capacity
            _consumption_rates = [consumption_rate] * _n
            
        elif hasattr(consumption_rate, "__len__"):
            _n = len(consumption_rate)
            _capacities = [capacity] * _n
            _consumption_rates = consumption_rate
            
        else: 
            _n = n 
            _capacities = [capacity] * _n
            _consumption_rates = [consumption_rate] * _n

        
        if _n != n:
            raise Exception("Number of batteries different by explicited number n.")
        
        

        self.btypes = tuple(BatteryType(i, _capacities[i], _consumption_rates[i]) for i in range(_n))
        self.__func = func


    def choose_one(self):
        """ Choose a single battery type """
        return self.__func(self.btypes)


    def choose_some(self, n):
        """ 
        Choose more batteries types. 
        :param n: The number of types to return.
        """
        for _ in range(n):
            yield self.__func(self.btypes)