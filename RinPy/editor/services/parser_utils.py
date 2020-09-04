import re
import collections

# console plot lib
#   - pip install termplotlib
#   - sudo apt install gnuplot -y
try:
    import termplotlib as tpl
except ImportError:
    print('termplotlib is not found')

try:
    from .simulator import Block
except ImportError:
    from simulator import Block

# tokens
NUM = r'(?P<NUM>\d+(?:\.\d*)?)'
PLUS = r'(?P<PLUS>\+)'
MINUS = r'(?P<MINUS>-)'
TIMES = r'(?P<TIMES>\*)'
DIVIDE = r'(?P<DIVIDE>/)'
DOG = r'(?P<DOG>@)'
LPAREN = r'(?P<LPAREN>\()'
RPAREN = r'(?P<RPAREN>\))'
WS = r'(?P<WS>[ \t\r\f\v]+)'
EQ = r'(?P<EQ>==)'          # EQ must be above EQUALS
GE = r'(?P<GE>>=)'          # GE must be above EQUALS and GT
LE = r'(?P<LE><=)'          # LE must be above EQUALS and LT
NE = r'(?P<NE>!=)'          # NE must be above EQUALS
GT = r'(?P<GT>>)'
LT = r'(?P<LT><)'
# ASS must be above NAME
ASS = r'(?P<ASS>[A-Za-z_][A-Za-z_0-9]*[ \t\r\f\v]*=(?!=))'
VAR = r'(?P<VAR>var)'       # VAR must be above NAME
DEF = r'(?P<DEF>def)'       # DEF must be above NAME
IF = r'(?P<IF>if)'          # IF must be above NAME
ELSE = r'(?P<ELSE>else)'    # ELSE must be above NAME
FOR = r'(?P<FOR>for)'       # FOR must be above NAME
WHILE = r'(?P<WHILE>while)' # WHILE must be above NAME
AND = r'(?P<AND>and)'       # AND must be above NAME
OR = r'(?P<OR>or)'          # OR must be above NAME
NOT = r'(?P<NOT>not)'       # NOT must be above NAME
RETURN = r'(?P<RETURN>return)' # RETURN must be above NAME
NAME = r'(?P<NAME>[A-Za-z_][A-Za-z_0-9]*)'
COMMA = r'(?P<COMMA>,)'
DOT = r'(?P<DOT>\.)'
NL = r'(?P<NL>\n)'
SEMICOLON = r'(?P<SEMICOLON>;)'
LSQBRACK = r'(?P<LSQBRACK>\[)'
RSQBRACK = r'(?P<RSQBRACK>\])'
LCUBRACK = r'(?P<LCUBRACK>{)'
RCUBRACK = r'(?P<RCUBRACK>})'

# master pattern
master_pat = re.compile('|'.join([
    NUM,        PLUS,       MINUS,
    TIMES,      DIVIDE,     DOG,
    LPAREN,     RPAREN,     WS,
    EQ,         GE,         LE,
    NE,         GT,         LT,
    ASS,        VAR,        DEF,
    IF,         ELSE,
    FOR,        WHILE,      AND,
    OR,
    NOT,        RETURN,     
    NAME,       COMMA,      DOT,
    NL,
    SEMICOLON,  LSQBRACK,   RSQBRACK,
    LCUBRACK,   RCUBRACK,   
]))

# named tuple for tokens
Token = collections.namedtuple('Token', ['type', 'value'])

# generate tokens from string
def generate_tokens(text):
    '''generate tokens from string'''
    scanner = master_pat.scanner(text)
    for m in iter(scanner.match, None):
        tok = Token(m.lastgroup, m.group())
        # skip spaces
        if tok.type != 'WS':
            yield tok


# system functions
def plot(pars, memo_space, sim):
    # todo use names in pars instead of signals
    '''plot function'''
    x_block, y_block = pars
    x = x_block.outputs[0].hist
    y = y_block.outputs[0].hist
    fig = tpl.figure()
    fig.plot(x, y, height=15)
    fig.show()
    return None

def calc(pars, memo_space, sim):
    dt, tmax = map(lambda b: b.pars[0], pars)
    sim.calc(dt, tmax)
    return None

def array_to_str(arr):
    elements = []
    for el in arr:
        if isinstance(el, Block):
            elements.append(str(el.outputs[0].val))
        elif isinstance(el, list):
            elements.append(array_to_str(el))
        else:
            elements.append(str(el))

    return f'[{", ".join(elements)}]'

def print_signal(pars, memo_space, sim):
    lines = []
    for par in pars:
        if isinstance(par, Block):
            # print('is block')
            # print(str(par))
            # lines.append(f'{par.block_type}_{par.id} = {round(par.outputs[0].val, 5)}')
            lines.append(str(par.outputs[0].val))
            # lines.append(str(par))
        elif isinstance(par, list):
            lines.append(array_to_str(par))
        else:
            lines.append(str(par))
    print(' '.join(lines))
    return None

def debug(pars, memo_space, sim):
    print(sim)
    

sys_funs = {'plot': plot, 'calc': calc, 'print': print_signal, 'debug': debug}

logic_funs = {
    '>':    lambda x, y: x > y,
    '<':    lambda x, y: x < y,
    '>=':   lambda x, y: x >= y,
    '<=':   lambda x, y: x <= y,
    '==':   lambda x, y: x == y,
    '!=':   lambda x, y: x != y,
    'not':  lambda x: not x,
}