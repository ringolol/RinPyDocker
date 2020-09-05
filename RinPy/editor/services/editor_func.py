from os.path import isfile, join
from pathlib import Path
from subprocess import run
import os
import re

from . import djex


re_par_dir = re.compile(r'\$go_to_parents_directory\$(?P<num>[0-9]+)')


def editor_main(request):
    current_path = get_current_path(request)
    inpt, output, current_path = handle_button_click(request, current_path)
    files = list_files(current_path)
    directory = get_dir_path(current_path)
    space = {
        'output': output,
        'input': inpt,
        'files': files,
        'directory': directory,
    }
    return space

def get_current_path(request):
    # get editor path from cookies
    current_path = request.session.get('current_path', './default_user_files')
    print('current_path: ' + current_path)
    return current_path

def handle_button_click(request, current_path):
    output, inpt = '', 'print(2*2)'

    if(request.POST.get('runbtn')): # on btn_run click
        inpt = request.POST.get('code')
        # run code
        output  = djex.djex(request, inpt)
    
    else: # explorer functionality
        file_name = list(filter(lambda x: x != 'csrfmiddlewaretoken', 
                request.POST))
        if file_name: # if file/dir/up_btn was clicked
            inpt, current_path = explorer_func(inpt, current_path, file_name[0])
            request.session['current_path'] = str(current_path)
            
    return inpt, output, current_path

def explorer_func(inpt, current_path, file_name):
    # go one level up
    match_go_up = re_par_dir.match(file_name)
    if match_go_up:
        for _ in range(int(match_go_up.group('num'))):
            current_path = Path(current_path).parent
    # open file
    elif isfile(join(current_path, file_name)):
        with open(join(current_path, file_name)) as f:
            inpt = f.read()
    # open folder
    else:
        current_path = join(current_path, file_name)

    return inpt, current_path

def list_files(current_path):
    # list files in the explorer path
    try:
        # f = run(f'sudo su - restricted_user -c "ls {current_path}"', 
        #         shell=True, check=True, capture_output=True, timeout=5)
        f = run(f'docker exec rinpydocker_excecutor_1 ls {current_path}', 
                shell=True, check=True, capture_output=True, timeout=5)
        # folders are blue and files are white
        files = list(map(
            lambda x: (x, 'black' if isfile(join(current_path, x)) else 'blue'), 
            f.stdout.decode("utf-8").split('\n')
        ))[:-1]
    # if permission is denied or another exception have occurred return empty list
    except Exception:
        files = []

    return files

def get_dir_path(current_path):
    dir_names = ['Home'] \
        + list(filter(lambda x: x != '.', str(current_path).split('/')))
    directory = [
        (folder, len(dir_names) - inx - 1)
            for inx, folder in enumerate(dir_names)
    ]

    return directory