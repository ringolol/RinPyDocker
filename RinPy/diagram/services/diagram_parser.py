import json
import io
from contextlib import redirect_stdout
import asyncio

from .djex import djex


def parse_diagram(diag):
    # diag = json.loads(diagram)

    code = ''
    disps = []

    for layer in diag['diag']['layers']:
        if layer['type'] == 'diagram-nodes':
            for model in layer['models'].values():
                model_id = "block_" + model['id'].replace('-', '')
                model_name = model['name']
                # if model_name == 'const':
                #     model_name = f'num'
                # elif model_name == 'gain':
                #     model_name = f'num'
                model_pars = list(map(float, model['parameters'].values()))
                model_states = list(map(float, model['states'].values()))
                code += f"{model_id} = {model_name}({model_pars}, {model_states})\n"
                if model['name'] == 'disp':
                    disps.append(model_id)
                for port in model['ports']:
                    port_name = port['name'].split('_')
                    code += f"port_{port['id'].replace('-', '')} = {model_id}.{port_name[0].lower()+f'[{port_name[1]}]'}\n"
    for layer in diag['diag']['layers']:
        if layer['type'] == 'diagram-links':
            for model in layer['models'].values():
                code += f"port_{model['sourcePort'].replace('-', '')} @ port_{model['targetPort'].replace('-', '')}\n"


    code += f"calc({diag['calc']['dt']}, {diag['calc']['t']})\n"

    for disp in disps:
        code += f"print({disp})\n"

    print(code)

    return djex(code)
