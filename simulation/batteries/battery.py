class BatteryType:

    """ An instance of this class represents a battery type """

    def __init__(self, _id, capacity):
        """
        :param _id: A unique id to identify the battery type.
        :param capacity: The maximum charge in kWh.s

        """
        self._id = _id 
        self.capacity = capacity 
    
    def __repr__(self):
        return f"BatteryType_{self._id}"



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
    def charged (self):
        return self.level == self.capacity