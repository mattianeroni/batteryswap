class Distributor: 
    """ 
    The distributor is a particular vehicle used to redistribute 
    batteries. 

    Currently, the distributors are not subject to batteries consumption
    and have an inifnite capacity.
    In future, for a more accurate simulation, they might be electric vehicles
    as others, and they might have alimited capacity.
    """
    def __init__(self, env, speed, origin, destination=None):
        """
        :param env: The simulation environment
        :param speed: The vehicle speed 
        :param origin: The node the vehicle starts from 
        :param detination: The node where the vehicle is going.        
        """
        self.env = env 
        self.speed = speed 
        self.position = origin 
        self.origin = origin 
        self.destination = destination 
