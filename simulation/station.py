import simpy 



class Station (simpy.Resource):

    """ An instance of this class represents a charging station """

    def __init__(self, env, capacity, n_btypes, swaptime, power, waitcharge):
        """
        :param env: The simulation environment.
        :param capacity: The number of vehicles the station can process together.

        :param n_btypes: A sequence of tuples (i.e., (BatteryType, n) ), where n 
                        represents the number of batteries kept for that type.
        
        :param swaptime: The operator time needed to swap batteries.
        
        :param power: The erogated electricity expressed in kW.

        :param waitcharge: This parameter is True if only fully charged batteries 
                           can be retrieved, and False otherwise.

        """

        super().__init__(env, capacity)
        
        self.env = env 
        self.swaptime = swaptime 
        self.power = power 
        self.waitcharge = waitcharge 

        self.incharge = {
                btype: simpy.Store(env, capacity=n)
            for btype, n in n_btypes
        }

        self.batteries = {
                btype: simpy.Store(env, capacity=n)
            for btype, n in n_btypes
        }