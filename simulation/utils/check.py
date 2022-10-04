def check_configuration (config, verbose=False):
    """ Method used to check eventual uncorrectness in the configuration """

    # Check batteries types number, capacity and consumption rate
    if verbose:
        print("[ ] Checking batteries parameters...")

    if hasattr(config.BATTERIES_CAPACITY, "__len__") and hasattr(config.BATTERIES_CONSUMPTION_RATE, "__len__"):
            
        i, j = len(config.BATTERIES_CAPACITY), len(config.BATTERIES_CONSUMPTION_RATE)

        if i != j:
            raise Exception("Undefined number of batteries. Check length of BATTERIES_CAPACITY and BATTERIES_CONSUMPTION_RATE.")
            
        _n = i 
        _capacities = config.BATTERIES_CAPACITY
        _consumption_rates = config.BATTERIES_CONSUMPTION_RATE
        
    elif hasattr(config.BATTERIES_CAPACITY, "__len__"):
        _n = len(config.BATTERIES_CAPACITY)
        _capacities = config.BATTERIES_CAPACITY
        _consumption_rates = [config.BATTERIES_CONSUMPTION_RATE] * _n
            
    elif hasattr(config.BATTERIES_CONSUMPTION_RATE, "__len__"):
        _n = len(config.BATTERIES_CONSUMPTION_RATE)
        _capacities = [config.BATTERIES_CAPACITY] * _n
        _consumption_rates = config.BATTERIES_CONSUMPTION_RATE
            
    else: 
        _n = config.N_BATTERIES 
        _capacities = [config.BATTERIES_CAPACITY] * _n
        _consumption_rates = [config.BATTERIES_CONSUMPTION_RATE] * _n

        
    if _n != config.N_BATTERIES:
        raise Exception("Number of batteries different by explicited number N_BATTERIES.")

    # Adjust parameters
    config.N_BATTERIES = _n 
    config.BATTERIES_CAPACITY = _capacities
    config.BATTERIES_CONSUMPTION_RATE = _consumption_rates

    if verbose:
        print("done")


    