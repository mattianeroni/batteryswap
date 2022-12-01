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
    env.process(getter(env, charger, waitcharge=True))
    

    yield env.timeout(20)
    yield env.process(putter(env, charger, batteries[0]))

    yield env.timeout(20)
    yield env.process(putter(env, charger, batteries[1]))

    yield env.timeout(20)
    yield env.process(putter(env, charger, batteries[2]))

     

    yield env.timeout(10)




def test3 (env, charger, batteries):
    print(batteries)

    env.process(getter(env, charger, waitcharge=False))

    for i in batteries:
        env.process(putter(env, charger, i))
        
    yield env.timeout(10)
    print(charger.put_queue)
   
    #yield env.timeout(0)
    print(charger.items)

    i = yield env.process(getter(env, charger, waitcharge=True))
    i = yield env.process(getter(env, charger, waitcharge=True))
    i = yield env.process(getter(env, charger, waitcharge=False))








if __name__ == "__main__":
    tests = [
        
        test3
    ]

    for proc in tests:
        print(proc.__name__)
        env = simpy.Environment()
        charger = Charger(env, capacity=2, power=10)

        btype = BatteryType(0, 100)

        batteries = [
            Battery(btype, level=10),
            Battery(btype, level=10),
            Battery(btype, level=10),
            Battery(btype, level=10),
        ]

        env.process(proc(env, charger, batteries))
        env.run()
        print(end="\n\n")
