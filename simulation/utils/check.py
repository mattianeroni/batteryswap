def check_configuration (config):
    """ Method used to check eventual uncorrectness in the configuration """
    
    _n_batteries = config.BATTERY_TYPES.__len__()
    for station_t in config.STATION_TYPES:
        if _n_batteries != len(station_t.chargers_capacities):
            raise Exception("Inconsistency detected in batteries number. Please, check length of chargers_capacities in stations.")


    # Return True if the controls are correctly concluded.
    return True
