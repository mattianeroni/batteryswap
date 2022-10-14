class SimulationNoPath (Exception):
    """ Exception raised when a path is not found because 
    of the simulation behaviour """
    pass 


class SimulationNoBattery (Exception):
    """ Exception raised when a vehicle cannot conclude its 
    trip because it is waiting for batteries in a certain station """
    pass  