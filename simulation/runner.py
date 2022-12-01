import simpy
import random 
import gc 
import statistics 
import functools
import networkx as nx
from networkx.algorithms.shortest_paths import astar
from networkx.exception import NetworkXNoPath

from simulation.utils.technical import path_travel_time, path_consumption, path_length, euclidean_distance
from simulation.utils.technical import seconds_to_hours, hours_to_seconds, m_to_km
from simulation.utils.check import check_configuration
from simulation.utils.algorithms import define_path
from simulation.graph import Graph
from simulation.vehicles import Vehicle, Distributor
from simulation.exceptions import SimulationNoPath, SimulationNoBattery



class SimulationRunner:
    
    """ An instance of this class represents a simulation to be executed """
    
    def __init__(self, env, config, G ):
        """
        When a runner is instantiated, a simulation environment is created, the graph is imported 
        according to the spacification in the Config instance, and some checks on the feasibility 
        of the configuration are made. 
        """
        self.env = env
        
        self.config = config
        assert check_configuration(config), "Inconsistencies detected in the configuration."
        
        self.G = G

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
        if self.config.SHARING:
            self.env.process(self._redistribution())
        self.env.process(self._checker())
        self.env.process(self._run())
        print("Simulation...", end="")
        self.env.run(self.config.SIM_TIME)    
        print("done")


    def _checker (self):
        while True:
            yield self.env.timeout(1000)
            print(self.env.now)

    def _redistribution (self):
        """ Process simulating the redistribution of batteries """
        env, config, G, __redistribution_trip = self.env, self.config, self.G, self.__redistribution_trip

        yield env.timeout(config.DISTRIBUTION_FREQUENCY)

        # Init the vehicles in charge of redistributing batteries
        vehicles = tuple(
            Distributor(env, 
                speed=config.VEHICLES_SPEED, 
                origin=random.choice(tuple(G.nodes))
            )
            for _ in range(config.N_REDISTRIBUTORS)
        )

        # Init the redistribution process 
        redis_proc = tuple(env.process(__redistribution_trip(i)) for i in vehicles)
        
        # Simulation loop
        while True:
            # Wait for redistributions to be concluded before starting a new round
            yield env.all_of(redis_proc) and env.timeout(config.DISTRIBUTION_FREQUENCY)
            redis_proc = tuple(env.process(__redistribution_trip(i)) for i in vehicles)     
        


    def __redistribution_trip (self, vehicle):
        """
        Process used to simulate a single redistribution from. 
        The vehicle goes form its position to the station where 
        it can take batteries, and then to the station that needs 
        batteries.

        :param vehicle: The distributor.        
        """
        env, config, G = self.env, self.config, self.G
        
        # Extract the list of charging stations --i.e., (node_id, station object)
        stations_list = tuple((i, node['station']) for i, node in G.nodes.items() if node['is_station'])
        
        # Pick the station the batteries will be retrieved from
        # NOTE: We choose the one with the highest number of batteries on the side 
        # (undependently on the battery type).
        source_id, source = max(stations_list, key=lambda i: i[1].chargers_ontheside )

        # Reconsider eventual suspension of the operation
        if source.chargers_ontheside == 0:
            return vehicle 

        # Pick the station the batteries will be brought to
        # NOTE: We choose the one with the highest difference between capacity and level 
        # (undependently on the battery type).
        target_id, target = max(stations_list, key=lambda i: i[1].chargers_capacity - i[1].chargers_level )     
        
        
        # Move to the source station to retrieve batteries
        path = astar.astar_path(G, vehicle.position, target_id, heuristic=functools.partial(euclidean_distance, G=G), weight="length")
        yield env.timeout(path_travel_time(G, path, vehicle))
        vehicle.position = source_id

        # Reconsider eventual suspension of the operation
        if source.chargers_ontheside == 0:
            return vehicle 

        # Retrieve batteries keeping them split by type
        batteries = {btype: [] for btype in config.BATTERY_TYPES}

        for btype, charger in source.chargers.items():
            batteries[btype].extend([ event.item for event in charger.put_queue ])
            charger.reset_put_queue()

        # Load batteries 
        yield env.timeout(config.DISTRIBUTOR_LOADING_TIME)

        # Move to the target station to bring batteries 
        path = astar.astar_path(G, source_id, target_id, heuristic=functools.partial(euclidean_distance, G=G), weight="length")
        yield env.timeout(path_travel_time(G, path, vehicle))
        vehicle.position = target_id 

        # Unload batteries 
        yield env.timeout(config.DISTRIBUTOR_LOADING_TIME)

        for btype, batteries_list in batteries.items():
            charger = target.chargers[btype]
            for i in batteries_list:
                charger.put(i)
        
        return vehicle
            



    def _run (self):
        """ Starting point of the simulation """
        env, config, G, __trip = self.env, self.config, self.G, self.__trip

        # Initialise vehicles processes
        origin_probs = tuple(i["startp"] for i in G.nodes.values())
        dest_probs = tuple(i["endp"] for i in G.nodes.values())

        _origins = tuple(random.choices(tuple(G.nodes), weights=origin_probs, k=config.N_VEHICLES))
        _dests = tuple(random.choices(tuple(G.nodes), weights=dest_probs, k=config.N_VEHICLES))

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

            for proc in ended_proc.keys():
                vehicles_proc.remove(proc)
            
            diff = config.N_VEHICLES - len(vehicles_proc)
            self.total_trips += diff 

            vehicles_proc.extend([
                env.process( 
                    __trip( 
                        Vehicle(
                            env,
                            vtype=config.VEHICLE_SELECTOR(config.VEHICLE_TYPES),
                            speed=config.VEHICLES_SPEED,
                            origin=random.choices(tuple(G.nodes), weights=origin_probs, k=1)[0],
                            destination=random.choices(tuple(G.nodes), weights=dest_probs, k=1)[0],
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
            self.total_distance += path_length(G, path)

            # If reached node is a station charge the vehicle.
            if G.nodes[vehicle.position]["is_station"] and vehicle.position != target: 
                station = G.nodes[vehicle.position]["station"]
                with station.request() as req:
                    yield env.process(station.charge(req, vehicle, config.SHARING, config.WAIT_CHARGE))
            
            # Update the time the vehicle required to reach the destination
            self.total_travel_time += env.now - _start_travelling

        # When the trip is concluded the vehicle is returned
        return vehicle