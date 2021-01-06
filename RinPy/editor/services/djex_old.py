from subprocess import TimeoutExpired, run


def djex(request, code_str, file_path='', timeout=5):
    '''exec code_str and return print output or exeption text'''
    # get user name
    unique_id = request.user.username
    
    # write code into file
    with open(f'/home/restricted_user/.prog_{unique_id}.py', 'w') as f:
        f.write(code_str)

    # run code and return output and errors
    output = ''
    try:
        o = run(f'sudo su - restricted_user -c "python3 /home/restricted_user/.prog_{unique_id}.py"', shell=True, capture_output=True, timeout=timeout)
        print(o)
        output = o.stdout.decode("utf-8")
        output += o.stderr.decode("utf-8")
    # timeout exception
    except TimeoutExpired:
        output = 'You program exceded time limit of 5 seconds and was terminated.'

    return output
