# import io
# from contextlib import redirect_stdout
# import asyncio

# try:
#     from .parser import ExpressionEvaluator
# except ImportError:
#     from parser import ExpressionEvaluator

# # use docker instead of this stone-age technology!

# async def parse_code(code_str):
#     loop = asyncio.get_running_loop()
#     parser = ExpressionEvaluator()
#     out = await loop.run_in_executor(None, parser.parse, code_str)
#     return out

# async def run_code(code_str, timeout):
#     f = io.StringIO()
#     with redirect_stdout(f):
#         try:
#             await asyncio.wait_for(parse_code(code_str), timeout=timeout)
#         except asyncio.TimeoutError:
#             print(f'Program was running for more than {timeout} '+
#                     'sec and was terminated!')
#         except Exception as e:
#             # raise
#             print(str(e))
#     return f.getvalue()

# def djex(request, code_str, file_path='', timeout=30):
#     '''exec code_str and return print output or exeption text'''
    
#     out = asyncio.run(run_code(code_str, timeout))
#     return out


from subprocess import TimeoutExpired, run

try:
    from .parser import ExpressionEvaluator
except ImportError:
    from parser import ExpressionEvaluator

dec_code = \
'''
from parser import ExpressionEvaluator
parser = ExpressionEvaluator()
parser.parse("""
{}
""")
'''

def djex(request, sim_code_str, file_path='', timeout=30):
    '''exec code_str and return print output or exception text'''

    # run code and return output and errors
    py_code = dec_code.format(sim_code_str)
    output = ''
    try:
        o = run(f'docker exec rinpydocker_excecutor_1 python -c \'{py_code}\'', 
            shell=True, 
            capture_output=True, 
            timeout=timeout
        )
        output = o.stdout.decode("utf-8")
        output += o.stderr.decode("utf-8")
    # timeout exception
    except TimeoutExpired:
        output = 'You program exceded time limit of 5 seconds and was terminated.'

    return output

# print(djex({}, '''
# x = 1
# dy = integ()
# y = dy @ integ()
# kdy = dy @ 0.3
# e = x - (kdy + y)
# e @ dy
# t = time()
# calc(0.01, 15)
# plot(t, y)
# plot(y, dy)
# print(y)
# '''))