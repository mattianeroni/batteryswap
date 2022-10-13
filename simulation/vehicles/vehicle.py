from numpy import negative
from simulation.batteries import Battery


class VehicleType:

    """ A type of vehicle managed by the simulation """
    
    def __init__(self, _id, btype, n_batteries, consumption, positive_slope_rate, negative_slope_rate):
        """
        :param _id: A unique id that identifies the vehicle type 
        :param btype: The battery type 
        :param n_batteries: The number of batteries needed to move the vehicle.
        :param consumption: The impact on consumptions due to the vehicle type.
        :param positive_slope_rate: Percentage increase of vehicle consumption in case of positive 
                                    slope. Expressed in [% / grade].
        :param negative_slope_rate: Percentage decrease of vehicle consumption in case of negative 
                                    slope. Expressed in [% / grade].
        """
        self._id = _id 
        self.btype = btype 
        self.n_batteries = n_batteries
        self.consumption = consumption
        

    def __repr__(self):
        return f"VehicleType_{self._id}"




class Vehicle:

    """ An instance of this class represents a single vehicle """

    def __init__(self, env, vtype, speed, origin, destination):
        """
        :param env: The simulation environment 
        :param vtype: The type of vehicle 
        :param speed: The average speed of the vehicle 
        :param origin: The node where the vehicle starts its trip.
        :param destination: The node where the vehicle ends its trip.
        """
        self.env = env 
        self.vtype = vtype 
        self.batteries = tuple(Battery(vtype.btype) for _ in range(vtype.n_batteries))
        self.speed = speed 
        
        self.origin = origin 
        self.destination = destination 
        self.position = origin 
        self.travel_time = 0
        self.covered = 0

    @property 
    def consumption_rate (self):
        return self.vtype.consumption

    @property 
    def positive_slope_rate (self):
        return self.vtype.positive_slope_rate

    @property 
    def negative_slope_rate (self):
        return self.vtype.negative_slope_rate
    