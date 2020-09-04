from parser import ExpressionEvaluator


code = '''
var x = 1
var y = integ()
var e = x - y
e @ y
var t = time()
calc(0.01, 10)
plot(t, y)
print(y)
print(e)
'''

code2 = '''
var x = 1
var dy = integ()
var y = dy @ integ()
var kdy = dy @ 0.3
var e = x - (kdy + y)
e @ dy
var t = time()
calc(0.01, 15)
plot(t, y)
plot(y, dy)
print(y)
'''

code3 = '''
def f() { 
  var x = 1
  calc(2, 1)
  print(x)
}
f()
'''

code4 = '''
var i = 0
while i < 10 {
 print(i)
 var i = i + 1
}
'''

code5 = '''
var y = x@2
var x = 10
calc(2, 1)
print(y)
'''

code6 = '''
def sign(x) {
  if x >= 0 {
    return 1
  } else {
    return -1
  }
}
var s = 1
var y = integ()
var e = s - y
e @ y
var t = time()
var z = y - 0.5
var temp = sign(z)
calc(0.01, 10)
plot(t, temp)
print(y)
print(e)
'''

code7 = '''
def sign(x) {
  if x >= 0 {
    return 1
  } else {
    return -1
  }
}
var s = 10
var dy = integ()
var y = dy @ integ()
var p = dy @ 0.3 + y
var e = s - p
var r = sign(e) @ 10
r @ dy
var t = time()
calc(0.001, 20)
plot(t, y)
plot(y, dy)
'''

p = ExpressionEvaluator()
p.parse(code6)
p.memory_dump()


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