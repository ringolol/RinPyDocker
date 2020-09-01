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