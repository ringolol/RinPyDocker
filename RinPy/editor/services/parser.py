'''
Full grammatics for the interpretator:
    code        ::=  assig { ("\\n"|";") assig }*
    assig       ::=  "if" if_exp 
                        | "while" while_exp 
                        | "def" fun
                        | "return" expr
                        | { ASS } log_expr
    expr        ::=  term { ("+"|"-") term }*
    term        ::=  factor { ("*"|"/"|"@") factor }*
    factor      ::=  NUM | "(" log_expr ")" | '[' {log_expr}* ']' | named
    named       ::=  NAME {"[" log_expr "]"} {"(" {log_expr ","}* ")"}
    if_exp      ::=  "if" log_expr "{" code "}" 
                       { "else" if_exp }*
                       {"else" "{" code "}"}
    log_expr    ::=  log_term { "or" log_term }*
    log_term    ::=  cond { "and" cond }*
    cond        ::=  {"not"} expr { (">"|"<"|"=="|">="|"<="|"!=") expr }
    fun         ::=  "def" NAME "(" { pars } ")" "{" code "}"
    pars        ::=  { NAME "," }*
    while_exp   ::=  "while" cond "{" code "}"
    

Work in progress:
    for_exp     ::=  "for" named "=" "NUM":{"NUM":}"NUM" "{" code "}"
    named       ::=  NAME {"[" log_expr "]"} {"(" {log_expr ","}* ")"} {"." named}
'''

# Ideas:
#   - choose input and output to connect (medium)
#   - strings (medium?)
#   - proper numerical integration (very hard)
#   - for-cycle (easy)
#   - unit tests (hard)
#   - comments (easy)

# Issues
#   - block has only one input and output (it's bad)
#   - SignalVector has a parent, but not Vector itself

try:
    # works for django
    from .simulator import Sim, BLOCK_TYPES, Block, ReturnException
    from .parser_utils import master_pat, generate_tokens, \
            sys_funs, logic_funs
except ImportError:
    # works outside of django
    from simulator import Sim, BLOCK_TYPES, Block, ReturnException
    from parser_utils import master_pat, generate_tokens, \
            sys_funs, logic_funs


class Fun:
    '''class for storing functions and calculating them'''

    def __init__(self, name, par_names, body):
        self.name = name
        self._par_names = par_names
        self._body = body

    def __call__(self, pars, sim, memo_space, shared=False, sys=False):
        '''calculate function in sim space using pars as parameters 
            and memo_space as memory space'''

        if not shared:
            par_space = {k:v for k, v in zip(self._par_names, pars)}
            space = {**sys_funs} if sys else {}
            space = {**space, **memo_space, **par_space}
        else:
            space = memo_space
        try:
            out_val = ExpressionEvaluator(sim, space).parse(self._body)
        except ReturnException as ex:
            out_val = ex.val
        return out_val

    def __repr__(self):
        return f'Fun(name={self.name}, pars={tuple(self._par_names)})'


class ExpressionEvaluator:
    '''Recursive descent parser'''

    def __init__(self, sim = None, memory = None):
        '''init memory space and sim space'''

        # sim space
        self.sim = sim if sim else Sim()

        # memory space with vars and funs
        if not memory:
            self.memory = {**sys_funs}
        else:
            self.memory = memory

    def parse(self, inp):
        '''parse and evaluate expression from string in memory space'''

        # inp is either a list or a string
        # generate tokens or use inp as tokens
        if isinstance(inp, list):
            self.tokens = iter(inp)
        elif isinstance(inp, str):
            self.tokens = generate_tokens(inp)
        else:
            raise SyntaxError('inp must be a list of Tokens or a string')

        # init tok and nexttok
        self.tok = self.nexttok = None

        # advance to the first token
        self._advance()
            
        # start evaluating
        return self.code()

    def _advance(self):
        '''move by one token'''
        # print(self.nexttok.value if self.nexttok else '')
        self.tok, self.nexttok = self.nexttok, next(self.tokens, None)

    def _accept(self, toktype):
        '''try to _advance if nexttoken is toketype'''

        if self.nexttok and self.nexttok.type == toktype:
            self._advance()
            return True
        else:
            return False

    def _expect(self, toktype):
        '''_expect this toktype to occure next, else raise an exeption'''

        if not self._accept(toktype):
            raise SyntaxError(f'Expected {toktype}, got {self.nexttok}')

    def _skip_sep(self):
        while self._accept('NL') or self._accept('SEMICOLON'):
            pass

    def memory_dump(self):
        '''print memory dict'''

        print('\nMemory-dump:')
        for key in self.memory:
            print(f'{key}:\n  {self.memory[key]}')

    # functions for interpretator
    def code(self):
        '''
        code    ::=  assig { ('\\n'|';') assig }*
        '''

        self._skip_sep()
        res = self.assig()
        while self._accept('NL') or self._accept('SEMICOLON'):
            self._skip_sep()
            # handle empty expressions
            if not self.nexttok:
                return self.sim.create('num', [0])
            res = self.assig()
        
        return res

    def fun(self):
        '''
        "def" NAME "(" { pars } ")" "{" code "}"
        '''

        self._accept('NAME')
        name = self.tok.value
        self._expect('LPAREN')
        pars = self.pars()
        self._expect('RPAREN')
        self._expect('LCUBRACK')
        depth, body = 1, ''
        while depth > 0 or (self.nexttok and self.tok.value != '}'):
            if self.nexttok.value == '}':
                depth -= 1
            elif self.nexttok.value == '{':
                depth += 1
            body += self.tok.value
            self._advance()
        self.memory[name] = Fun(name, pars, body[1:])
        return self.memory[name]

    def assig(self):
        '''
        assig   ::=  "if" if_exp 
                | "while" while_exp 
                | "def" fun
                | "return" expr
                | { ASS } log_expr
        '''

        if self._accept('ASS'):
            name = self.tok.value[:-1].strip()
            exp = self.log_expr()
            self.memory[name] = exp
            return self.memory[name]
        elif self._accept('DEF'):
            return self.fun()
        elif self._accept('RETURN'):
            exp = self.expr()
            raise ReturnException(exp)
        elif self._accept('IF'):
            return self.if_exp()
        elif self._accept('FOR'):
            return self.for_exp()
        elif self._accept('WHILE'):
            self.while_exp()
        else:
            return self.log_expr()

    def pars(self):
        '''
        pars ::= { NAME {','} }*
        '''

        pars = []
        while self._accept('NAME'):
            pars.append(self.tok.value)
            self._accept('COMMA')
        return pars

    def expr(self):
        '''
        expr ::= term { ('+'|'-') term }*
        '''

        expval = self.term()
        while self._accept('PLUS') or self._accept('MINUS'):
            op = self.tok.type
            right = self.term()
            if op == 'PLUS':
                expval += right
            elif op == 'MINUS':
                expval -= right
        return expval

    def term(self):
        '''
        term ::= factor { ('*'|'/'|'@') factor }*
        '''

        termval = self.factor()
        while self._accept('TIMES') or self._accept('DIVIDE') \
                or self._accept('DOG'):
            op = self.tok.type
            right = self.factor()
            if op == 'TIMES':
                termval *= right
            elif op == 'DIVIDE':
                termval /= right
            elif op == 'DOG':
                termval @= right
        return termval

    def factor(self):
        '''
        factor  ::=  NUM | "(" log_expr ")" | '[' {log_expr}* ']' | named
        '''

        minus = self._accept('MINUS')
        if self._accept('NUM'):
            return self.sim.create('num', [(-1 if minus else 1)*float(self.tok.value)])
        elif self._accept('LPAREN'):
            expval = self.log_expr()
            self._expect('RPAREN')
            return -expval if minus else expval
        elif self._accept('LSQBRACK'):
            expr_flg = True
            arr = []
            while expr_flg:
                try:
                    exp = self.log_expr()
                    arr.append(exp)
                except SyntaxError:
                    if not self._accept('COMMA'):
                        expr_flg = False
            self._expect('RSQBRACK')
            return arr
        elif self._accept('NAME'):
            named = self.named(self.tok.value)
            if isinstance(named, Block):
                return -named if minus else named
            else:
                return named
        else:
            raise SyntaxError('expected a number, an open parentheses,'+
                    '\n\ta variable, or a function')

    def named(self, name):
        '''
        named       ::=  NAME {"[" log_expr "]"} {"(" {log_expr ","}* ")"}
        '''

        # it is function
        if self._accept('LSQBRACK'):
            exp = self.log_expr()
            num = exp.outputs[0].val
            val = self.memory[name][int(num)]
            self._expect('RSQBRACK')
            if isinstance(val, Fun):
                name = val.name
            elif isinstance(val, Block) or isinstance(val, list):
                self.memory['_'] = val
                try:
                    val = self.named('_')
                except SyntaxError:
                    pass
                return val
            else:
                raise SyntaxError(f'found unknown type in the array +' +
                        f'"type({val}) = {type(val)}"')
        if self._accept('LPAREN'):
            # while we are inside the function brackets 
            #   copy its content into par_str
            expr_flg = True
            pars = []
            while expr_flg:
                try:
                    exp = self.log_expr()
                    pars.append(exp)
                except SyntaxError:
                    if not self._accept('COMMA'):
                        expr_flg = False
            self._expect('RPAREN')

            if name in BLOCK_TYPES:
                return self.sim.create(name, pars)

            out_val = self.memory[name](pars=pars, 
                                        memo_space=self.memory, 
                                        sim=self.sim)
            return out_val
            
        else: # it is var
            if name not in self.memory:
                # create dummy signal
                self.memory[name] = self.sim.create('num', [0])

            return self.memory[name]


    def cond(self):
        '''
        cond    ::=  {"not"} expr { (">"|"<"|"=="|">="|"<="|"!=") expr }
        '''

        is_not = True if self._accept('NOT') else False
        left_expr = self.expr()
        if self._accept('GT') or self._accept('LT') or self._accept('EQ') \
            or self._accept('GE') or self._accept('LE') or self._accept('NE'):
            op = self.tok.value
            right_expr = self.expr()
            res = logic_funs[op](left_expr, right_expr)
            return not res if is_not else res
        # raise Exception('expected a condition operator: >|<|>=|<=|!=|==')
        return not left_expr if is_not else left_expr

    def if_exp(self, skip=False):
        '''
        if_exp      ::=  "if" log_expr "{" code "}" 
                           { "else" if_exp }* 
                           {"else" "{" code "}"}
        '''

        statement = self.log_expr()
        if not isinstance(statement, bool):
            raise SyntaxError('Expected a boolean value')
        self._skip_sep()
        self._expect('LCUBRACK')
        if skip or not statement:
            depth = 1
            while depth > 0 or (self.nexttok and self.tok.value != '}'):
                if self.nexttok.value == '}':
                    depth -= 1
                elif self.nexttok.value == '{':
                    depth += 1
                self._advance()
        else:
            try:
                self.code()
            except SyntaxError:
                skip = True
                if not self._accept('RCUBRACK'):
                    raise SyntaxError('expected RCUBRACK')

        self._skip_sep()
        
        if self._accept("ELSE"):
            self._skip_sep()
            if self._accept("IF"):
                self.if_exp(skip)
            elif not skip:
                self._expect('LCUBRACK')
                try:
                    self.code()
                except SyntaxError:
                    if not self._accept('RCUBRACK'):
                        raise SyntaxError('expected RCUBRACK')
            else:
                # todo make a function out of it!
                self._expect('LCUBRACK')
                depth = 1
                while depth > 0 or (self.nexttok and self.tok.value != '}'):
                    if self.nexttok.value == '}':
                        depth -= 1
                    elif self.nexttok.value == '{':
                        depth += 1
                    self._advance()
                self._accept('RCUBRACK')
        return None

    def log_expr(self):
        '''
        log_expr::=  log_term { "or" log_term }*
        '''

        expval = self.log_term()
        while self._accept('OR'):
            right = self.log_term()
            if not (isinstance(expval, bool) and isinstance(right, bool)):
                raise SyntaxError('Expected a boolean value')
            expval |= right
        return expval

    def log_term(self):
        '''
        log_term::=  cond { "and" cond }*
        '''

        termval = self.cond()
        while self._accept('AND'):
            right = self.cond()
            if not (isinstance(termval, bool) and isinstance(right, bool)):
                raise SyntaxError('Expected a boolean value')
            termval &= right
        return termval

    def while_exp(self):
        '''
        while_exp   ::=  "while" cond "{" code "}"
        '''

        cond = ''
        while self.nexttok.value != '{':
            cond += self.nexttok.value
            self._advance()
            
        cond_fun = Fun('', [], cond)
        # print(cond_fun)
        self._expect('LCUBRACK')

        depth, body = 1, ''
        while depth > 0 or (self.nexttok and self.tok.value != '}'):
            if self.nexttok.value == '}':
                depth -= 1
            elif self.nexttok.value == '{':
                depth += 1
            body += self.tok.value
            self._advance()
        body_fun = Fun('', [], body[1:])
        while cond_fun([], memo_space=self.memory, sim=self.sim):
            body_fun([], memo_space=self.memory, sim=self.sim, shared=True)

        return None

    def for_exp(self):
        '''
        for-exp ::=  "for" named "=" "NUM":{"NUM":}"NUM" "{" code "}"
        '''
        raise NotImplementedError('For-loop is not yet implemented')
    


if __name__ == '__main__':
    # test
    arithmetic = (2, 1)  # calced only once
    test_set = [
        # ('', 0, arithmetic),
        ('2*(1-2)', -2, arithmetic),
        ('1+1*3*(5-2*(1-2))', 22, arithmetic),
        ('x=2', 2, arithmetic),
        ('x+1', 3, arithmetic),
        ('y+5', Exception('exception'), arithmetic),
        ('def k(y) { x + y }', None, arithmetic),
        ('k(3)', 5, arithmetic),
        ('3+4*(z=3)', Exception('exception'), arithmetic),
        ('z', Exception('exception'), arithmetic),
        ('def f() { 2 + 3 * 2 }', None, arithmetic),
        ('def avg(x, y) { (x + y) / 2 }', None, arithmetic),
        ('avg(5+3, 2*3)', 7, arithmetic),
        ('avg(5+(3+5)*3*2+((((1)))), 2*3)', 30, arithmetic),
        ('f()', 8, arithmetic),
        ('avg(f(), avg(avg(2, 4), 3))', 5.5, arithmetic),
        ('def sum(x, y, z) { x + y + z }', None, arithmetic),
        (
            'sum(f(), avg(sum(1,1,1),3), sum(f(), f(), avg(8, f())))', 
            35, 
            arithmetic
        ),
        ('1/0', Exception('exception'), arithmetic),
        (
            'x = 1; y = integ(); e = x - y; e @ y; t = time(); calc(0.02, 10); plot(t, y)', 
            None, 
            (0.01, 5)
        ),
        ('plot(t, y)', None, (0.01, 5)),
        ('avg', None, arithmetic),
        ('x', None, arithmetic),
        ('arr = [1, 2, avg, x]', None, arithmetic),
        ('arr[0]', 1, arithmetic),
        ('arr[2](2,3)', 2.5, arithmetic),
        ('arr[3]', 1, arithmetic),
        ('arr2 = [14, f(), f, 88]', None, arithmetic),
        ('arr2[0]', None, arithmetic),
        ('arr2[1]', None, arithmetic),
        ('arr2[2]', None, arithmetic),
        ('arr2[2]()', None, arithmetic),
        ('arr2[3]', None, arithmetic),
    ]

    parser = ExpressionEvaluator()

    for case, real_ans, sim_pars in test_set:
        try:
            end_block = parser.parse(case)
            if isinstance(end_block, Block):
                parser.sim.calc(*sim_pars)
                solution = end_block.outputs[0].val
            else:
                solution = None
        except Exception as e:
            solution = e
        are_exceptions = (isinstance(real_ans, Exception) 
                and isinstance(solution, Exception))
        if real_ans == None or solution == real_ans or are_exceptions:
            print(f'CORRECT -- "{case}" => "{solution}"')
        else:
            print(f'INCORRECT -- "{case}" => GOT "{solution}"'+
                    f' BUT INSPECTED "{real_ans}"')
            res = 'INCORRECT'
   
    parser.memory_dump()