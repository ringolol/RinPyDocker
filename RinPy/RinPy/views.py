from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.template import loader
from django.http import HttpResponse

def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("login")

def register(request):
    template = loader.get_template('registration/register.html')

    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')
 
    else:
        f = UserCreationForm()

    return HttpResponse(template.render({'form': f}, request))
    