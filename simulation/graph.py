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
    def from_nx_graph(cls, nxG, env, btypes, config):
        """
        Method to generate the Graph object needed by the simulation.

        :param nxG: A networkx.MultiDiGraph.
        :param env: The simulation environment.
        :param btype: The battteries types managed.
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

            station_cap = config.STATION_SELECTION(config.STATIONS_CAPACITY)
            chargers_caps = config.CHARGERS[list(config.STATIONS_CAPACITY).index(station_cap)] if config.CHARGER_SELECTION is None else config.CHARGER_SELECTION(config.CHARGERS) 
            station_power = config.STATIONS_POWER[list(config.STATIONS_CAPACITY).index(station_cap)] if config.POWER_SELECTION is None else config.POWER_SELECTION(config.STATIONS_POWER)
            
            node["station"] =  Station(
                env, 
                capacity=station_cap, 
                n_btypes=[ (type_, number) for type_, number in zip(btypes, chargers_caps) ],
                swaptime=config.SWAP_TIME,
                power=station_power,
            )


        # Compute edges slope (i.e., grade) 
        ox.elevation.add_edge_grades(G, add_absolute=True, precision=3)
        
        # Edges energy consumption

        return G


    @classmethod
    def from_file(cls, filename, env, btypes, config):
        """
        Same as from_nx_graph but it reads the MultiDiGraph from a 
        GraphML file.
        """
        nxG = ox.load_graphml(filename)
        return cls.from_nx_graph(nxG, env, btypes, config)

    
