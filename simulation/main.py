from simulation.runner import SimulationRunner
from simulation.utils.io import export_configuration, read_configuration
from simulation.configuration import Config 
from simulation.graph import Graph


import matplotlib.pyplot as plt 
import time 
import simpy 
import multiprocessing
import os 
import json 



def run (id, return_dict, config_file):
    print(f"Worker {config_file + str(id)} started")
    config = read_configuration(config_file)
    env = simpy.Environment()
    G = Graph.from_file(env, config, stations=False, elevation=False, elevation_provider="open_elevation", timeout=20)
    sim = SimulationRunner(env, config, G)
    _start = time.time()
    sim()
    _end = time.time()
    #print("Computational time: ", round(_end - _start, 3), "s")
    #print("Total trips started: ", sim.total_trips)
    #print("Vehicles not arrived to destination: ", sim.failed_trips)
    #print("Graph topology problems: ", sim.nx_failed_trips)
    #print("Relative travel time: ", sim.relative_travel_time, " hours / km")
    #print("Relative travel time: ", round(sim.relative_travel_time * 60, 3), " mins / km")
    #print("Average waiting time at stations: ", round(sim.avg_waiting_time, 3), " s")

    return_dict[config_file + str(id)] = {
        "area" : config.GRAPH_FILE,
        "stations" : sum(1 for i in G.nodes if i['is_station']),
        "vehicles" : config.N_VEHICLES,
        "sharing" : config.SHARING,
        "wait_charge" : config.WAIT_CHARGE,
        "computational_time" :  round(_end - _start, 3),  # seconds
        "relative_travel_time" : round(sim.relative_travel_time * 60, 3),  # mins / km
        "avg_waiting" : round(sim.avg_waiting_time, 3),
        "avg_queue" : round(sim.avg_queue, 3)
    }
    print(f"Worker {config_file + str(id)} concluded")



def multiprocess_run():
    
    for filename in os.listdir("./configs/"):
        
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        jobs = []
        
        for i in range(3):
            proc = multiprocessing.Process(
                target=run, 
                args=(i, return_dict, "./configs/" + filename)
            )
            jobs.append(proc)
            proc.start()

        for proc in jobs:
            proc.join()

        with open("./results", "a") as file:
            file.write(json.dumps(return_dict))
            file.write("\n")

        



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
    