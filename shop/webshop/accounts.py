from django.contrib.auth import authenticate, login, logout
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from models import *
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from products import * 
# for login view
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.contrib.sites.models import Site, RequestSite

@csrf_protect
@never_cache
def login_view(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm):
    """Displays the login form and handles the login action."""

    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- redirects to http://example.com should 
            # not be allowed, but things like /view/?param=http://example.com 
            # should be allowed. This regex checks if there is a '//' *before* a
            # question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)

    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)

    uform = UserCreationForm()
    pform = UserProfileForm()

    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        'uform': uform,
        'pform': pform,
    }, context_instance=RequestContext(request))


"""
def login_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    #next = "/"
    #if request.POST.has_key('next'):

    user = authenticate(username=username, password=password)
    if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
        login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect("/account/loggedin/")
    else:
        # Show an error page
        return HttpResponseRedirect("/account/invalid/")
"""

def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/")

def register_view(request):
    if request.method == 'POST':
        uform = UserCreationForm(request.POST)
        pform = UserProfileForm(data=request.POST)
        if uform.is_valid() and pform.is_valid():
            new_user = uform.save()
            i = UserProfile()
            i.user = new_user
            pform = UserProfileForm(data=request.POST, instance=i)
            up = pform.save()
            logged_user = authenticate(username=new_user.username, password=uform.cleaned_data['password1'])
            if logged_user is not None and logged_user.is_active:
                #successful auth
                login(request, logged_user)


            return HttpResponseRedirect("/")
    else:
        uform = UserCreationForm()
        pform = UserProfileForm()
    return render_to_response("registration/register.html", {
        'uform': uform,
        'pform': pform,
    },context_instance=RequestContext(request))

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email",]

class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user_kwargs = {} 
        if 'user' in kwargs:
            self.user = kwargs['instance'].user
            user_kwargs = kwargs.copy()
            user_kwargs['instance'] = self.user

        super(UserProfileForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        return super(UserProfileForm, self).save(*args, **kwargs)

    class Meta:
        model = UserProfile
        fields = ["homeAddress", "phoneNumber"]

@login_required
def account_view(request):
    msg = ""
    if request.method == "POST":
        uform = UserForm(data=request.POST, instance=request.user)
        pform = UserProfileForm(data=request.POST)

        if uform.is_valid() and pform.is_valid():
            uform.save()
            try:
                up = UserProfile.objects.get(user=request.user)
            except:
                up = UserProfile(user=request.user)

            pform = UserProfileForm(data=request.POST, instance=up)
            pform.save()
            msg = "Data successfully saved."

    else:
        uform = UserForm(instance=request.user)
        try:
            up = UserProfile.objects.get(user=request.user)
        except:
            up = None
        pform = UserProfileForm(instance=up)
    
    return render_to_response("registration/account.html", {
        'uform': uform,
        'pform': pform,
        'msg' : msg
    }, context_instance=RequestContext(request))
