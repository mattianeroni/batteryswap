import simpy 

from .charger import Charger



class Station (simpy.Resource):

    """ An instance of this class represents a charging station """

    def __init__(self, env, capacity, btypes, chargers_capacities, swaptime, power):
        """
        :param env: The simulation environment.
        :param capacity: The number of vehicles the station can process together.
        :param btypes: The managed batery types.
        :param chargers_capacities: The number of batteries for each type that can be chargeed together.
        :param swaptime: The operator time needed to swap batteries.
        :param power: The erogated electricity expressed in kW.
        
        """

        super().__init__(env, capacity)
        
        self.env = env 
        self.swaptime = swaptime 
        self.power = power  

        self.chargers = {
                btype: Charger(env, capacity=n, power=power)
            for btype, n in zip(btypes, chargers_capacities)
        }