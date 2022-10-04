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