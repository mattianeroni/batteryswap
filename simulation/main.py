from simulation.runner import SimulationRunner
from simulation.utils.io import export_configuration, read_configuration
from simulation.configuration import Config 
from simulation.graph import Graph


import matplotlib.pyplot as plt 
import time 
import simpy 


if __name__ == "__main__":

    """
    env = simpy.Environment()

    config = read_configuration("./configs/config.json")
    G = Graph.from_file(env, config, stations=False, elevation=False, elevation_provider="open_elevation", timeout=20)
    


    sim = SimulationRunner(env, config, G)
    _start = time.time()
    sim()
    _end = time.time()
    print("Computational time: ", round(_end - _start, 3), "s")
    print("Total trips started: ", sim.total_trips)
    print("Vehicles not arrived to destination: ", sim.failed_trips)
    print("Graph topology problems: ", sim.nx_failed_trips)
    print("Relative travel time: ", sim.relative_travel_time, " hours / km")
    print("Relative travel time: ", round(sim.relative_travel_time * 60, 3), " mins / km")
    print("Average waiting time at stations: ", round(sim.avg_waiting_time, 3), " s")

    print("-------------------------------------------------------------------------")
    """
    config = read_configuration("./configs/config.json")
    config.SHARING = False
    env = simpy.Environment()
    G = Graph.from_file(env, config, stations=False, elevation=False, elevation_provider="open_elevation", timeout=20)
    sim = SimulationRunner(env, config, G)
    _start = time.time()
    sim()
    _end = time.time()
    print("Computational time: ", round(_end - _start, 3), "s")
    print("Total trips started: ", sim.total_trips)
    print("Vehicles not arrived to destination: ", sim.failed_trips)
    print("Graph topology problems: ", sim.nx_failed_trips)
    print("Relative travel time: ", sim.relative_travel_time, " hours / km")
    print("Relative travel time: ", round(sim.relative_travel_time * 60, 3), " mins / km")
    print("Average waiting time at stations: ", round(sim.avg_waiting_time, 3), " s")
    