'''
Full grammatics for the interpretator:
    code        ::=  assig { ("\\n"|";") assig }*
    assig       ::= "def" fun
                        | "return" expr
                        | "if" if_exp 
                        | "for" for_exp         # not implemented
                        | "while" while_exp 
                        | ASS { log_expr }
    expr        ::=  term { ("+"|"-") term }*
    term        ::=  factor { ("*"|"/"|"@") factor }*
    factor      ::=  {+} {-} ( NUM | "(" log_expr ")" | '[' {log_expr}* ']' | named )
    named       ::=  NAME {"[" log_expr "]"} {"(" {log_expr ","}* ")"} {".in" | ".out"}
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
'''

# Ideas:
#   - strings (medium?)
#   - proper numerical integration (very hard)
#   - for-cycle (easy)
#   - unit tests (hard)
#   - comments (easy)

try:
    # works for django
    from .simulator import Sim, BLOCK_TYPES, Block, ReturnException, Signal
    from .parser_utils import master_pat, generate_tokens, \
            sys_funs, logic_funs
except ImportError:
    # works outside of django
    from simulator import Sim, BLOCK_TYPES, Block, ReturnException, Signal
    from parser_utils import master_pat, generate_tokens, \
            sys_funs, logic_funs


class Fun:
    '''class for storing functions and calculating them'''

    def __init__(self, name, par_names, body):
        self.name = name
        self._par_names = par_names
        self._body = body

    def __call__(self, pars, sim, memo_space, shared=False, sys=False):
        '''
        calculate function in sim space using pars as parameters 
            and memo_space as memory space
        if shared is True then vars will be inserted directly into memo_space
            (this is used in if-statements and while-loops)
        if sys is True then add systems function into name-space
        '''

        if not shared: # create separated name-space
            par_space = {k:v for k, v in zip(self._par_names, pars)}
            space = {**sys_funs} if sys else {}
            space = {**space, **memo_space, **par_space}
        else: # use existing name-space
            space = memo_space

        try:
            # calc function
            out_val = ExpressionEvaluator(sim, space).parse(self._body)
        except ReturnException as ex:
            out_val = ex.val # return value

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

        # print(self.nexttok) # debug
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
        '''skip ';' and '\\n' '''

        while self._accept('NL') or self._accept('SEMICOLON'):
            pass

    def memory_dump(self):
        '''print memory dict'''

        print('\nMemory-dump:')
        for key in self.memory:
            print(f'{key}:\n  {self.memory[key]}')

    def _get_body(self):
        '''get body of a function, an if-statement, a while-loop, etc.'''

        depth, body = 1, ''
        while depth > 0 or (self.nexttok and self.tok.value != '}'):
            if self.nexttok.value == '}':
                depth -= 1
            elif self.nexttok.value == '{':
                depth += 1
            body += self.tok.value
            self._advance()
        return body

    # ----------------SYNTAX---------------------------
    def code(self):
        '''
        code    ::=  assig { ('\\n'|';') assig }*
        '''

        self._skip_sep()
        res = self.assig()
        while self._accept('NL') or self._accept('SEMICOLON'):
            self._skip_sep()
            if not self.nexttok: # handle some empty expressions
                return None
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
        body = self._get_body()
        self.memory[name] = Fun(name, pars, body[1:])
        return self.memory[name]

    def assig(self):
        '''
        assig   ::= "def" fun
                        | "return" expr
                        | "if" if_exp 
                        | "for" for_exp         # not implemented
                        | "while" while_exp 
                        | ASS { log_expr }
        '''

        if self._accept('DEF'): # define function
            return self.fun()
        elif self._accept('RETURN'):
            # return from function,
            #   works like break inside a while loop
            exp = self.expr()
            raise ReturnException(exp)
        elif self._accept('IF'): # if-statement
            return self.if_exp()
        elif self._accept('FOR'): # for-loop in development
            return self.for_exp()
        elif self._accept('WHILE'): # while-loop
            self.while_exp()
            return None

        if self._accept('ASS'): # assign, e.g. var = ...
            name = self.tok.value[:-1].strip()
        else:
            name = '_'

        exp = self.log_expr()
        self.memory[name] = exp
        return self.memory[name]

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
        factor      ::=  {+} {-} ( NUM | "(" log_expr ")" | '[' {log_expr}* ']' | named )
        '''

        self._accept('PLUS')
        minus = self._accept('MINUS')
        if self._accept('NUM'):
            return self.sim.create('num', [
                (-1 if minus else 1) * float(self.tok.value)
            ])
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
        named       ::=  NAME {"[" log_expr "]"} {"(" {log_expr ","}* ")"} {".in" | ".out"}
        '''

        if self._accept('DOT'):
            self._expect('NAME')
            par = self.tok.value
            # dot syntax can be used only with .in and .out right now
            if par not in ['in', 'out']:
                raise SyntaxError('Dot syntax can be used only with .in and .out')
            else:
                par += 'puts'
            self.memory['_'] = getattr(self.memory[name], par)
            try:
                val = self.named('_')
            except SyntaxError:
                raise # todo: add some logic here
            return val
        elif self._accept('LSQBRACK'):
            exp = self.log_expr()
            num = exp.outputs[0].val
            val = self.memory[name][int(num)]
            self._expect('RSQBRACK')
            if isinstance(val, Fun):
                name = val.name
            elif isinstance(val, Block) or isinstance(val, list) or isinstance(val, Signal):
                self.memory['_'] = val
                try:
                    val = self.named('_')
                except SyntaxError:
                    raise # todo: add some logic here
                return val
            else:
                raise SyntaxError(f'found unknown type in the array ' +
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
            
        else: # it is a var
            if name not in self.memory:
                # create dummy signal
                self.memory[name] = self.sim.create('num', [float('nan')])

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
            self._get_body()
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
                self._expect('LCUBRACK')
                self._get_body()
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
        self._expect('LCUBRACK')
        body = self._get_body()

        body_fun = Fun('', [], body[1:])
        while cond_fun([], memo_space=self.memory, sim=self.sim):
            body_fun([], memo_space=self.memory, sim=self.sim, shared=True)

        return None

    def for_exp(self):
        '''
        for-exp ::=  "for" named "=" "NUM":{"NUM":}"NUM" "{" code "}"
        '''
        raise NotImplementedError('For-loop is not yet implemented')
    