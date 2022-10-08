class StationType:

    """ An instance of this class represents a type of charging station """
    
    def __init__(self, _id, capacity, power, chargers_capacities):
        self.__id = _id 
        self.capacity = capacity 
        self.power = power 
        self.chargers_capacities = chargers_capacities

    def __repr__(self):
        return f"Station_{self.__id}"




class StationsGenerator:

    """ An instance of this class represents a generator of stations """

    def __init__(self, config):
        """
        :param config: The simulation configuration.
        """
        self.stypes = tuple(config.STATION_TYPES)
        self.__func = config.STATION_SELECTOR


    def choose_one(self):
        """ Choose a single station type """
        return self.__func(self.stypes)


    def choose_some(self, n):
        """ 
        Choose more stations types. 
        :param n: The number of types to return.
        """
        for _ in range(n):
            yield self.__func(self.stypes)