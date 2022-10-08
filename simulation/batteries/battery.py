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
        return f"Battery_{self.__id}"



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