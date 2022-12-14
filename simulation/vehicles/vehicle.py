from simulation.batteries import Battery

import random


class VehicleType:

    """ A type of vehicle managed by the simulation """
    
    def __init__(self, _id, btype_id, n_batteries, consumption, positive_slope_rate, negative_slope_rate, btypes):
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
        self.btype_id = btype_id
        self.btype = btypes[btype_id]
        self.n_batteries = n_batteries
        self.consumption = consumption
        self.positive_slope_rate = positive_slope_rate 
        self.negative_slope_rate = negative_slope_rate
        

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
        self.batteries = tuple(Battery(vtype.btype, level=random.random() * vtype.btype.capacity) 
                            for _ in range(vtype.n_batteries))
        self.speed = speed 
        
        self.origin = origin 
        self.destination = destination 
        self.position = origin 

    @property 
    def level (self):
        return sum(i.level for i in self.batteries)

    @property 
    def capacity (self):
        return sum(i.capacity for i in self.batteries)

    @property 
    def n_batteries (self):
        return self.vtype.n_batteries

    @property 
    def btype (self):
        return self.batteries[0].btype

    @property 
    def consumption (self):
        return self.vtype.consumption

    @property 
    def positive_slope_rate (self):
        return self.vtype.positive_slope_rate

    @property 
    def negative_slope_rate (self):
        return self.vtype.negative_slope_rate


    def consume (self, energy):
        """
        The state of the vehicle batteries is updated according
        to the quantity of energy consumed.

        NOTE: The energy consumed in equally distributed over all the batteries

        :param energy: The energy consumed in kWh.
        """
        uenergy = energy / len(self.batteries)
        for b in self.batteries:
            b.level = max(0, b.level - uenergy)

        
    