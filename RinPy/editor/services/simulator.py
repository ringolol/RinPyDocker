# Signals can be operated like numbers
#   1) Signals operations, where [node] is an output node:
#     -  a+b => (a)->[+sum+]<-(b)
#     -  a-b => (a)->[+sum-]<-(b)
#     -  a*b => (a)->[b]
#     -  a/b => (a)->[1/b]
#     -  -a  => (a)->[gain] or [-a]?
#     -  |a| => (a)->[abs]
#     -  ...
#   2) Signal operations return signals
#   3) A constant in signal expression is a signal
#       (probably a source signal)
#   4) Signals are connected into a web
#   5) The simulation is working on the whole web


from collections import namedtuple
from numbers import Number
from math import isclose

import termplotlib as tpl


class ReturnException(Exception):
    def __init__(self, val):
        super().__init__()
        self.val = val


class SimException(Exception):
    pass

# class Array(list): # in use!
#     '''array which can store FUNs and blocks'''
#     pass


# namedtuple for blocks
BlockType = namedtuple('BlockType', [
    'inert',        # if block is not inert we integrate it
    'source',       # if block is source it is calced first
    'inpN',         # number of inputs
    'outpN',        # number of outputs
    'def_pars',     # default parameters
    'def_states'    # default states
])

# numeric integrals
def rect_meth(t, dt, xn, dx):
    # x(n+1) = x(n) + (t2-t1)*dx
    return xn + dt*dx

# blocks' functions
def num(t, dt, inputs, outputs, pars, states, source):
    if not source:
        outputs[0].val = pars[0] * inputs[0].val
    else:
        outputs[0].val = pars[0]

def add(t, dt, inputs, outputs, pars, states, source):
    outputs[0].val = inputs[0].val + inputs[1].val

def integ(t, dt, inputs, outputs, pars, states, source):
    return inputs[0].val if inputs[0] != None \
        and inputs[0].val != None else 0

def div(t, dt, inputs, outputs, pars, states, source):
    outputs[0].val = inputs[0].val / inputs[1].val

def mult(t, dt, inputs, outputs, pars, states, source):
    outputs[0].val = inputs[0].val * inputs[1].val

def time(t, dt, inputs, outputs, pars, states, source):
    outputs[0].val = t

def fun(t, dt, inputs, outputs, pars, states, source):
    f = pars[0]
    sim = Sim()
    outs = f(pars=[sim.create('num', [inp.val]) for inp in inputs.values()], 
                    sim=sim, memo_space={}, sys=True).outputs
    for inx, out in enumerate(outs.values()):
        outputs[inx].val = out.val

# blocks
BLOCK_TYPES = {
    'num':      BlockType(True,  True,  1, 1, [1], []),
    'add':      BlockType(True,  False, 2, 1, [], []),
    'integ':    BlockType(False, True,  1, 1, [], [0]),
    'div':      BlockType(True,  False, 2, 1, [], []),
    'mult':     BlockType(True,  False, 2, 1, [], []),
    'time':     BlockType(True,  True,  0, 1, [], []),
    'fun':      BlockType(True,  True,  1, 1, [None, None], []),
}

# functions for blocks
BLOCK_FUNCTIONS = {
    'num':      num,
    'add':      add,
    'integ':    integ,
    'div':      div,
    'mult':     mult,
    'time':     time,
    'fun':      fun,
}


class Sim:
    '''class for creating block schemes and simulating them'''

    def __init__(self):
        self.blocks = []
        self.t_hist = None

    def create(self, name, pars=None, states=None):
        '''add block to simulation using name, parameters (pars) and states'''
        block = Block(name, pars, states, self)
        self.blocks.append(block)
        if name == 'num':
            block.calc(2, 1)
        return block

    def calc(self, dt, tmax):
        '''calculate for tmax time with step dt'''
        t = 0
        self.t_hist = []
        self.reset()
        
        while t <= tmax:
            sim_blocks = self.blocks
            cont_flg = True
            while sim_blocks:
                cont_flg = False
                non_calc = []
                for block in sim_blocks:
                    if block.source or block.is_ready():
                        try:
                            block.calc(t, dt)
                        except Exception as ex:
                            print(ex)
                        cont_flg = True
                    else:
                        non_calc.append(block)
                sim_blocks = non_calc

                if not cont_flg and sim_blocks:
                    print('-----------inf-cycle-----------')
                    print(sim_blocks)
                    print('-------------------------------')
                    break
            self.t_hist.append(t)
            t += dt

    def reset(self):
        for block in self.blocks:
            block.set_ready(False)

    def __repr__(self):
        string = '-----Sim()-----\n'
        for block in self.blocks:
            string += str(block) + '\n'
        string += '--------------'
        return string


class Signal:
    '''simple signal between blocks'''
    def __init__(self, parent=None):
        self.ready = False
        self._val = 0
        self.parent = parent
        self.hist = []

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value
        self.hist.append(value)

    def reset(self, flg = False):
        self.ready = flg

    def __repr__(self):
        return f'Signal(val={self.val}, parent={self.parent.name})'

    def __mul__(self, other):
        m = self.sim.create('mult')
        m.inputs[0] = self
        m.inputs[1] = other
        m.upd_and_calc()
        return m.outputs[0]

    def __matmul__(self, other):
        dic = other.parent.inputs
        oinx = list(dic.keys())[list(dic.values()).index(other)]
        other.parent.inputs[oinx] = self
        other.parent.upd_and_calc()
        return other

    def __add__(self, other):
        s = self.sim.create('add')
        s.inputs[0] = self
        s.inputs[1] = other
        s.upd_and_calc()
        return s.outputs[0]

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        '''used for negation of signal, e.g. [b1]-->[-1]-->'''
        g = self.sim.create('num', [-1])
        n = self.parent @ g
        n.upd_and_calc()
        return n.outputs[0]

    def __truediv__(self, other):
        '''divides one signal by another'''
        d = self.sim.create('div')
        d.inputs[0] = self
        d.inputs[1] = other
        d.upd_and_calc()
        return d.outputs[0]


class Block:
    '''a sim block'''

    def __init__(self, name, pars, states, sim):
        '''init block using its name, pars and states'''

        self.name = name
        (self.inert, self.source, inpN, outpN, 
                def_pars, def_states) = BLOCK_TYPES[name]

        if pars == None:
            self.pars = def_pars[:]
        elif len(pars) == len(def_pars):
            self.pars = pars[:]
            if name == 'fun':
                inpN = int(self.pars[1].outputs[0].val)
                outpN = len(self.pars[0]._par_names)
        else:
            raise SimException(f'number of pars for block {name} does not match'+\
                    f', need {len(def_pars)} got {len(pars)}')

        self.inputs = { key:Signal(self) for key in range(inpN) }
        self.outputs = { key:Signal(self) for key in range(outpN) }
        self.const = self.inert

        if states == None:
            self.states = def_states[:]
        elif len(states) == len(def_states):
            self.states = states[:]
        else:
            raise SimException(f'states number for block {name} does not match'+\
                    f', need {len(def_states)} got {len(states)}')

        self.fun = BLOCK_FUNCTIONS[name]
        self.sim = sim

    def is_ready(self):
        '''return true if all inputs are ready'''
        return all([inp.ready for inp in self.inputs.values()])

    def set_ready(self, flg=True):
        '''set all outputs ready'''
        for outp in self.outputs.values():
            outp.reset(flg)

    # def is_connected(self):
    #     '''check if all signals are connected to some output 
    #         (always true for an output)'''
    #     return all(self._signals)

    # def copy(self):
    #     return Block(self.name, self.pars, self.states, self.sim)

    def calc(self, t, dt):
        if not self.source and not self.is_ready():
            return False

        '''calc the block'''
        if self.inert:
            # algebraic calculation
            self.fun(
                t, dt, self.inputs, 
                self.outputs, self.pars, self.states, self.source
            )
        else:
            # numeric integration
            dx12 = self.fun(
                t, dt, self.inputs, 
                self.outputs, self.pars, self.states, self.source
            )
            for i in range(len(self.states)-1, -1, -1):
                self.states[i] = rect_meth(t, dt, self.states[i], dx12)
                self.outputs[i].val = self.states[i]

        self.set_ready()
        return True

    def upd_and_calc(self):
        self.upd_const_flag()
        if self.const:
            self.calc(0, 0)

    def upd_const_flag(self):
        self.const = all([not inp or inp.parent.const for inp in self.inputs.values()])

    def __repr__(self):
        return f'Block(name={self.name}, pars={self.pars},'+\
            f' states={self.states}, inp={self.inputs}, outp={self.outputs})'

    def __mul__(self, other):
        '''multiply two signals'''
        m = self.sim.create('mult')
        m.inputs[0] = self.outputs[0]
        m.inputs[1] = other.outputs[0]
        m.upd_and_calc()
        return m

    def __matmul__(self, other):
        '''concatenatinate blocks, e.g. [b1]-->[b2]-->'''
        # num block after connection its input becomes a gain
        if other.name in ['num']:
            other.source = False
        other.inputs[0] = self.outputs[0]
        other.upd_and_calc()
        return other

    def __add__(self, other):
        '''used for summation of output signals of two blocks,
            e.g. [b1]-->(+  +)<--[b2]'''
        s = self.sim.create('add')
        s.inputs[0] = self.outputs[0]
        s.inputs[1] = other.outputs[0]
        s.upd_and_calc()
        return s

    def __sub__(self, other):
        '''used for substraction,
            e.g. [b1]-->(+  -)<--[b2]'''
        return self + (-other)

    def __neg__(self):
        '''used for negation of signal, e.g. [b1]-->[-1]-->'''
        g = self.sim.create('num', [-1])
        n = self @ g
        n.upd_and_calc()
        return n

    def __truediv__(self, other):
        '''divides one signal by another'''
        d = self.sim.create('div')
        d.inputs[0] = self.outputs[0]
        d.inputs[1] = other.outputs[0]
        d.upd_and_calc()
        return d
    
    def __lt__(self, other):
        return self.outputs[0].val < other.outputs[0].val

    def __eq__(self, other):
        return isclose(self.outputs[0].val, other.outputs[0].val)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return other.__lt__(self)

    def __ge__(self, other):
        return other.__lt__(self) or self.__eq__(other)


if __name__ == '__main__':
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

