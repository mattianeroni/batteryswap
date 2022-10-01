import math 




def charge_time(battery, power):
    """ 
    Method to calculate the charging time of a battery.
    
    Charging Time [3600 * kWh / kW] = (Battery Capacity - Battery Level) / Charger Power

    :param battery: The battery to charge.
    :param power: The power erogated by the charger.
    :return: Charging time in seconds
    """
    return int(3600 * (battery.capacity - battery.level) / power )