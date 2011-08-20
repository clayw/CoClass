from django.contrib.auth import authenticate, login
from django.contrib import auth
from django.shortcuts import render_to_response, redirect, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect, Http404
from forms import SignInForm
from forms import SignUpForm
from forms import ProfileForm
from forms import VenueForm
from forms import PreferencesForm
from forms import ExpertForm
from forms import LostPassForm
from accounts.models import create_account, reset_pass
from django.contrib.auth.models import User
from models import UserProfile
import cStringIO as StringIO
import hashlib
from auxiliary import generic_handle_pic
from django.shortcuts import get_object_or_404

## following is taken from messages package version 0.4.2
from django.contrib.auth.decorators import login_required
from django.conf import settings

from auxiliary import secure_required


from django_messages.models import Message
from django_messages.forms import ComposeForm
from django_messages.utils import format_quote

from models import Contact

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None
## end of stuff from messages package

def lostpass(request):
    if request.method =='POST':
        form = LostPassForm(request.POST)
        if form.is_valid():
            reset_pass(form.cleaned_data['email'])
            return HttpResponseRedirect('/')
    else:
        form = LostPassForm()
    return render_to_response('accounts/lostpass.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def signin(request):
    if request.method == 'POST':
        form = SignInForm(request.POST) 
        if form.is_valid(): 
            user = form.cleaned_data['user']
            if form.cleaned_data['remember']:
                request.session.set_expiry(9999999)
            login(request, user)
            return HttpResponseRedirect('/accounts/') 
    else:
        form = SignInForm()
    return render_to_response('accounts/login.html', {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

def signup(request):
    import captcha
    email = ''
    key = request.REQUEST.get('key', '')
    pu = None
    if key:
        try:
            pu = PseudoUser.objects.get(pk=key)
            email = pu.email
        except:
            key = ''
    if request.method == 'POST':
        form = SignUpForm(request.POST) 
        check_captcha = captcha.submit(request.POST['recaptcha_challenge_field'], request.POST['recaptcha_response_field'], settings.RECAPTCHA_PRIVATE_KEY, request.META['REMOTE_ADDR'])
        if check_captcha.is_valid and form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            create_account(first_name, last_name, username, email, password)
            user = authenticate(username=username, password=password) 
            login(request, user)
            if pu:
                from auxiliary import base36_to_int
                hc_id, t = pu.host_class_to.split(',')
                hc = HostClass.objects.get(pk=base36_to_int(hc_id)) 
                hcm = HostClassMember(host_class=hc, user=user)
                hcm.save()
                return HttpResponseRedirect('/h/v/' + hc.pk)
            else:
                return HttpResponseRedirect('/accounts/edit/') 
    else:
        form = SignUpForm({'email': email})
    html_captcha = captcha.displayhtml(settings.RECAPTCHA_PUBLIC_KEY, use_ssl=True)

    return render_to_response('accounts/signup.html', {
        'form': form, 'key':key, 'html_captcha':html_captcha
    }, context_instance=RequestContext(request))

@login_required
def main(request):
    user = request.user
    message_list = Message.objects.inbox_for(request.user)
    return render_to_response('accounts/main.html', {
        'message_list': message_list, #'user': user,
    }, context_instance=RequestContext(request))

@login_required
def add_contact(request, username=None):
    profile_user = get_object_or_404(User, username=username)
    is_user = request.user == profile_user
    notacontact = request.user.is_authenticated() and not is_user and len(request.user.contact.filter(to_contact__exact=profile_user)) == 0
    if notacontact:
        Contact(to_contact=profile_user, from_contact=request.user).save()
        return HttpResponseRedirect('/users/%s/' % (profile_user.username)) # Redirect after POST

@login_required
def contact_list(request):
    return render_to_response('accounts/contact_list.html', {}, context_instance=RequestContext(request))

def profile(request, user_id=None, username=None):
    try:
        if user_id:
            profile_user = get_object_or_404(User, pk=user_id)
        else:
            profile_user = get_object_or_404(User, username=username)
    except User.DoesNotExist:
        raise Http404
    is_user = request.user == profile_user
    notacontact = request.user.is_authenticated() and not is_user and len(request.user.contact.filter(to_contact__exact=profile_user)) == 0

    host_members = profile_user.takings.all() # filter by user allowed to see
    return render_to_response('accounts/profile.html', {
        'profile_user': profile_user, 
        'host_members': host_members, 
        'notacontact': notacontact,
        'user': request.user,
    }, context_instance=RequestContext(request))

@login_required
def edit_profile(request):
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = ProfileForm(request.POST) 
        if form.is_valid():
            profile.interests = form.cleaned_data['interests']
            profile.background = form.cleaned_data['background']
            if request.FILES:
                image_data=request.FILES['photo_0']
                filename, ctx = generic_handle_pic(image_data)
                profile.user_pic.save(filename, ctx)
            profile.save()
            return HttpResponseRedirect('/user/%d/' % request.user.id) # Redirect after POST
    else:
        form = ProfileForm({'interests': profile.interests, 'background': profile.background})

    return render_to_response('accounts/edit_profile.html', {
        'form': form
    }, context_instance=RequestContext(request))

@login_required
def preferences(request):
    user = request.user
    
    profile = user.get_profile()
    if request.method == 'POST':
        form = PreferencesForm(request.POST) 
        if form.is_valid():
            return HttpResponseRedirect('/user/%d/' % user.id) # Redirect after POST
    else:
        form = PreferencesForm({'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            })

    return render_to_response('accounts/preferences.html', {
        'form': form
    }, context_instance=RequestContext(request))

@login_required
def classes(request):
    user = request.user
    host_members = user.takings.all()
    return render_to_response('accounts/account_courses.html', {
        'host_members': host_members
    }, context_instance=RequestContext(request))

@login_required
def place(request):
    places = request.user.place.all()
    return render_to_response('accounts/places.html', {
        'places': places
    }, context_instance=RequestContext(request))

@login_required
def edit_place(request, place_id=None):
    #if place_id:
        #place = 
    if request.method =='POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = VenueForm()
    return render_to_response('accounts/makeplace.html', {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required
def reply(request):
    pass

def profile_classes(request, user_id):
    user = User.objects.get(pk=user_id)
    profile = user.get_profile()
    host_members = user.takings.all()
    return render_to_response('accounts/profile_courses.html', {
        'profile': profile, 'host_members': host_members
    }, context_instance=RequestContext(request))

@login_required
def expert_settings(request):
    user = request.user
    places = user.place.all()
    try:
        expert = user.expert.all()[0]
    except:
        expert = None
    if request.method == 'POST':
        from accounts.forms import VenueForm
        from places.models import Place
        post_data = request.POST
        place_form = VenueForm(post_data)
        form = ExpertForm(request.POST, instance=expert)    
        if form.is_valid():
            if post_data['place'] == '-1':
                if place_form.is_valid():
                    place = place_form.save(request)
                else:
                    raise Exception("place not valid?")
            else:
                place = Place.objects.get(pk=int(post_data["place"]))
            expert = form.save(commit=False)
            expert.user = user
            expert.place = place
            if post_data.get('active', False):
                expert.privacy = 'a'
            expert.save()
            return HttpResponseRedirect('/users/%s/expert' % (request.user.username))
    else:
        form = ExpertForm(instance=expert)
    return render_to_response('accounts/expert_settings.html', {
        'expert': expert, 'form':form, 'places':places
    }, context_instance=RequestContext(request))

def expert_profile(request, username):
    profile_user = User.objects.get(username=username)
    profile = profile_user.get_profile()
    expert = profile_user.expert.all()[0]
    return render_to_response('accounts/expert_profile.html', {
        'expert': expert,
        'profile_user': profile_user,
        'profile': profile,
    }, context_instance=RequestContext(request))


@login_required
def expert_hire(request, username):
    profile_user = User.objects.get(username=username)
    expert =profile_user.expert.all()[0]
    host_class_members = request.user.takings.all()
    import django_messages.forms
    if request.method == 'POST':
        sender = request.user
        form = django_messages.forms.ComposeForm({'body': request.POST['body'], 'subject':"I would like to hire you as an expert", 'recipient': expert.user.username })
        if form.is_valid():
            from host.models import HostClass
            host_class_pk = request.POST.get('host_class')           
            host_class = HostClass.objects.get(pk=host_class_pk)
            if host_class.is_member(request.user):
                from models import ExpertSignup
                esr = ExpertSignup.requests.create(host_class=host_class, sender=request.user, recipient=profile_user, subject='I would like to hire you as an expert', body=form.cleaned_data['body'])
                print "expert requested"
                print esr
                request.user.message_set.create(                                                                         
                    message=(u"Message successfully sent."))    
                return HttpResponseRedirect('/accounts/')
    else:
        form = django_messages.forms.ComposeForm()
        form.fields['recipient'].initial = ' '
        form.fields['subject'].initial = ' '
        form.fields['body'].initial = "I am planning on taking a course and you may be knowledgeable in the subject matter.  Will you help me at the rate of %.2f?" % (expert.price)
    return render_to_response('accounts/compose_expert.html', {
        'expert': expert, 'profile': profile,
        'classes': classes, 'form': form,
        'host_class_members':host_class_members
    }, context_instance=RequestContext(request))


@login_required
def expert_agreement(request):
    try:
        request.POST['agree']
    except:
        raise Http404
    user = request.user
    from models import Expert
    expert = Expert(user=user)
    expert.save()
    return HttpResponseRedirect('/accounts/expert/')

def facebook_auth_complete(request):
    login(request, user)

    return HttpResponseRedirect('/')
    
