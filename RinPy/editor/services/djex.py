from .parser import ExpressionEvaluator
import io
from contextlib import redirect_stdout
import asyncio

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
    return f.getvalue()

def djex(request, code_str, file_path='', timeout=30):
    '''exec code_str and return print output or exeption text'''
    try:
        out = asyncio.run(run_code(code_str, timeout))
    except Exception as e:
        raise
        out = str(e)
    return out