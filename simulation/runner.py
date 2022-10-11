import simpy 
from simulation.utils.check import check_configuration
from simulation.graph import Graph



class SimulationRunner:
    
    """ An instance of this class represents a simulation to be executed """
    
    def __init__(self, config, elevation=False, elevation_provider="open_elevation", timeout=20):
        """
        When a runner is instantiated, a simulation environment is created, the graph is imported 
        according to the spacification in the Config instance, and some checks on the feasibility 
        of the configuration are made. 

        :param config: The configuration of the simulation. 
        :param elevation: If True the streets slope is exctacted from Open Maps (NOTE: May take time!).
        :param elevation_provider: The website trusted to get the nodes elevation data. 
        :param timeout: The maximum time allowed for a GET request to receive node elevation data.
        """
        self.env = simpy.Environment()
        
        self.config = config
        assert check_configuration(config)
        
        self.G = Graph.from_file(self.env, config, elevation=elevation, elevation_provider=elevation_provider, timeout=timeout)


    def _run (self):
        """ Starting point of the simulation """
        env = self.env 
        yield env.timeout(100)

    def __call__(self):
        """ Method to call to execute the simulation """
        self.env.process(self._run())
        self.env.run(self.config.SIM_TIME)    