import simpy 


def putter (env, s, i):
    yield s.put(i)



def main (env, s):
    #env.process(putter(env, s, 'a'))
    yield s.put('a')
    print(f"{env.now} - {s.items}")

    yield env.timeout(10)

    yield s.get()
    print(f"{env.now} - {s.items}")

    yield env.timeout(10)

    for i in ("b", "c", "d"):
        #env.process(putter(env, s, i))
        s.put(i)
    print(f"{env.now} - {s.items}")

    yield env.timeout(10)

    yield s.get()
    print(f"{env.now} - {s.items}")

    


if __name__ == '__main__':
    env = simpy.Environment() 
    s = simpy.Store(env, capacity=2)
    env.process(main(env, s))
    env.run()