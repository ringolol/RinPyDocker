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