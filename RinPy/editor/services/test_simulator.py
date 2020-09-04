import unittest
from simulator import Sim

class TestSimulator(unittest.TestCase):
    def test_sim(self):
        sim = Sim()
        memory = {}
        memory['c'] = sim.create('num', [2])
        memory['z'] = memory['c'] @ sim.create('num', [3])
        memory['c2'] = sim.create('num', [3])
        memory['y'] = memory['c'] + memory['c2']
        memory['b'] = -memory['c2']
        memory['x'] = memory['c'] - memory['c2']
        sim.calc(2, 1)
        print(sim)


# static system
sim = Sim()
memory = {}
memory['c'] = sim.create('num', [2])
memory['z'] = memory['c'] @ sim.create('num', [3])
memory['c2'] = sim.create('num', [3])
memory['y'] = memory['c'] + memory['c2']
memory['b'] = -memory['c2']
memory['x'] = memory['c'] - memory['c2']
sim.calc(2, 1)
print(sim)

# dynamic system #1
sim = Sim()
memory = {}
memory['x'] = sim.create('num', [1])
memory['y'] = sim.create('integ', [])
memory['e'] = memory['x'] - memory['y']
memory['e'] @ memory['y']
sim.calc(0.005, 20)
fig = tpl.figure()
fig.plot(sim.t_hist, memory['y'].outputs[0].hist, ylim=[0, 1.1])
fig.show()

# dynamic system #2
sim = Sim()
memory = {}
memory['x'] = sim.create('num', [1])
memory['dy'] = sim.create('integ')
memory['y'] = memory['dy'] @ sim.create('integ')
memory['kdy'] = memory['dy'] @ sim.create('num', [0.3])
memory['s']  = memory['kdy'] + memory['y']
memory['e'] = memory['x'] - memory['s']
(memory['e'] * sim.create('num', [1])) @ memory['dy']
sim.calc(0.001, 20)
fig = tpl.figure()
fig.plot(sim.t_hist, memory['y'].outputs[0].hist)
fig.show()
fig2 = tpl.figure()
fig2.plot(memory['y'].outputs[0].hist, memory['dy'].outputs[0].hist)
fig2.show()

# static #2
# 2*(1-2)
sim = Sim()
memory = {}
memory['x'] = sim.create('num', [1]) - sim.create('num', [2])
memory['y'] = sim.create('num', [2])*memory['x']
sim.calc(2, 1)
print(memory['x'], memory['y'])

# static #3
sim = Sim()
memory = {}
memory['y'] = sim.create('num', [14]) / sim.create('num', [2])
sim.calc(2, 1)
print(memory['y'])

# dynamic #3
sim = Sim()
memory = {}
memory['y'] = sim.create('integ')
sim.calc(0.01, 5)
fig = tpl.figure()
fig.plot(sim.t_hist, memory['y'].outputs[0].hist)
fig.show()

# logic #1
sim = Sim()
memory = {}
memory['x'] = sim.create('num', [15])
memory['y'] = sim.create('num', [15])
memory['z'] = sim.create('num', [14])
sim.calc(2, 1)
print(memory['x'] > memory['y'], memory['x'] == memory['y'], memory['x'] > memory['z'])