def check_configuration (config, verbose=False):
    """ Method used to check eventual uncorrectness in the configuration """

    # Check batteries types number, capacity and consumption rate
    if verbose:
        print("[ ] Checking batteries parameters...", end="")

    # If capacities and consumption rates are sequences they are kept as is, 
    # otherwise, if they are integers, they are repeated transforming them in tuples.
    # During this process che consistency of provided information is checked.
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
    config.BATTERIES_CAPACITY = tuple(_capacities)
    config.BATTERIES_CONSUMPTION_RATE = tuple(_consumption_rates)


    if verbose:
        print("done")



    

    # Check stations parameters 
    if verbose:
        print("[ ] Checking stations parameters...", end="")

    # Parameters which are just integers are transformed in sequences 
    if not hasattr(config.STATIONS_CAPACITY, "__len__"):
        config.STATIONS_CAPACITY = [config.STATIONS_CAPACITY]
    
    if type(config.CHARGERS[0]) == int:
        config.CHARGERS = [config.CHARGERS]

    if not hasattr(config.STATIONS_POWER, "__len__"):
        config.STATIONS_POWER = [config.STATIONS_POWER]


    max_len = max( i for i in (len(config.STATIONS_CAPACITY), len(config.CHARGERS), len(config.STATIONS_POWER)) if i > 1)

    if len(config.STATIONS_CAPACITY) == 1:
        config.STATIONS_CAPACITY = config.STATIONS_CAPACITY * max_len

    if len(config.CHARGERS) == 1:
        config.CHARGERS = config.CHARGERS * max_len

    if len(config.STATIONS_POWER) == 1:
        config.STATIONS_POWER = config.STATIONS_POWER * max_len


    # Check the consistency of provided information
    if config.CHARGER_SELECTION is None and len(config.CHARGERS) != len(config.STATIONS_CAPACITY):
        raise Exception("Define a CHARGER_SELECTION if the number of CHARGERS is different by the number of STATIONS_CAPACITY.")
    
    if config.POWER_SELECTION is None and len(config.STATIONS_POWER) != len(config.STATIONS_CAPACITY):
        raise Exception("Define a POWER_SELECTION if the number of STATIONS_POWER is different by the number of STATIONS_CAPACITY.")

    for caps in config.CHARGERS:
        if len(caps) != config.N_BATTERIES:
            raise Exception("Each element of CHARGERS must provide a capacity for each battery type.")
    
    if verbose:
        print("done")


    # Return True if the controls are correctly concluded.
    return True



    