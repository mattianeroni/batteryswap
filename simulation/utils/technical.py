import math 



def seconds_to_hours (seconds):
    """ Convert a time in seconds to a time in hours """
    return seconds / 3600 



def hours_to_seconds (hours):
    """ Convert a time in hours to a time in seconds """
    return hours * 3600


def slope_to_grades (slope):
    """ Convert a slope (i.e., rise over run) to grades """
    return math.degrees(math.atan(slope))



def slope_to_rads (slope):
    """ Convert a slope (i.e., rise over run) to radiants """
    return math.atan(slope)



def charge_time(battery, power):
    """ 
    Method to calculate the charging time of a battery.
    
    Charging Time [3600 * kWh / kW] = (Battery Capacity - Battery Level) / Charger Power

    :param battery: The battery to charge.
    :param power: The power erogated by the charger.
    :return: Charging time in seconds
    """
    return int( hours_to_seconds( (battery.capacity - battery.level) / power ) )



def level_at_time (ctime, battery, power):
    """
    Method to calculate the level of a battery that is not fully charged 
    but started charging time ago.

    :param ctime: The instant of time in which we want to check the battery level.
    :param battery: The considered battery.
    :param power: The power erogated by the charger in kW. 
    :return: The current level of the battery.

    """
    passed_t = ctime - battery.start_charging
    required_t = charge_time(battery, power)

    if passed_t >= required_t:
        return battery.capacity 
    
    return battery.level + power * seconds_to_hours(passed_t) 



def missing_time_to_charge (ctime, battery, power):
    """
    This method measure the missing time before a battery to be 
    fully charged. This time is expressed in seconds.

    :param ctime: The instant of time in which we want to check the battery level.
    :param battery: The considered battery.
    :param power: The power erogated by the charger in kW. 
    :return: The current level of the battery.
    """
    passed_t = ctime - battery.start_charging
    required_t = charge_time(battery, power)
    
    return max(0, required_t - passed_t) 