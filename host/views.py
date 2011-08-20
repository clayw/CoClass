from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from forms import MakeHostForm 
from forms import CourseSessionForm 
from forms import MakeCourseForm 
from forms import SessionEditForm
from host.models import HostClass
from host.models import HostClassMember
from host.models import HostClassSession
from host.models import HostClassComment
from host.models import HostClassInvite
from host.models import HostClassSignup
from classes.models import CourseInfo
from classes.models import CourseInfoEditor
from classes.models import CourseInfoSession
from classes.models import Session
from django.contrib.auth.models import User
from places.models import Place
from django.contrib.auth.decorators import login_required
from datetime import datetime, time, timedelta
from accounts.forms import VenueForm
from accounts.models import create_account_from_email
from django.core.paginator import Paginator
from django.core.paginator import InvalidPage
from django.core.paginator import EmptyPage
from django.core.mail import send_mail
from auxiliary import int_to_base36
from auxiliary import base36_to_int
from auxiliary import generic_handle_pic
from django.shortcuts import get_object_or_404

from django_messages.forms import ComposeForm
@login_required
def signup(request, host_b36):
    host_id = base36_to_int(host_b36) 
    host_class = get_object_or_404(HostClass, pk=host_id)
    if host_class.privacy != 'c':# or host_class.is_member(request.user):
        host_class = HostClass.objects.get(pk=host_id)
        if request.method == 'POST':
            sender = request.user
            subject = 'Request to join %s' % (host_class.course.title)
            recipients = host_class.members.filter(editor__exact=True)
            #recipient = host_class.members.get(editor=True)
            form = ComposeForm({'body': request.POST.get('body'), 'subject':subject, 'recipient':'clay'})
            if form.is_valid():                    
                #message_list = form.save(sender=request.user)                                                                           
                body = form.cleaned_data['body']
                #request.user.message_set.create(message=(u"Message successfully sent."))
                from_user = request.user
                for to_user_hcm in recipients: 
                    to_user = to_user_hcm.user
                    hcs = HostClassSignup.requests.create(host_class=host_class, sender=from_user, recipient=to_user, subject=subject, body=body)
                    #hcs = HostClassSignup(host_class=host_class, message=message)
                    #hcs.save()
                return HttpResponseRedirect('/h/v/%s/' % (host_b36))
        else:
            form = ComposeForm()
            form.fields['recipient'].initial = ' '
            form.fields['subject'].initial = ' '
            form.fields['body'].initial = "I would like to take %s." % (host_class.course.title)

        #expert = HostClassExpert.objects.filter(host_class=host_class)
        return render_to_response('host/signup.html', {
            'host_class': host_class,
            'form': form
        }, context_instance=RequestContext(request))
@login_required
def change_status(request, host_b36, change, status, username):
    host_id = base36_to_int(host_b36) 
    host_class = HostClass.objects.get(pk=host_id)
    if host_class.is_admin(request.user):
        chx = {'remove':False, 'add':True}[change]
        user = User.objects.get(username=username)
        num_editors = host_class.members.filter(editor__exact=True).count()
        hcm = HostClassMember.objects.get(user=user, host_class=host_class)
        if status == 'admin' and (change == 'add' or num_editors > 1):
            hcm.editor = chx
            print 'making admin'
        elif status == 'expert':
            hcm.expert = chx
        hcm.save()
        return HttpResponseRedirect('/h/members/%s/' % (host_b36))

@login_required
def members(request, host_b36):
    host_id = base36_to_int(host_b36) 
    host_class = HostClass.objects.get(pk=host_id)
    user = request.user
    if host_class.is_admin(user):
        members = host_class.members.all()
        return render_to_response('host/edit_members.html', {
            'host_class':host_class,
            'members': members
        }, context_instance=RequestContext(request))


@login_required
def edit_class(request, host_b36):
    host_id = base36_to_int(host_b36) 
    host_class = HostClass.objects.get(pk=host_id)
    user = request.user

    places = None
    if request.user.is_authenticated():
        places = user.place.all()

    if host_class.is_admin(user):
        course = host_class.course
        if request.method == 'POST':
            post_data = request.POST
            course_form = MakeCourseForm(request.POST)
            session_form = CourseSessionForm(request.POST)
            place_form = VenueForm(post_data)
            if post_data['place'] == '-1':
                if place_form.is_valid():
                    place = place_form.save(request)
                else:
                    raise Exception("place not valid")
            else:
                place = Place.objects.get(pk=int(post_data["place"]))
            if course_form.is_valid() and session_form.is_valid():
                if not course.published: # and course.is_editor(request.user):
                    course.title = course_form.cleaned_data['title']
                    course.description = course_form.cleaned_data['description']
                    course.prereqs = course_form.cleaned_data['prerequisites']
                    #course.from_date = course_form.cleaned_data['from_date']
                    #course.course_number = course_form.cleaned_data['course_number']
                    course.url = course_form.cleaned_data['url']
                    course.save()
                hc = session_form.save(course, place, host_class)
                return HttpResponseRedirect('/h/e/%s/' % int_to_base36(hc.pk))
        else:
            course_form = MakeCourseForm({'title':course.title, 
                'description':course.description,
                'prerequisites':course.prereqs,
                #'from_date':course.from_date,
                #'course_number':course.course_number,
                'url':course.url })
            session_form = CourseSessionForm({'starting_date':host_class.disp_start_date, 
                'time':host_class.meeting_time, 
                'check_sunday': host_class.sunday,
                'check_monday': host_class.monday,
                'check_tuesday': host_class.tuesday,
                'check_wednesday': host_class.wednesday,
                'check_thursday': host_class.thursday,
                'check_friday': host_class.friday,
                'check_saturday': host_class.saturday,
                'privacy':host_class.privacy})

        return render_to_response('host/edit.html', {
            'host_class': host_class, 'course_form': course_form,
            'places': places, 'session_form': session_form
            }, context_instance=RequestContext(request))
    else:
        raise Http404

@login_required
def fork_class(request, host_b36):
    host_id = base36_to_int(host_b36) 
    host_class = HostClass.objects.get(pk=host_id)
    course = host_class.course
    if host_class.is_admin(request.user) and course.published: 
        ci = CourseInfo(title=course.title,
                description=course.description,
                prereqs=course.prereqs,
                #from_date=course.from_date,
                #course_number=course.course_number,
                url=course.url, previous_version=course)
        ci.save()
        i = 0
        for cis in course.course_info_session.all():
                cis = CourseInfoSession(course_info=ci, session=cis.session, session_number=i+1)
                i += 1
                cis.save()
        CourseInfoEditor(course_info=ci, editor=request.user, creator=True)
        host_class.course = ci
        host_class.save()
    return HttpResponseRedirect('/h/e/%s/' % (host_b36))


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(HostClassComment, pk=comment_id)
    host_class = comment.host_class
    if comment.host_member.user == request.user or host_class.is_admin(request.user):
        comment.delete()
        return HttpResponseRedirect(host_class.get_absolute_url())

def host_class(request, host_b36):
    host_id = base36_to_int(host_b36) 
    host_class = HostClass.objects.get(pk=host_id)

    try:
        hcm = host_class.members.get(user__exact=request.user)
    except:
        hcm = []

    course = host_class.course

    if host_class.privacy != 'c' or host_class.is_member(request.user):
        comments = host_class.comments.order_by('-time')
        members = host_class.members.all() 
        hcm_expert = filter(lambda x: x.expert, members)
        if request.method == 'POST':
            if hcm:
                host_member = host_class.members.filter(user__exact=request.user.id)[0]
                comment = request.POST['comment']
                nc = HostClassComment(host_class=host_class, host_member=host_member, comment=comment)
                nc.save()
            
        return render_to_response('host/host_class_new.html', {'host_class': host_class, 'course': course, 'comments': comments, 'members': members, 'hcm':hcm, 'hcm_expert':hcm_expert}, context_instance=RequestContext(request))

def ajax_calendar(request, host_b36):
    host_id = base36_to_int(host_b36) 
    host_class = HostClass.objects.get(pk=host_id)
    if host_class.privacy != 'c' or host_class.is_member(request.user):
        dates = host_class.dates.all()
        return render_to_response('host/ajax_calendar.html', {
            'dates': dates
            }, context_instance=RequestContext(request))

def ajax_place(request, host_b36):
    host_id = base36_to_int(host_b36) 
    host_class = HostClass.objects.get(pk=host_id)
    
    if host_class.privacy != 'c' or host_class.is_member(request.user):
        return render_to_response('host/ajax_place.html', {'host_class': host_class}, context_instance=RequestContext(request))

def ajax_sessions(request, host_b36, session_pk=None):
    host_id = base36_to_int(host_b36) 
    """
    Return the next session if no specific session number given
    """ 
    if session_pk:
        ses = HostClassSession.objects.get(pk=session_pk)
        host_class = ses.host_class
        session_id = ses.session_number()
    else:
        host_class = HostClass.objects.get(pk=host_id)
        session_id = request.GET.get('p', '1')
    if host_class.privacy != 'c' or host_class.is_member(request.user):
        meetings = host_class.dates.order_by('date')
        paginator = Paginator(meetings, 1)
        results = paginator.page(session_id)

        return render_to_response('host/ajax_sessions.html', {
            'host_class': host_class,
            'session': results.object_list[0],
            'results': results,
            'paginator': paginator,
            }, context_instance=RequestContext(request))

def ajax_session_post(request, host_b36, session_id=None):
    host_id = base36_to_int(host_b36) 
    if session_id:
        session = HostClassSession.objects.get(pk=session_id)
        host_class = session.host_class
    else: 
        session = None
        host_class = HostClass.objects.get(pk=host_id)
    if host_class.is_admin(request.user):
        form = SessionEditForm(request.GET)
        if form.is_valid():
            del_links, add_links = [], []
            for key in request.GET:
                keysp = key.split('_')
                value = request.GET[key]
                if keysp[0] == 'add':
                    add_links.append((value, request.GET['title_'+keysp[1]+'_'+keysp[2]]))
                    #sl = SessionLink(session=host_session.course_session, url=value, title=request.GET['title_'+keysp[1]+'_'+keysP[2]])
                    #sl.save()
                elif keysp[0] == 'del':
                    del_links.append(value)
                    #uuid = value
                    #sl = SessionLink.objects.get(pk=uuid)
                    #if sl.session == session.course_session:
                    #    sl.delete()
            host_session = form.save(host_class, session, del_links, add_links)
            return HttpResponse(host_session.render_hidden_input())
def ajax_session_propagate(request, host_b36, session_id):
    host_id = base36_to_int(host_b36) 
    session = HostClassSession.objects.get(pk=session_id)
    host_class = session.host_class
    if host_class.is_admin(request.user):
        hc_dates = host_class.dates.order_by('date').filter(date__gte=session.date)
        skip_till_ses = True
        for hc_ses in hc_dates:
            if skip_till_ses and hc_ses.uuid == session_id:
                skip_till_ses = False
            else:
                session.date = hc_ses.date
                session.save()
                session = hc_ses
        session.date = host_class.next_available_date()
        session.save()
        return HttpResponse('1')

def ajax_session_delete(request, host_b36, session_id):
    host_id = base36_to_int(host_b36) 
    if session_id:
        session = HostClassSession.objects.get(pk=session_id)
        host_class = session.host_class
    else: 
        session = None
        host_class = HostClass.objects.get(pk=host_id)
    if host_class.is_admin(request.user):
        cs = session.course_session
        #for link in cs.link.all():
        #    if link.active():
        #        link.delete()
        cs.delete()
        session.delete()
        return HttpResponse('1')

def ajax_session_edit(request, host_b36, session_id=None):
    host_id = base36_to_int(host_b36) 

    if session_id:
        session = HostClassSession.objects.get(pk=session_id)
        host_class = session.host_class
        cs = session.course_session
        form = SessionEditForm({'title':cs.title, 'description':cs.description, 'video_url':cs.video_url, 'date': session.date.date(), 'time':session.date.time()})
        dict = {'session': session, 'form': form, 'host_class': host_class,}
    else: 
        host_class = HostClass.objects.get(pk=host_id)
        form = SessionEditForm({'time':host_class.meeting_time, 'date':host_class.next_available_date()})
        dict = { 'form': form, 'host_class': host_class,}
    if host_class.is_admin(request.user):
        return render_to_response('host/ajax_session_edit.html', dict, context_instance=RequestContext(request))

def host_search(request):
    from classes.course_miners import youtube_playlist_to_data
    details = None
    if request.GET.has_key('q'):
        additional_vars = search_form(request.GET)
    if request.method == 'POST':
        course_form = MakeCourseForm(request.POST)
        if course_form.is_valid():
            clean_form = course_form.cleaned_data
            ci = CourseInfo(title=clean_form['title'], 
                    description=clean_form['description'], 
                    prereqs=clean_form['prerequisites'],
                    #from_date = course_form.cleaned_data['from_date'],
                    #course_number = course_form.cleaned_data['course_number'],
                    url = course_form.cleaned_data['url'])
            ci.save()
            try:
                if int(request.POST.get('links','0')) > 0:
                    course_data = youtube_playlist_to_data(clean_form['url'])
                    for i, entry in enumerate(course_data['links']):
                        title = entry.title.text    
                        if entry.location:
                            location = entry.location.text
                        content = entry.content.text
                        link = entry.link[0].href
                        session = Session(title=title, description=content, video_url=link)
                        session.save()
                        cis = CourseInfoSession(course_info=ci, session=session, session_number=i+1)
                        cis.save()
                        print 'session', session
            except: pass 
            ceditor = CourseInfoEditor(course_info=ci, editor=request.user, creator=True)
            ceditor.save()
            return HttpResponseRedirect('/h/create/%s/' % int_to_base36(ci.id))
    else:
        if request.GET.has_key('playlist_url'):
            course_data = youtube_playlist_to_data(request.GET.get('playlist_url', ''))
            course_form = MakeCourseForm(course_data)
            lenlinks = len(course_data['links'])
            details = mark_safe('This course has %d video lectures.  You can modify these in step 3.<input type="hidden" name="links" value="%s" />' % (lenlinks, lenlinks))
            if request.GET.has_key('a'):
                return render_to_response('host/incl/make_form.html', {'details': details, 'course_form': course_form}, context_instance=RequestContext(request))
        else:
            course_form = MakeCourseForm()
    render_vars = {'course_form': course_form, 
            'class_creater': True, 
            'playlist_url': request.GET.get('playlist_url', 'http://www.youtube.com/view_play_list?p=....')}
    if details:
        render_vars['details'] = details
    return render_to_response('host/make.html', render_vars, context_instance=RequestContext(request))

@login_required
def host_create(request, course_b36=None, additional_vars={}):
    course_id = base36_to_int(course_b36) 
    user = request.user
    places = None
    if request.user.is_authenticated():
        places = user.place.all()
    course = CourseInfo.objects.get(pk=course_id)
    if request.method == 'POST':
        post_data = request.POST
        session_form = CourseSessionForm(post_data) # this form captures basic info, MWF, start date, meeting time
        place_fm = VenueForm(post_data)
        if session_form.is_valid():
            if post_data['place'] == '-1':
                if place_fm.is_valid():
                    place = place_fm.save(request)
                else:
                    raise Exception("place not valid?")
            else:
                place = Place.objects.get(pk=int(post_data["place"]))
            hc = session_form.save(course, place)
            hc_member = HostClassMember(host_class=hc, user=request.user, editor=True)
            hc_member.save()
            sessions = course.course_info_session.all()
            if len(sessions) > 0:
                for course_info_session in sessions:
                    session = course_info_session.session
                    next_date = hc.next_available_date()
                    hcs = HostClassSession(host_class=hc, course_session=session, date=datetime.combine(next_date, hc.meeting_time))
                    hcs.save()
            next = request.POST.get('next', '')
            if next == '1':
                return HttpResponseRedirect('/h/meetings/%s/?next=1' % (int_to_base36(hc.id)))
            else:
                return HttpResponseRedirect('/h/v/%s/' % (int_to_base36(hc.pk)))
    else:
        session_form = CourseSessionForm()

    render_vars = {'course': course, 'places': places, 'session_form':session_form, 'class_creater': True}
    return render_to_response('host/make2.html', render_vars
        , context_instance=RequestContext(request))

def search_form(get_data):
    """ 
    This is an aux function to be used by ajax_search_form and host_search
    """
    #results_html = ajax_search_form(request)
    query = get_data.get('q', '')
    results_per_page = int(get_data.get('n', '25'))
    results = SearchQuerySet().models(CourseInfo).auto_query(query)
    paginator = Paginator(results, results_per_page)
    try:
        page = int(get_data.get('page', '1'))
    except ValueError:
        page = 1
    try:
        search_results = paginator.page(page)
    except (EmptyPage, InvalidPage):
        search_results = paginator.page(paginator.num_pages)
    render_vars = {'paginator': paginator, 'search_results': search_results}
    return render_vars


from haystack.query import SearchQuerySet
def ajax_search_form(request):
    """
    returns fully rendered table of course results
    """
    render_vars = search_form(request.GET)
    return render_to_response('search/incl/class_list.html', render_vars)
        


def edit_calendar(request, host_b36):
    host_id = base36_to_int(host_b36) 
    host_class = HostClass.objects.get(pk=host_id)
    host_sessions = host_class.dates.all()
    if host_class.is_admin(request.user):
        #created = host_class.created
        class_creater = request.REQUEST.get('next', '') == '1'
        print class_creater
        if request.method == 'POST':
            post_data = request.POST
            host_class_sessions = []
            hour = host_class.meeting_time.hour
            min = host_class.meeting_time.minute
            #if class_creater: #created:
            #    host_class.created = True
            #    host_class.save()
            for key in post_data:
                value = post_data[key]
                if key.startswith('h_'):
                    h_, session_id = key.split('_')
                    session = host_class.dates.get(pk=session_id)
                    trans_date = datetime.strptime(value, "%a_%b_%d_%Y %H:%M:%S")
                    if session.date != trans_date:
                        session.date = trans_date
                        session.save()
            next = request.POST.get('next', '')
            if not class_creater:
                return HttpResponseRedirect('/h/meetings/%s' % (int_to_base36(host_class.pk)))
            elif next == '1':
                return HttpResponseRedirect('/h/invite/%s/?next=1' % (int_to_base36(host_class.pk)))
            else:
                return HttpResponseRedirect('/h/v/%s/' % (int_to_base36(host_class.pk)))

        if not class_creater:
            ext_template = "host/base_edit.html"
        else:
            ext_template = "host/base.html"

        return render_to_response('host/edit_calendar.html', {
            'host_class': host_class, 'course': host_class.course, 'host_sessions':host_sessions, 'class_creater':class_creater,
            'ext_template': ext_template
            }, context_instance=RequestContext(request))
    else:
        return Http404


def invite(request, host_b36):
    host_id = base36_to_int(host_b36) 
    host_class = get_object_or_404(HostClass, pk=host_id)
    
    if host_class.is_member(request.user):
        contacts = request.user.contact.all()
        class_creater = request.GET.get('next', '') == '1'
        if request.method == 'POST':
            message = request.POST['message']
            from models import send_invite_letters
            invitee_list = []
            for key in request.POST:
                if key.startswith('inv'):
                    _inv, usrnm = key.split('-')
                    invitee = User.objects.get(username=usrnm)
                    if invitee in [c.to_contact for c in contacts]:
                        invitee_list.append(invitee)
            emails = request.POST['emails']
            if emails:
                email_list = emails.split(',')
            else:
                email_list = []
	    from CoClass.invite.models import PseudoUser
            for email in email_list:
                # regex validate email
                #invitee = create_pseudouser_or_get_user(email)
                print email
                invitee = PseudoUser.objects.create(email)
                host_class_to = ','.join([int_to_base36(host_class.pk), request.user.username])
                #req = Request(host_class_to_from=host_class_to_from)
                #req.save()
                invitee.host_class_to = host_class_to
                html_content = message
                html_content += "\n\nClick the link below to learn about taking %s.\n\n\nhttp://www.coclass.com/accounts/signup/?key=%s " % (host_class.course.title, invitee.activation_key)
                send_mail("%s wants you to take %s on CoClass" % (request.user.get_full_name(), host_class.course.title), html_content, 'clay@coclass.com', [email])
            print invitee_list
            send_invite_letters(to_users=invitee_list, from_user=request.user, host_class=host_class, body=message)
            return HttpResponseRedirect('/h/v/%s/' % (int_to_base36(host_class.pk)))
        message_initial = "Starting %s, I will be studying %s. We will meet %s at %s to watch video lectures.  You should join!" % (host_class.disp_start_date, host_class.course.title, host_class.render_days(), host_class.place.name )
        if not class_creater:
            ext_template = "host/base_edit.html"
        else:
            ext_template = "host/base.html"
        return render_to_response('host/invite.html', {
            'host_class':host_class, 
            'course':host_class.course, 
            'class_creater': class_creater, 
            'message': message_initial, 
            'contacts': contacts,
            'ext_template':ext_template
            }, context_instance=RequestContext(request))

