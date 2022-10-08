import networkx as nx 
import osmnx as ox 
import random 

from simulation.stations import Station
from utils.open_elevation import get_elevation


class Graph(nx.MultiDiGraph):

    """ 
    An instance of this class represents the Graph needed by the simulation 
    as an extension of a networkx.MultiDiGraph.
    """


    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        return self
    

    @classmethod 
    def from_nx_graph(cls, nxG, env, config):
        """
        Method to generate the Graph object needed by the simulation.

        :param nxG: A networkx.MultiDiGraph.
        :param env: The simulation environment.
        :param config: The simulation's configuration.

        :return: A Graph instance.
        """
        G = cls.__new__(cls)
        G.__dict__.update(nxG.__dict__)

        # Initialise charging stations
        for _, node in G.nodes.items():

            # Set node elevation 
            node["elevation"] = get_elevation(node['y'], node['x'])
            
            # Node is not a charging station
            if random.random() > config.PERCENTAGE_STATIONS:
                node["is_station"] = False
                node["startp"] = random.random()
                node["endp"] = random.random()
                continue 
            
            # Node is a charging station
            node["is_station"] = True
            node["startp"] = 0.0
            node["endp"] = 0.0

            station_type = config.STATION_SELECTOR(config.STATION_TYPES) 

            node["station"] =  Station(
                env, 
                capacity=station_type.capacity, 
                btypes=config.BATTERY_TYPES,
                chargers_capacities=station_type.chargers_capacities,
                swaptime=config.SWAP_TIME,
                power=station_type.power,
            )


        # Compute edges slope (i.e., grade) 
        ox.elevation.add_edge_grades(G, add_absolute=True, precision=3)

        return G


    @classmethod
    def from_file(cls, filename, env, config):
        """
        Same as from_nx_graph but it reads the MultiDiGraph from a 
        GraphML file.
        """
        nxG = ox.load_graphml(filename)
        return cls.from_nx_graph(nxG, env, config)

    
