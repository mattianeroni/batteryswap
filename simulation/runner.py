import simpy 
from simulation.utils.check import check_configuration
from simulation.graph import Graph

import random 
import gc 


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
        
        # The number of trips successfully concluded
        self.success_trips = 0 
        self.total_trips = 0


    
    def __call__(self):
        """ Method to call to execute the simulation """
        self.env.process(self._run())
        self.env.run(self.config.SIM_TIME)    



    def _run (self):
        """ Starting point of the simulation """
        env, config, G = self.env, self.config, self.G

        # Initialise vehicles processes
        _origins = tuple(random.choices(tuple(G.nodes), weights=(i["startp"] for i in G.nodes.values()), k=config.N_VEHICLES))
        _dests = tuple(random.choices(tuple(G.nodes), weights=(i["endp"] for i in G.nodes.values()), k=config.N_VEHICLES))
        vehicles_proc = [ 
            env.process(    
                Vehicle(env, 
                    vtype=config.VEHICLE_SELECTOR(config.VEHICLE_TYPES), 
                    speed=config.VEHICLES_SPEED,
                    origin=_origins[i],
                    destination=_dests[i],
                ).trip()
            )
            for i in range(config.N_VEHICLES)
        ] 
        self.total_trips += config.N_VEHICLES

        # Free memory 
        del _origins
        del _dests 
        gc.collect() 

        # Simulation loop that add a new trip as soon as a trip is concluded
        while True:
            to_add = 0
            
            ended_proc = yield env.any_of(vehicles_proc)
            for proc, ok in ended_proc.items():
                vehicles_proc.remove(proc)
                to_add += 1 
                self.success_trips += int(ok)
            
            self.total_trips += to_add 
            vehicles_proc.extend([
                env.process(
                    Vehicle(env, 
                        vtype=config.VEHICLE_SELECTOR(config.VEHICLE_TYPES), 
                        speed=config.VEHICLES_SPEED,
                        origin=random.choices(tuple(G.nodes), weights=(i["startp"] for i in G.nodes.values()), k=1)[0],
                        destination=random.choices(tuple(G.nodes), weights=(i["endp"] for i in G.nodes.values()), k=1)[0],
                    ).trip()
                ) for _ in range(to_add)
            ])