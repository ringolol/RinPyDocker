from subprocess import TimeoutExpired, run

# A Known Python Injection:
#   1""")
#   import os
#   print(os.system("ls -a"))
#   ("""


dec_code = \
'''
from sim_parser import ExpressionEvaluator
parser = ExpressionEvaluator()
parser.parse("""
{}
""")
'''

def djex(sim_code_str, timeout=30):
    '''execute sim_code_str and return print output and/or exception message'''

    # run code and return output and errors
    py_code = dec_code.format(sim_code_str)
    try:
        # f'docker exec rinpydocker_excecutor_1 python -c \'{py_code}\''
        o = run(f'docker run --rm rinpydocker_excecutor python -c \'{py_code}\'', 
            shell=True, 
            capture_output=True, 
            timeout=timeout
        )
        output = o.stdout.decode("utf-8")
        output += o.stderr.decode("utf-8")
    # timeout exception
    except TimeoutExpired:
        output = f'You program exceded time limit of {timeout} seconds and was terminated.'

    return output