import unittest
import io
from contextlib import redirect_stdout
import asyncio

from parser import ExpressionEvaluator


async def parse_code(code_str):
    loop = asyncio.get_running_loop()
    parser = ExpressionEvaluator()
    out = await loop.run_in_executor(None, parser.parse, code_str)
    return out

async def run_code(code_str, timeout):
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            await asyncio.wait_for(parse_code(code_str), timeout=timeout)
        except asyncio.TimeoutError:
            print(f'Program was running for more than {timeout} '+
                    'sec and was terminated!')
        except Exception as e:
            # raise
            print(str(e))
    return f.getvalue()

def djex(request, code_str, file_path='', timeout=30):
    '''exec code_str and return print output or exeption text'''
    
    out = asyncio.run(run_code(code_str, timeout))
    return out


code_add = '''
print(1+1)
''' # 2

code_mult = '''
print(2*2)
''' # 4

code_var = '''
x = 3
print(x)
''' # 3

code_if = '''
if 6 > 5 {
    print(1)
}
''' # 1

code_if2 = '''
if 5 > 6 {
    print(1)
}
''' # ...

code_if3 = '''
x = 6
if x > 5 {
    print(1)
}
''' # 1

code_if4 = '''
x = 6
y = 5
if x > y {
    print(1)
}
''' # 1

code_if_else = '''
x = 6
if x > 6 {
    print(1)
} else {
    print(2)
}
''' # 2

code_if_ifelse_else = '''
x = 5
y = 8
if x == y {
    print(1)
} else if x + 3 == y {
    print(2)
} else {
    print(3)
}
''' # 2

code_if_ifelse_else2 = '''
x = 5
y = 8
if x == y {
    print(1)
} else if x + 3 == y - 1 {
    print(2)
} else {
    print(3)
}
''' # 3

code_div_zero = '''
1/0
''' # div by zero

code_array = '''
a = [1, 2, 3]
print(a[1])
''' # 2

code_array2 = '''
a = [1, 2, [3]]
print(a[2])
''' # [3]

code_array3 = '''
a = [1, 2, [3]]
print(a[2][0])
''' # 3

code_nan = '''
print(a)
''' # nan

code_arithmetic = '''
a = 1+1*3*(5-2*(1-2))
print(a)
''' # 22

code_fun = '''
def foo() {
    print(1)
}
foo()
''' # 1

code_fun2 = '''
def foo(x) {
    print(2 + x * x)
}
foo(2)
''' # 6

code_fun3 = '''
def foo(x, y) {
    print(x * y)
}

foo(3, 5)
''' # 15

code_fun4 = '''
def foo() {
    return 42
}
print(foo())
''' # 42

code_while = '''
i = 0
while i < 10 {
 print(i)
 i = i + 1
}
''' # 1, 2, 3, ..., 9

code_array_fun = '''
def foo(x) {
    return 33
}
arr = [foo, 1]
print(arr[0]())
''' # 33

code_array_fun2 = '''
def foo(x) {
    return 33
}
arr = [foo, 1]
print(arr)
''' # [Fun(...), 1]

code_array_indexes_web = '''
x = [1, 2, 3, 4, 5]

i = 0
while i < 5 {
  print(x[i]*x[i])
  i = i + 1
}
''' # 1.0, 4.0, 9.0, 16.0, 25.0

code_fib_web = '''
def f(a, b, n) {
  if n > 0 {
    return f(b, a+b, n-1)
  } else {
    return b
  }
}

i = 0
while i < 10 {
  print(f(0, 1, i))
  i = i + 1
}
''' # ...

code_array_web = '''
def f(z) { 
  x = 1
  print(2*2, 3, x, f, z)
  return z
}

x = [4, f(5), [3, [4]]]
print(x)
''' # ...

code_fun_web = '''
def f() { 
  x = 1
  print(2*2, 3, x, f)
}

f()

'''

code_fun_blocks_web = '''
def foo(x, y) {
    return [x + y, 42 - y]
}

a = 1
b = time()
f = fun(foo, 2)
a.out[0] @ f.in[0]
b.out[0] @ f.in[1]
calc(0.1, 5)
print(f)
print(f.out[0])
print(f.out[1])
'''
# 6.0
# Signal(val=5.999999999999998, parent=fun)
# Signal(val=37.0, parent=fun)

code_harmonic_web = '''
x = 1
y = integ()
e = x - y
e @ y
t = time()
calc(0.001, 10)
print(y)
print(e)
'''
# 0.99995
# 5e-05

code_if_else_web = '''
i = 0
while i < 10 {
  if i > 5 {
    print(1, i) 
  } else {
    print(0, i) 
  }
  i = i + 1
}
'''
# 0.0 0.0
# 0.0 1.0
# 0.0 2.0
# 0.0 3.0
# 0.0 4.0
# 0.0 5.0
# 1.0 6.0
# 1.0 7.0
# 1.0 8.0
# 1.0 9.0

code_nested_arrays_web = '''
def foo(x) {
 return 42 
}

def bar(x) {
 print(x)
 print(x[2], x[2][0], x[2][0][0], x[3][0][0][1]()) 
}

x = [1, 2, [[13]], [[[1, foo]]]]
bar(x)
'''
# [1.0, 2.0, [[13.0]], [[[1.0, Fun(name=foo, pars=('x',))]]]]
# [[13.0]] [13.0] 13.0 42.0

code_nested_cycles = '''
i = 0
while i < 5 {
 j = 0
 while j < 5 {
  print(i, j)
  j = j + 1
 }
 i = i + 1
}
'''

# 0.0 0.0
# 0.0 1.0
# 0.0 2.0
# 0.0 3.0
# 0.0 4.0
# 1.0 0.0
# 1.0 1.0
# 1.0 2.0
# 1.0 3.0
# 1.0 4.0
# 2.0 0.0
# 2.0 1.0
# 2.0 2.0
# 2.0 3.0
# 2.0 4.0
# 3.0 0.0
# 3.0 1.0
# 3.0 2.0
# 3.0 3.0
# 3.0 4.0
# 4.0 0.0
# 4.0 1.0
# 4.0 2.0
# 4.0 3.0
# 4.0 4.0

code_oscillator_web = '''
x = 1
dy = integ()
y = dy @ integ()
kdy = dy @ 0.3
e = x - (kdy + y)
e @ dy
t = time()
calc(0.00001, 3)
print(y)
''' # 1.61094

code_signal_routing_web = '''
x = num(3)
y = 4
a = add()
b = mult()
x.out[0] @ a.in[0]
y.out[0] @ a.in[1]
print(a)
x.out[0] @ b.in[0]
a.out[0] @ b.in[1]
print(b)
''' # 7.0, 21.0

code_slide_web = '''
def sign(x) {
  if x >= 0 {
    return [1] 
  } else {
    return [-1]
  }
}

g = 1
dy = integ()
y = dy @ integ()
e = g - (y + 0.8*dy)
u = e @ fun(sign, 1)
u @ dy
t = time()
calc(0.00005, 2)
print(y)
''' # 0.84814


class TestParser(unittest.TestCase):

    def test_add(self):
        self.assertEqual(float(djex({}, code_add)), 2)

    def test_mult(self):
        self.assertEqual(float(djex({}, code_mult)), 4)

    def test_var(self):
        self.assertEqual(float(djex({}, code_var)), 3)

    def test_if(self):
        self.assertEqual(float(djex({}, code_if)), 1)

    def test_if2(self):
        self.assertEqual(djex({}, code_if2), '')

    def test_if3(self):
        self.assertEqual(float(djex({}, code_if3)), 1)

    def test_if4(self):
        self.assertEqual(float(djex({}, code_if4)), 1)

    def test_if_else(self):
        self.assertEqual(float(djex({}, code_if_else)), 2)

    def test_if_ifelse_else(self):
        self.assertEqual(float(djex({}, code_if_ifelse_else)), 2)

    def test_if_ifelse_else2(self):
        self.assertEqual(float(djex({}, code_if_ifelse_else2)), 3)
    
    def test_div_zero(self):
        self.assertIn('division by zero', djex({}, code_div_zero))

    def test_array(self):
        self.assertEqual(float(djex({}, code_array)), 2)

    def test_array2(self):
        self.assertEqual(djex({}, code_array2).strip(), '[3.0]')

    def test_array3(self):
        self.assertEqual(float(djex({}, code_array3)), 3)

    def test_nan(self):
        self.assertEqual(djex({}, code_nan).strip(), 'nan')

    def test_arithmetic(self):
        self.assertEqual(float(djex({}, code_arithmetic)), 22)

    def test_fun(self):
        self.assertEqual(float(djex({}, code_fun)), 1)

    def test_fun2(self):
        self.assertEqual(float(djex({}, code_fun2)), 6)

    def test_fun3(self):
        self.assertEqual(float(djex({}, code_fun3)), 15)

    def test_fun4(self):
        self.assertEqual(float(djex({}, code_fun4)), 42)

    def test_while(self):
        self.assertEqual(djex({}, code_while), '0.0\n1.0\n2.0\n3.0\n4.0\n5.0\n6.0\n7.0\n8.0\n9.0\n')

    def test_array_fun(self):
        self.assertEqual(float(djex({}, code_array_fun)), 33)

    def test_array_fun2(self):
        self.assertEqual(djex({}, code_array_fun2), "[Fun(name=foo, pars=('x',)), 1.0]\n")
    
    def test_array_indexes_web(self):
        self.assertEqual(djex({}, code_array_indexes_web), '1.0\n4.0\n9.0\n16.0\n25.0\n')

    def test_fib_web(self):
        self.assertEqual(djex({}, code_fib_web), '1.0\n1.0\n2.0\n3.0\n5.0\n8.0\n13.0\n21.0\n34.0\n55.0\n')

    def test_array_web(self):
        self.assertEqual(djex({}, code_array_web), "4.0 3.0 1.0 Fun(name=f, pars=('z',)) 5.0\n[4.0, 5.0, [3.0, [4.0]]]\n")

    def test_fun_web(self):
        self.assertEqual(djex({}, code_fun_web), '4.0 3.0 1.0 Fun(name=f, pars=())\n')

    def test_harmonic_web(self):
        self.assertEqual(djex({}, code_harmonic_web), '0.99995\n5e-05\n')

    def test_if_else_web(self):
        self.assertEqual(djex({}, code_if_else_web), '''0.0 0.0
0.0 1.0
0.0 2.0
0.0 3.0
0.0 4.0
0.0 5.0
1.0 6.0
1.0 7.0
1.0 8.0
1.0 9.0
''')

    def test_nested_arrays_web(self):
        self.assertEqual(djex({}, code_nested_arrays_web), "[1.0, 2.0, [[13.0]], [[[1.0, Fun(name=foo, pars=('x',))]]]]\n[[13.0]] [13.0] 13.0 42.0\n")

    def test_nested_cycles(self):
        self.assertEqual(djex({}, code_nested_cycles), '''0.0 0.0
0.0 1.0
0.0 2.0
0.0 3.0
0.0 4.0
1.0 0.0
1.0 1.0
1.0 2.0
1.0 3.0
1.0 4.0
2.0 0.0
2.0 1.0
2.0 2.0
2.0 3.0
2.0 4.0
3.0 0.0
3.0 1.0
3.0 2.0
3.0 3.0
3.0 4.0
4.0 0.0
4.0 1.0
4.0 2.0
4.0 3.0
4.0 4.0
''')

    def test_oscillator_web(self):
        self.assertAlmostEqual(float(djex({}, code_oscillator_web)), 1.61094)

    def test_signal_routing_web(self):
        self.assertEqual(djex({}, code_signal_routing_web), '7.0\n21.0\n')

    def test_slide_web(self):
        self.assertAlmostEqual(float(djex({}, code_slide_web)), 0.84814)


if __name__ == '__main__':
    unittest.main()