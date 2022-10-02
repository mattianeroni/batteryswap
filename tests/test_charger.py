import simpy 

from simulation.stations.charger import Charger 
from simulation.batteries import Battery, BatteryType
from simulation.utils.technical import charge_time, level_at_time, missing_time_to_charge, hours_to_seconds, seconds_to_hours


def putter(env, charger, battery):
    yield charger.put(battery)
    print(f"{env.now} - stored {battery}")


def getter(env, charger, waitcharge=True):
    i = yield charger.get(waitcharge=waitcharge)
    print(f"{env.now} - retrieved {i}")
    return i 


def test0(env, charger, batteries):
    for i, b in enumerate(batteries):
        yield charger.put(b)
        print(i)

    # OUTPUT
    # 0
    # 1
    # 2


def test1(env, charger, batteries):
    yield charger.put(batteries[0])
    print(
        "Time to charge : ", seconds_to_hours( charge_time(batteries[0], charger.power) ), ", ",
        f"Missing time to charge at {seconds_to_hours(int(env.now))} : ", seconds_to_hours( missing_time_to_charge(env.now, batteries[0], charger.power) ), ", ",
        f"Level at {seconds_to_hours(int(env.now))} : ", level_at_time(env.now, batteries[0], charger.power), ", "
    )
    yield env.timeout(3600)
    print(
        "Time to charge : ", seconds_to_hours( charge_time(batteries[0], charger.power) ), ", ",
        f"Missing time to charge at {seconds_to_hours(int(env.now))} : ", seconds_to_hours( missing_time_to_charge(env.now, batteries[0], charger.power) ), ", ",
        f"Level at {seconds_to_hours(int(env.now))} : ", level_at_time(env.now, batteries[0], charger.power), ", "
    )
    yield env.timeout(3600 * 3)
    print(
        "Time to charge : ", seconds_to_hours( charge_time(batteries[0], charger.power) ), ", ",
        f"Missing time to charge at {seconds_to_hours(int(env.now))} : ", seconds_to_hours( missing_time_to_charge(env.now, batteries[0], charger.power) ), ", ",
        f"Level at {seconds_to_hours(int(env.now))} : ", level_at_time(env.now, batteries[0], charger.power), ", "
    )

    # OUTPUT
    # Time to charge :  9.0 ,  Missing time to charge at 0.0 :  9.0 ,  Level at 0.0 :  10.0 , 
    # Time to charge :  9.0 ,  Missing time to charge at 1.0 :  8.0 ,  Level at 1.0 :  20.0 , 
    # Time to charge :  9.0 ,  Missing time to charge at 4.0 :  5.0 ,  Level at 4.0 :  50.0 , 


def test2(env, charger, batteries):
    env.process(getter(env, charger, waitcharge=False))
    env.process(getter(env, charger, waitcharge=False))
    env.process(getter(env, charger, waitcharge=False))
    env.process(getter(env, charger, waitcharge=False))

    yield env.timeout(20)

    for b in batteries:
        env.process(putter(env, charger, b))
        #syield env.timeout(1)

     

    yield env.timeout(10)




if __name__ == "__main__":
    tests = [
        #test0, test1,
        test2
    ]

    for proc in tests:
        print(proc.__name__)
        env = simpy.Environment()
        charger = Charger(env, capacity=3, power=10)

        btype = BatteryType(0, 100, 0.5)

        batteries = [
            Battery(btype, level=10),
            Battery(btype, level=20),
            Battery(btype, level=100),
            Battery(btype, level=50),
        ]

        env.process(proc(env, charger, batteries))
        env.run()
        print(end="\n\n")
