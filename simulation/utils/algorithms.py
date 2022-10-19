from networkx.algorithms.shortest_paths import astar

from simulation.utils.technical import consumption
from simulation.utils.technical import euclidean_distance
from simulation.exceptions import SimulationNoPath

import functools
import itertools
import collections 
import heapq
import osmnx as ox
import networkx as nx 



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

            # If we didn't pass through a station, a station search in neighbour nodes is required.
            # The research is done through Breath-First Search algorithm.
            if (bfs_path := neighbour_station(G, baseline_path[:i + 1], vehicle, level)):
                return bfs_path
            
            # No station even through the breath-first search
            raise SimulationNoPath 

    # The destion can be reached out without any stop.
    return tuple(baseline_path) 



def neighbour_station (G, path, vehicle, level):
    """
    This method is called when the vehicle is not able to reach 
    the destination without stopping at a charging station. 
    
    However, there is no charging station on the path the 
    vehicle is covering. 
    
    Because of this, starting from the last visited node, a 
    pseudo Breadth-First Search (BFS) is carried out to find 
    a charging station on a path different from the previously 
    defined one. 

    :param G: The graph.
    :param path: The covered nodes from the beginning of the 
                baseline path to the last considered node.
                NOTE: No nodes before the source are considered.
    :param vehicle: The vehicle.
    :param level: The current battery level.
    :return: A new path that is currently leaving the baseline path
            in order to reach a charging station.
    """
    N = len(path)

    for i, node in enumerate(reversed(path)):
        
        # Update the fuel if the vehicle retry
        if i > 0:
            successor = path[N - i]
            level += consumption(G[node][successor][0], vehicle)
        
        # Try to find a station with a Breath-First Search
        # We pass as tabu nodes the ones visited before the current node.
        # We do not consider the ones visited next, because there might 
        # be a shorter path to reach them, different by the A* path.
        path_to_station = station_breath_first_search(G, node, level, vehicle, set(path[:N - i]))
        if path_to_station:
            return tuple(itertools.chain( path[:N - i], path_to_station )) 

    # No path to station found
    return None
        
            



def station_breath_first_search (G, node, level, vehicle, tabu): 
    """
    This is a kind of Breath-First Search.
    As soon as a charging station is found, the path to reach it out
    is returned.

    NOTE: This algorithm can be refined, since it has a criticality. 
    A pure Breath-First Search (BFS) is currently implemented, hence once 
    a node is visited it cannot be visted anymore. This is not 100% 
    accurate since the same node, reached by different paths, may 
    be associated to a different remaining energy, and, because of this,
    it can offer different possibilities.
    A reasonable solution could be to use a dictionary instead of a set 
    for < explored_nodes > and define a maximum number each node can 
    be visited. 
    Even this solution has been tested and it seems there are no consistent
    differnces. A classic BFS was therefore implemented.

    NOTE: A possible extension of this algorithm could explore all 
    the nodes at the same level before stopping, collectiong all the 
    stations at the same level, and finally returning the closest to
    the target node.

    :param G: The graph.
    :param node: The root node the search starts from.
    :param level: The fuel level at the root node.
    :param vehicle: the vehicle.
    :param tabu: The set of tabu nodes which is not our interest visiting.
    :return: The path to the station found.
    """
    roots = [(0, node, [], level)]
    explored_nodes = set()

    while len(roots) > 0:

        # Get the next node strating from which we can look for a station
        tree_level, cnode, path, _level = heapq.heappop(roots)
        tree_level += 1

        # Visit the sons...
        for i, edge in G[cnode].items():

            # If the node can be reached with the remaining energy...
            if (i not in tabu) and (i not in explored_nodes) and (newlevel := _level - consumption(edge[0], vehicle)) >= 0:
                
                # A station was found
                if G.nodes[i]['is_station']:
                    return path + [i]
                
                # A reachable node that can be used later as root was found
                heapq.heappush(roots,  (tree_level, i, path + [i], newlevel) )
            
            # Update the set of explored nodes.
            explored_nodes.add(i)
    
    # No station found
    return None