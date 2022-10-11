from simulation.runner import SimulationRunner
from simulation.utils.configuration import export_configuration, read_configuration
from simulation.configuration import Config 


if __name__ == "__main__":

    config = Config()
    sim = SimulationRunner(config)
    sim()
    
    

    