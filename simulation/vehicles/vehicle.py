from simulation.batteries import Battery


class VehicleType:

    """ A type of vehicle managed by the simulation """
    
    def __init__(self, _id, btype, n_batteries, consumption_rate):
        """
        :param _id: A unique id that identifies the vehicle type 
        :param btype: The battery type 
        :param n_batteries: The number of batteries needed to move the vehicle.
        :param consumption_rate: The impact on consumptions due to the vehicle type.
        """
        self.__id = _id 
        self.btype = btype 
        self.batteries = tuple(Battery(btype) for _ in range(n_batteries))
        self.consumption_rate = consumption_rate
        

    def __repr__(self):
        return f"Vehicle_{self.__id}"




class Vehicle:

    """ An instance of this class represents a single vehicle """

    def __init__(self, env, vtype, speed):
        """
        :param env: The simulation environment 
        :param vtype: The type of vehicle 
        :param speed: The average speed of the vehicle 
        """
        self.env = env 
        self.vtype = vtype 
        self.speed = speed 