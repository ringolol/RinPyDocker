import json
import io
from contextlib import redirect_stdout
import asyncio

from sim_parser import ExpressionEvaluator


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

def djex(request, code_str, timeout=30):
    '''exec code_str and return print output or exception text'''
    
    out = asyncio.run(run_code(code_str, timeout))
    return out

with open('example.json') as f:
    diag = json.loads(f.read())

code = ''

disps = []

for layer in diag['ser']['layers']:
    if layer['type'] == 'diagram-nodes':
        for model in layer['models'].values():
            model_id = "block_" + model['id'].replace('-', '')
            model_name = model['name']
            if model_name == 'const':
                model_name = f'num'
            elif model_name == 'gain':
                model_name = f'gain'
            code += f"{model_id} = {model_name}()\n"
            if model['name'] == 'disp':
                disps.append(model_id)
            for port in model['ports']:
                port_name = port['name'].split('_')
                code += f"port_{port['id'].replace('-', '')} = {model_id}.{port_name[0].lower()+f'[{port_name[1]}]'}\n"

for layer in diag['ser']['layers']:
    if layer['type'] == 'diagram-links':
        for model in layer['models'].values():
            code += f"port_{model['sourcePort'].replace('-', '')} @ port_{model['targetPort'].replace('-', '')}\n"


code += f"calc({diag['calc']['dt']}, {diag['calc']['t']})\n"

for disp in disps:
    code += f"print({disp})\n"

code = code.replace('num()', '1') # temp solution

print(code)
print(djex({}, code))
