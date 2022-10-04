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



class BatteriesGenerator:

    """ An instance of this class represents a generator of batteries """

    def __init__(self, func, config):
        """
        :param func: The function used to select a battery type.
        :param config: The simulation configuration.
        """
        self.btypes = tuple(BatteryType(i, config.BATTERIES_CAPACITY[i], config.BATTERIES_CONSUMPTION_RATE[i]) for i in range(config.N_BATTERIES))
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