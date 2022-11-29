from simulation.runner import SimulationRunner
from simulation.utils.io import export_configuration, read_configuration
from simulation.configuration import Config 


import matplotlib.pyplot as plt 
import time 


if __name__ == "__main__":

    config = read_configuration("./configs/config.json")

    sim = SimulationRunner(config, stations=False)

    


    _start = time.time()
    sim()
    _end = time.time()
    print("Computational time: ", round(_end - _start, 3), "s")
    print("Total trips started: ", sim.total_trips)
    print("Vehicles not arrived to destination: ", sim.failed_trips)
    print("Graph topology problems: ", sim.nx_failed_trips)
    print("Relative travel time: ", sim.relative_travel_time, " hours / km")
    print("Relative travel time: ", round(sim.relative_travel_time * 60, 3), " mins / km")
    print("Average waiting time at stations: ", sim.avg_waiting_time, " s")

    print("-------------------------------------------------------------------------")

    config = read_configuration("./configs/config.json")
    sim = SimulationRunner(config, stations=False)
    _start = time.time()
    sim()
    _end = time.time()
    print("Computational time: ", round(_end - _start, 3), "s")
    print("Total trips started: ", sim.total_trips)
    print("Vehicles not arrived to destination: ", sim.failed_trips)
    print("Graph topology problems: ", sim.nx_failed_trips)
    print("Relative travel time: ", sim.relative_travel_time, " hours / km")
    print("Relative travel time: ", round(sim.relative_travel_time * 60, 3), " mins / km")
    print("Average waiting time at stations: ", sim.avg_waiting_time, " s")
    

    