from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

from .lib.editor_func import editor_main


@login_required
def editor(request):
    '''editor page'''
    space = editor_main(request)
    template = loader.get_template('editor/editor.html')

    return HttpResponse(template.render(space, request))
