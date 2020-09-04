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
    '''
    ReturnException is raised when user defined function
        returns a value
    '''

    def __init__(self, val):
        super().__init__()
        self.val = val


class SimException(Exception):
    '''Exception that is raised in simulator'''

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
    '''
    the simplest numeric integral:
        x(n+1) = x(n) + (t2-t1)*dx
    '''

    return xn + dt*dx


# blocks' functions
def num(t, dt, inputs, outputs, pars, states, source):
    '''
    a num block can be either a constant source or 
        a gain
    '''

    if not source: # is gain
        outputs[0].val = pars[0] * inputs[0].val
    else: # is source
        outputs[0].val = pars[0]

def add(t, dt, inputs, outputs, pars, states, source):
    '''add outputs from two blocks'''

    outputs[0].val = inputs[0].val + inputs[1].val

def integ(t, dt, inputs, outputs, pars, states, source):
    '''an integrator (1/s)'''

    if inputs[0] != None and inputs[0].val != None:
        return inputs[0].val
    return states[0]

def div(t, dt, inputs, outputs, pars, states, source):
    '''div outputs from two blocks'''

    outputs[0].val = inputs[0].val / inputs[1].val

def mult(t, dt, inputs, outputs, pars, states, source):
    '''mult outputs from two blocks'''

    outputs[0].val = inputs[0].val * inputs[1].val

def time(t, dt, inputs, outputs, pars, states, source):
    '''return sim time'''

    outputs[0].val = t

def fun(t, dt, inputs, outputs, pars, states, source):
    '''
    creates a function block from a user function
        pars[0] -- Fun(...),
        pars[1] -- outputs size
    '''

    f = pars[0]
    sim = Sim()
    p = [sim.create('num', [inp.val]) for inp in inputs]
    outs = f(pars=p, sim=sim, memo_space={}, sys=True)
    for inx in range(len(outputs)):
        outputs[inx].val = outs[inx].outputs[0].val


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
        '''add block to simulation using name, pars and states'''

        block = Block(name, pars, states, self)
        self.blocks.append(block)
        if name == 'num':
            block.upd_and_calc()
        return block

    def calc(self, dt, tmax):
        '''simulate the system for tmax time with step dt'''

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
                            raise ex
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
        '''reset all blocks ready flag'''

        for block in self.blocks:
            block.set_ready(False)

    def __repr__(self):
        string = '-----Sim()-----\n'
        for block in self.blocks:
            string += str(block) + '\n'
        string += '--------------'
        return string


class Signal:
    '''
    simple signal between blocks class
        parent -- signal parant block
        val -- signal value
        ready -- if true signal have been calculated
                    during this sim
        sim -- the simulator
        hist -- history of val values (for plots)
    '''

    def __init__(self, parent, sim):
        self.ready = False
        self.parent = parent
        self.sim = sim
        self.hist = []
        self.val = 0

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
        return f'Signal(val={self.val}, parent={self.parent.block_type})'

    def __mul__(self, other):
        m = self.sim.create('mult')
        m.inputs[0] = self
        m.inputs[1] = other
        m.upd_and_calc()
        return m.outputs[0]

    def __matmul__(self, other):
        lst = other.parent.inputs
        oinx = lst.index(other)
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

    def __init__(self, block_type, pars, states, sim):
        '''
        init block using its name, pars and states
            block_type -- block type (num, add, sub, fun, integ...)
            pars -- user defined parameters
            states -- user defined states
            sim -- the simulator
            inert -- if block is not inert use numeric integration
                to calc it else use fun directly
            source -- if block is source it doesn't need to wait
                for inputs
            fun -- block behavior, tells how outputs should be calced
            inputs -- block inputs, a list of signals
            outputs -- block outputs, a list of signals
            const -- constant blocks can be calculated in place
                ex: 1 + 2 = 3, but 1 + integ() = ?
        '''

        self.block_type = block_type

        # get block default parameters (not just pars) by its type
        (self.inert, self.source, inpN, outpN, 
                def_pars, def_states) = BLOCK_TYPES[block_type]

        # try to insert user parameters into block
        if pars == None:
            self.pars = def_pars[:]
        elif len(pars) == len(def_pars):
            self.pars = pars[:]
            # todo: rethink the way of changing inps num
            if block_type == 'fun':
                outpN = int(self.pars[1].outputs[0].val)
                inpN = len(self.pars[0]._par_names)
        else:
            raise SimException(f'number of pars for block {block_type} does not match'+\
                    f', need {len(def_pars)} got {len(pars)}')

        # try to insert user states into block
        if states == None:
            self.states = def_states[:]
        elif len(states) == len(def_states):
            self.states = states[:]
        else:
            raise SimException(f'states number for block {block_type} does not match'+\
                    f', need {len(def_states)} got {len(states)}')

        self.fun = BLOCK_FUNCTIONS[block_type]
        self.sim = sim

        self.inputs = [ Signal(self, self.sim) for _ in range(inpN) ]
        self.outputs = [ Signal(self, self.sim) for _ in range(outpN) ]
        self.const = self.inert

    def is_ready(self):
        '''return true if all inputs are ready'''

        return all([inp.ready for inp in self.inputs])

    def set_ready(self, flg=True):
        '''set all outputs ready'''

        for outp in self.outputs:
            outp.reset(flg)

    # def is_connected(self):
    #     '''check if all signals are connected to some output 
    #         (always true for an output)'''
    #     return all(self._signals)

    # def copy(self):
    #     return Block(self.block_type, self.pars, self.states, self.sim)

    def calc(self, t, dt):
        '''
        one iteration of calc for the block
            t -> t + dt'''

        # block is not ready for calc
        if not self.source and not self.is_ready():
            return False

        if self.inert: # algebraic calculation
            self.fun(
                t, dt, self.inputs, 
                self.outputs, self.pars, self.states, self.source
            )
        else: # numeric integration
            dx12 = self.fun(
                t, dt, self.inputs, 
                self.outputs, self.pars, self.states, self.source
            )
            # integ and upd states
            for i in range(len(self.states)-1, -1, -1):
                self.states[i] = rect_meth(t, dt, self.states[i], dx12)
                self.outputs[i].val = self.states[i]

        # ready up outputs
        self.set_ready()
        return True

    def upd_and_calc(self):
        '''upd block outputs (for const blocks)'''

        # todo: check if block is const?
        self.upd_const_flag()
        if self.const:
            self.calc(0, 0)

    def upd_const_flag(self):
        '''check if block is still constant'''

        self.const = all([not inp or inp.parent.const for inp in self.inputs]) \
                and self.const

    def __repr__(self):
        return f'Block(name={self.block_type}, pars={self.pars},'+\
            f' states={self.states}, inp={self.inputs}, outp={self.outputs})'

    def __mul__(self, other):
        '''multiply output signals from two blocks'''
        m = self.sim.create('mult')
        m.inputs[0] = self.outputs[0]
        m.inputs[1] = other.outputs[0]
        m.upd_and_calc()
        return m

    def __matmul__(self, other):
        '''concatenatinate blocks, e.g. [b1]-->[b2]-->'''
        # num block after connection its input becomes a gain
        if other.block_type in ['num']:
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
        