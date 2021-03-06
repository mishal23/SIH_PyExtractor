from django.shortcuts import render
from server import models
from server import views
from server.models import Account
from django.http import HttpResponseRedirect
from server.forms import AccountRegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout

def home(request):

	return render(request, 'index.html')



def setup_view(request):
    if Account.objects.all().count() > 0:
        request.session['alert_success'] = "Setup has already been completed."
        return HttpResponseRedirect('/')
    # Get template data from the session
    template_data = views.parse_session(request,{'form_button':"Register"})
    # Proceed with rest of the view
    if request.method == 'POST':
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            views.register_user(
                form.cleaned_data['email'],
                form.cleaned_data['password_first'],
                Account.ACCOUNT_ADMIN
            )
            user = authenticate(
                username=form.cleaned_data['email'].lower(),  # Make sure it's lowercase
                password=form.cleaned_data['password_first']
            )
            login(request, user)
            request.session['alert_success'] = "Successfully setup PyExtractor's primary admin account."
            return HttpResponseRedirect('/profile/')
    else:
        form = AccountRegisterForm()
    template_data['form'] = form
    return render(request,'setup.html',template_data)



def logout_view(request):
    # Django deletes the session on logout, so we need to preserve any alerts currently waiting to be displayed
    saved_data = {}
    if request.session.has_key('alert_success'):
        saved_data['alert_success'] = request.session['alert_success']
    else:
        saved_data['alert_success'] = "You have successfully logged out."
    if request.session.has_key('alert_danger'):
        saved_data['alert_danger'] = request.session['alert_danger']
    logout(request)
    if 'alert_success' in saved_data:
        request.session['alert_success'] = saved_data['alert_success']
    if 'alert_danger' in saved_data:
        request.session['alert_danger'] = saved_data['alert_danger']
    return HttpResponseRedirect('/')


def login_view(request):
    # Authentication check. Users currently logged in cannot view this page.
    if request.user.is_authenticated:
        return HttpResponseRedirect('/explore/')
    # get template data from session
    template_data = views.parse_session(request,{'form_button':"Login"})
    # Proceed with the rest of view
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username = form.cleaned_data['email'].lower(),
                password = form.cleaned_data['password']
            )
            login(request,user)
            request.session['alert_success'] = "Successfully logged into PyExtractor."
            return HttpResponseRedirect('/explore/')
    else:
        form = LoginForm()
    template_data['form'] = form
    return render(request, 'login.html', template_data)


def register_view(request):
    # Authentication check. Users logged in cannot view this page.
    if request.user.is_authenticated:
        return HttpResponseRedirect('/profile/')
    elif Account.objects.all().count() == 0:
        return HttpResponseRedirect('/setup/')
    # Get template data from session
    template_data = views.parse_session(request, {'form_button': "Register"})
    # Proceed with rest of the view
    if request.method == 'POST':
        form = AccountRegisterForm(request.POST)
        if form.is_valid():
            views.register_user(
                form.cleaned_data['email'],
                form.cleaned_data['password_first'],
                Account.ACCOUNT_ADMIN
            )
            user = authenticate(
                username = form.cleaned_data['email'].lower(),
                password = form.cleaned_data['password_first']
            )
            login(request,user)
            request.session['alert_success'] = "Successfully registered with PyExtractor."
            return HttpResponseRedirect('/profile/')
    else:
        form = AccountRegisterForm()
    template_data['form'] = form
    return render(request,'register.html',template_data)


def error_denied_view(request):
    # Authentication check
    authentication_result = views.authentication_check(request)
    if authentication_result is not None:
        return authentication_result
    # Get template data from session
    template_data = views.parse_session(request)
    # Proceed with rest of the view
    return render(request,'denied.html',template_data)

