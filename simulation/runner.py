import simpy
import random 
import gc 
import functools
import networkx as nx 
from networkx.exception import NetworkXNoPath

from simulation.utils.technical import path_travel_time, path_consumption, path_length
from simulation.utils.check import check_configuration
from simulation.utils.algorithms import define_path
from simulation.graph import Graph
from simulation.vehicles import Vehicle



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
        assert check_configuration(config), "Inconsistencies detected in the configuration."
        
        self.G = Graph.from_file(self.env, config, elevation=elevation, elevation_provider=elevation_provider, timeout=timeout)
        

        # The number of trips successfully concluded
        self.failed_trips = 0
        self.nx_failed_trips = 0 
        self.total_trips = 0
        self.total_distance = 0
        self.total_travel_time = 0


    
    def __call__(self):
        """ Method to call to execute the simulation """
        self.env.process(self._run())
        self.env.run()    



    def _run (self):
        """ Starting point of the simulation """
        env, config, G, __trip = self.env, self.config, self.G, self.__trip

        # Initialise vehicles processes
        _origins = tuple(random.choices(tuple(G.nodes), weights=(i["startp"] for i in G.nodes.values()), k=config.N_VEHICLES))
        _dests = tuple(random.choices(tuple(G.nodes), weights=(i["endp"] for i in G.nodes.values()), k=config.N_VEHICLES))
        vehicles_proc = [ 
            env.process(    
                __trip(
                    Vehicle(env, 
                        vtype=config.VEHICLE_SELECTOR(config.VEHICLE_TYPES), 
                        speed=config.VEHICLES_SPEED,
                        origin=_origins[i],
                        destination=_dests[i],
                    )
                )
            )
            for i in range(config.N_VEHICLES)
        ] 
        self.total_trips += config.N_VEHICLES

        # Free memory 
        del _origins
        del _dests 
        gc.collect() 

        # Simulation loop that add a new trip as soon as a trip is concluded
        while env.now < self.config.SIM_TIME:
            
            ended_proc = yield env.any_of(vehicles_proc)
            for proc, vehicle in ended_proc.items():
                vehicles_proc.remove(proc)
                self.total_distance += vehicle.covered
                self.total_travel_time += vehicle.travel_time
            
            diff = config.N_VEHICLES - len(vehicles_proc)
            self.total_trips += diff 
            vehicles_proc.extend([
                env.process(
                    __trip(
                        Vehicle(env, 
                            vtype=config.VEHICLE_SELECTOR(config.VEHICLE_TYPES), 
                            speed=config.VEHICLES_SPEED,
                            origin=random.choices(tuple(G.nodes), weights=(i["startp"] for i in G.nodes.values()), k=1)[0],
                            destination=random.choices(tuple(G.nodes), weights=(i["endp"] for i in G.nodes.values()), k=1)[0],
                        )
                    )
                ) for _ in range(diff)
            ])
        
        # Wait for remaining processes at the end of the simulation time 
        # defined by the configuration.
        ended_proc = yield env.all_of(vehicles_proc)
        self.total_distance += sum(i.covered for i in ended_proc.values())
        self.total_travel_time += sum(i.travel_time for i in ended_proc.values())


    def __trip (self, vehicle):
        """ 
        Process used to simulate the trip of a single vehicle from 
        its origin to its destination.
        :param vehicle: The vehicle that is doing the trip.
        """
        env, config, G = self.env, self.config, self.G
        source, target = vehicle.origin, vehicle.destination

        # If the vehicle is alreay arrived the process terminates
        if vehicle.position == vehicle.destination:
            return vehicle 
        
        #print(f"{int(env.now)} - {vehicle} starts.")
        # Register when the vehicle starts travelling
        _start_travelling = env.now 

        # Simulate the travelling station by station (when stations are needed)
        while vehicle.position != target and vehicle.level > 0:
            
            # The path to the target (if possible), or alternatively 
            # the path to an intermediate charging station. 
            try:
                path = define_path(G, source, target, vehicle)
            
            except NetworkXNoPath:
                self.nx_failed_trips += 1
                vehicle.travel_time = env.now - _start_travelling
                return vehicle 
            
            except SimulationNoPath:
                self.failed_trips += 1 
                vehicle.travel_time = env.now - _start_travelling
                return vehicle

            # No station or destination can be reached at this point.
            if not path:
                return vehicle
            
            # Wait for the vehicle to move
            yield env.timeout( path_travel_time(G, path, vehicle) )
            energy_used = path_consumption(G, path, vehicle)
            vehicle.position, source = path[-1], path[-1]

            # Update vehicle's batteries state
            vehicle.consume(energy_used)

            # Update the distance covered by the vehicle
            vehicle.covered += path_length(G, path)

            # If reached node is a station charge the vehicle.
            # Fake charge for the moment...
            if G.nodes[vehicle.position]["is_station"] and vehicle.position != target: 
                for i in vehicle.batteries:
                    i.level = i.capacity
            

        # Update the time the vehicle required to reach the destination
        vehicle.travel_time = env.now - _start_travelling
        return vehicle