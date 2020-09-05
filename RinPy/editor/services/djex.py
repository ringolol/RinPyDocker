import io
from contextlib import redirect_stdout
import asyncio

try:
    from .parser import ExpressionEvaluator
except ImportError:
    from parser import ExpressionEvaluator

# use docker instead of this stone-age technology!

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