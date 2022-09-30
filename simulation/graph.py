import networkx as nx 
import osmnx as ox 
import random 


class Graph(nx.MultiDiGraph):

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        #self.i = 44
        return self
    
    @classmethod 
    def from_nx_graph(cls, nxG, charging_stations, swap_time):
        """
        Method to generate the Graph object needed by the simulation.

        :param nxG: A networkx.MultiDiGraph.
        :param charging_stations: The percentage of nodes that are charging stations.
        :param swap_time: Operator time needed to change batteries.
        :return: A Graph instance.
        """
        G = cls.__new__(cls)
        G.__dict__.update(nxG.__dict__)

        # Initialise stations
        for _, node in G.nodes.items():
            
            # Node is not a station
            if random.random() > charging_stations:
                node["station"] = False
                node["startp"] = random.random()
                node["endp"] = random.random()
                continue 
            
            # Node is a station
            node["station"] = True
            node["startp"] = 0.0
            node["endp"] = 0.0
            node["swap_time"] = swap_time 
            



        return G


    @classmethod
    def from_file(cls, filename, charging_stations):
        """
        Same as from_nx_graph but it reads the MultiDiGraph from a 
        GraphML file.
        """
        nxG = ox.load_graphml(filename)
        return cls.from_nx_graph(nxG, charging_stations)

    
