from networkx.algorithms.shortest_paths import astar

from simulation.utils.technical import consumption
from simulation.utils.technical import euclidean_distance
from simulation.exceptions import SimulationNoPath

import functools



def define_path (G, source, target, vehicle, level=None):
    """
    Algorithm used to find a path from a source to a target, by considering 
    stations and necessity to recharge.

    :param G: The graph.
    :param current_path: The currently defined path.
    :param source: The starting node.
    :param target: The destination.
    :param vehicle: The vehicle.
    :param level: The current level of vehicle batteries. If not passed it 
                is taken from vehicle instance.

    :return: The new path considering stops and necessity to recharge.
            A list of nodes representing the path, and a set of nodes
            representing the stations where a stop is needed.
    """
    # Define a baseline path with no stops using the A* algorithm
    baseline_path = astar.astar_path(G, source, target, heuristic=functools.partial(euclidean_distance, G=G), weight="length")
        
    # Init fuel level and keep track of last station visited
    level = level or vehicle.level
    last_station, last_station_pointer = None, None 

    # Iterate throught the nodes of the baseline to predict the consumption
    for i, (cnode, nextnode) in enumerate(zip(baseline_path[:-1], baseline_path[1:])):

        if ( nextlevel := level - consumption(G[cnode][nextnode][0], vehicle) ) >= 0:
            # We can reach out the next node...
            level = nextlevel
            # If the reached node is a station, it is saved as station.
            if G.nodes[nextnode]["is_station"]:
                last_station, last_station_pointer = nextnode, i + 1
        
        else:
            # We cannot reach out the next node...
            if last_station:
                # If we passed through a station, for the moment, we simply return 
                # the path to that station.
                return tuple(baseline_path[:last_station_pointer+1])
            # If we didn't pass through a station, a station search in neighbour nodes
            # is required.
            raise SimulationNoPath #neighbour_station()

    # The destion can be reached out without any stop.
    return tuple(baseline_path) 



def neighbour_station ():
    pass    