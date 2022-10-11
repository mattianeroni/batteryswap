import simpy 
import functools 

from simulation.utils.check import check_configuration
from simulation.utils.configuration import export_configuration, read_configuration

from simulation.batteries import Battery
from simulation.configuration import Config 
from simulation.graph import Graph



def main (env, config):
    while True:
        yield env.timeout(80)



if __name__ == "__main__":

    env = simpy.Environment()

    config = Config() 
    assert check_configuration(config)

    G = graph.Graph.from_file("./graphs/Test.graphml", env, config, evelation=False)

    env.process(main(env, G, config))
    env.run(config.SIM_TIME)    


    for filename in ("Test.graphml", "Modena.graphml","Sassari.graphml","Barcelona.graphml", "Italy.graphml"):
        G = graph.Graph.from_file("./nxgraphs/" + filename, env, config, elevation=True, elevation_provider="open_elevation")
        G.plot()
        G.save("./graphs/" + filename)

    

    