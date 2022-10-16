import networkx as nx 
import osmnx as ox 
import random 
import json 

from simulation.stations import Station
from utils.open_elevation import get_elevation





def _str_to_bool(string):
    return False if string == "False" else True




class Graph(nx.MultiDiGraph):

    """ 
    An instance of this class represents the Graph needed by the simulation 
    as an extension of a networkx.MultiDiGraph.
    """


    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        return self
        
    

    @classmethod 
    def from_file (cls, env, config, stations=False, elevation=False, elevation_provider="open_elevation", timeout=20):
        """
        Method to generate the Graph object needed by the simulation.

        :param env: The simulation environment.
        :param config: The simulation's configuration.

        :param stations: If True the station nodes are recomputed.
        :param elevation: If true the streets slope is exctacted from Open Maps (NOTE: May take time!).
        :param elevation_provider: The website trusted to get the nodes elevation data. 
        :param timeout: The maximum time allowed for a GET request to receive node elevation data.

        :return: A Graph instance.
        """
        nxG = ox.load_graphml(config.GRAPH_FILE, 
            node_dtypes={"id_station": int, "is_station": _str_to_bool, "elevation": float, "startp": float, "endp": float}, 
            graph_dtypes={"has_stations": _str_to_bool}
        )

        G = cls.__new__(cls)
        G.__dict__.update(nxG.__dict__)
        
        # Imported from a previous exportation of a Graph 
        if G.graph.get("has_stations") == True and stations == False:
            for _, node in G.nodes.items():
                if node["is_station"]:
                    node["station"] = Station(
                        env, 
                        stype=config.STATION_TYPES[node["id_station"]],
                        btypes=config.BATTERY_TYPES,
                        swaptime=config.SWAP_TIME
                    )

            return G

        # Imported from a previous exportation of a normal networkx.MultiDiGraph
        G.graph["has_stations"] = True 
        # Initialise charging stations
        for node in G.nodes.values():

            # Set node elevation 
            if elevation:
                node["elevation"] = get_elevation(node['y'], node['x'], elevation_provider, timeout)
            else:
                node["elevation"] = 0.0 if not node.get("elevation") else node["elevation"]

            # Node is not a charging station
            if random.random() > config.PERCENTAGE_STATIONS:
                node["is_station"] = False
                node["startp"] = random.random()
                node["endp"] = random.random()
                continue 
                
                
            # Node is a charging station
            node["startp"] = 0.0
            node["endp"] = 0.0
            node["is_station"] = True

            station_type = config.STATION_SELECTOR(config.STATION_TYPES)
            node["id_station"] = station_type._id
            node["station"] =  Station(
                env, 
                stype=station_type,
                btypes=config.BATTERY_TYPES,
                swaptime=config.SWAP_TIME,
            )

        # Compute edges slope (i.e., grade) 
        ox.elevation.add_edge_grades(G, add_absolute=True, precision=3)

        return G


    def plot (self):
        """ 
        Method to plot the graph.
        In blue the normal nodes and in red the stations.       
        """
        _node_color = tuple("r" if node["is_station"] else "b" for node in self.nodes.values())
        ox.plot_graph(self, ax=None, figsize=(8, 8), bgcolor='white', node_color=_node_color, 
              node_size=15, node_alpha=None, node_edgecolor='none', node_zorder=1, 
              edge_color='blue', edge_linewidth=1, edge_alpha=None, show=True, close=False, 
              save=False, filepath=None, dpi=300, bbox=None)


    def save (self, filename):
        """ Method to save the graph instance in a GraphML file """
        for _, node in self.nodes.items():
            if node["is_station"]:
                node.pop("station")

        ox.save_graphml(self, filename)

    
