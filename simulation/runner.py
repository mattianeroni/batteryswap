import simpy
import random 
import gc 
import statistics 
import functools
import networkx as nx 
from networkx.exception import NetworkXNoPath

from simulation.utils.technical import path_travel_time, path_consumption, path_length
from simulation.utils.technical import seconds_to_hours, hours_to_seconds, m_to_km
from simulation.utils.check import check_configuration
from simulation.utils.algorithms import define_path
from simulation.graph import Graph
from simulation.vehicles import Vehicle
from simulation.exceptions import SimulationNoPath, SimulationNoBattery



class SimulationRunner:
    
    """ An instance of this class represents a simulation to be executed """
    
    def __init__(self, config, stations=False, elevation=False, elevation_provider="open_elevation", timeout=20):
        """
        When a runner is instantiated, a simulation environment is created, the graph is imported 
        according to the spacification in the Config instance, and some checks on the feasibility 
        of the configuration are made. 

        :param config: The configuration of the simulation. 
        :param stations: If True the station nodes are recomputed.
        :param elevation: If True the streets slope is exctacted from Open Maps (NOTE: May take time!).
        :param elevation_provider: The website trusted to get the nodes elevation data. 
        :param timeout: The maximum time allowed for a GET request to receive node elevation data.
        """
        self.env = simpy.Environment()
        
        self.config = config
        assert check_configuration(config), "Inconsistencies detected in the configuration."
        
        self.G = Graph.from_file(self.env, config, stations=stations, elevation=elevation, elevation_provider=elevation_provider, timeout=timeout)
        

        # The number of trips successfully concluded
        self.failed_trips = 0
        self.nx_failed_trips = 0 
        self.battery_failed_trips = 0
        self.total_trips = 0
        self.total_distance = 0
        self.total_travel_time = 0

    @property 
    def stations (self):
        """ The charging stations """
        return tuple(i for i, node in self.G.nodes.items() if node['is_station'])

    @property 
    def relative_travel_time (self):
        """ The relative travel time in [hours / km] """
        return round(seconds_to_hours(self.total_travel_time) / m_to_km(self.total_distance), 3)


    @property 
    def avg_waiting_time (self):
        """ The average waiting time at stations """
        total_log_times = []
        for i in self.G.nodes.values():
            if i['is_station']:
                total_log_times.extend(i['station'].log_times)
        
        if len(total_log_times) == 0:
            return 0

        return statistics.mean( total_log_times )

    
    def __call__(self):
        """ Method to call to execute the simulation """
        self.env.process(self._run())
        self.env.run(self.config.SIM_TIME)    



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
        while True:
            
            ended_proc = yield env.any_of(vehicles_proc)
            vehicles_proc = [proc for proc in vehicles_proc if not proc in ended_proc.keys()]
            
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

        # Simulate the travelling station by station (when stations are needed)
        while source != target and vehicle.level > 0:
            
            # The path to the target (if possible), or alternatively 
            # the path to an intermediate charging station. 
            try:
                path = define_path(G, source, target, vehicle)
            
            except NetworkXNoPath:
                # No station or destination can be reached because of the 
                # graph topology.
                self.nx_failed_trips += 1
                return vehicle 
            
            except SimulationNoPath:
                # No station or destination can be reached because of the 
                # simulation algorithm.
                self.failed_trips += 1 
                return vehicle

            # Register when the vehicle starts travelling
            _start_travelling = env.now 
            
            # Wait for the vehicle to move
            yield env.timeout( path_travel_time(G, path, vehicle) )
            energy_used = path_consumption(G, path, vehicle)
            vehicle.position, source = path[-1], path[-1]

            # Update vehicle's batteries state
            vehicle.consume(energy_used)

            # Update the distance covered by the vehicle
            vehicle.covered += path_length(G, path)
            self.total_distance += vehicle.covered

            # If reached node is a station charge the vehicle.
            # Fake charge for the moment...
            if G.nodes[vehicle.position]["is_station"] and vehicle.position != target: 
                station = G.nodes[vehicle.position]["station"]
                with station.request() as req:
                    yield env.process(station.charge(req, vehicle, config.SHARING, config.WAIT_CHARGE))
            

            # Update the time the vehicle required to reach the destination
            vehicle.travel_time += env.now - _start_travelling
            self.total_travel_time += vehicle.travel_time

        # When the trip is concluded the vehicle is returned
        return vehicle