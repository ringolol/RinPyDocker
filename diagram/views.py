from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required


# @login_required
def diagram(request):
    '''diagram page'''
    template = loader.get_template('diagram/diagram.html')
    return HttpResponse(template.render({}, request))