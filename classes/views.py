from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response

from host.forms import MakeCourseForm
from models import CourseInfo
from models import CourseInfoSession
from models import CourseInfoEditor
from models import CourseInfoRating
from models import Session
from models import Category
from auxiliary import base36_to_int
from auxiliary import int_to_base36
from classes.forms import SessionForm
from classes.forms import SessionAuxForm

from django.contrib.auth.models import User

from django.core.paginator import Paginator
from django.core.paginator import InvalidPage
from django.core.paginator import EmptyPage

from haystack.query import SearchQuerySet

@login_required
def edit_class(request, course_b36):
    course_id = base36_to_int(course_b36)
    course = get_object_or_404(CourseInfo, pk=course_id)
    if course.is_editor(request.user):
        if request.method == 'POST':
            form = MakeCourseForm(request.POST)
            if form.is_valid():
                course.title = form.cleaned_data['title']
                course.description = form.cleaned_data['description']
                course.prereqs = form.cleaned_data['prerequisites']
                #course.from_date = form.cleaned_data['from_date']
                #course.course_number = form.cleaned_data['course_number']
                course.url = form.cleaned_data['url']
                course.save()
        else: 
            form = MakeCourseForm({'title':course.title, 
                'description':course.description,
                'prerequisites':course.prereqs,
                'from_date':course.from_date,
                'course_number':course.course_number,
                'url':course.url })
        editors = course.editor.all()
        editors = [editor.editor for editor in editors]
        render_dict = { 'course': course, 'form': form, 'editors':editors }
        return render_to_response('classes/edit.html', render_dict
            , context_instance=RequestContext(request))

@login_required
def edit_session(request, course_b36, session_id):
    course_id = base36_to_int(course_b36)
    cis = CourseInfoSession.objects.get(pk=session_id) 
    session = cis.session
    course = CourseInfo.objects.get(pk=course_id)
    if course.is_editor(request.user):
        if request.method == 'POST':
            form = SessionForm(request.POST)
            session_aux_form = SessionAux_Form(request.POST)
            if form.is_valid() and session_aux_form.is_valid():
                del_links, add_links = [], []
                print request.POST
                for key in request.POST:
                    keysp = key.split('_')
                    value = request.POST[key]
                    if keysp[0] == 'add':
                        add_links.append((value, request.POST['title_'+keysp[1]+'_'+keysp[2]]))
                    elif keysp[0] == 'del':
                        del_links.append(value)
                print add_links
                new_session = form.save(session=session, add_links=add_links, del_links=del_links)
                cis.session = new_session
                cis.save()
                return HttpResponseRedirect('/c/edit-session/%s/%s/' % (course_b36, session_id))
        else: 
            form = SessionForm({'title': session.title, 'description':session.description, 'video_url':session.video_url })
            session_aux_form = SessionAuxForm({'session_number':cis.session_number})
        print session.link.all()
        render_dict = { 'course': course, 'session': session, 'form': form, 'session_aux_form':session_aux_form }
        editors = course.editor.all()
        editors = [editor.editor for editor in editors]
        render_dict['editors'] = editors
        return render_to_response('classes/edit.html', render_dict
            , context_instance=RequestContext(request))

def directory(request, categories=None):
    sqs = SearchQuerySet()
    sqs = sqs.models(CourseInfo)

    if categories:
        cat_list = categories.lower().strip('/').split('/')
        category = get_object_or_404(Category, name=cat_list[-1])
        children = category.children.all()
        sqs = sqs.filter(categories=category.name)
        curr_category = category
    else:
        children = Category.objects.filter(parent_category__isnull=True)
        curr_category = None

    sqs = sqs.order_by('-rating')

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    courses_paginator = Paginator(sqs, int(request.GET.get('rpp','25')))
    try:
        courses_page = courses_paginator.page(page)
    except (EmptyPage, InvalidPage):
        courses_page = courses_paginator.page(courses_paginator.num_pages)
    render_dict = {'children': children, 'curr_category':curr_category, 'courses_page': courses_page, 'paginator':courses_paginator, 'mod_path':request.path + '?rpp=25' }
    return render_to_response('classes/directory.html', render_dict
        , context_instance=RequestContext(request))

@login_required
def rate_class(request, course_b36, rating, username=None):
    course_id = base36_to_int(course_b36)
    #if request.user.username == username:
    rate_object, created = CourseInfoRating.objects.get_or_create(course_info=CourseInfo.objects.get(pk=course_id), user=request.user, defaults={'rating':rating})
    if not created:
        rate_object.rating = rating
        rate_object.save()
    return HttpResponse('success')

def view_class(request, course_b36=None, session_uuid=None):
    course_id = base36_to_int(course_b36)
    print session_uuid
    if session_uuid:
        session = get_object_or_404(Session, pk=session_uuid)
        cis = session.course_info_session.all()[0]
        course = cis.course_info
        render_dict = {'session': session, 'cis':cis}
    else:
        course = get_object_or_404(CourseInfo, pk=course_id)
        render_dict = {}
    render_dict['course'] = course
    editors = course.editor.all()
    editors = [editor.editor for editor in editors]
    if request.GET.has_key('a'):
        return render_to_response('classes/small_info.html', render_dict)
    render_dict['editors'] = editors
    user = request.user
    render_dict['iseditor'] = user in editors
    render_dict['user'] = request.user
    #if allowed_to_see(user, class):
    return render_to_response('classes/view.html', render_dict
        , context_instance=RequestContext(request))

        
def ajax_view_session(request, session_uuid):
    session = get_object_or_404(Session, pk=session_uuid)
    cis = session.course_info_session.all()[0]
    course = cis.course_info
    render_dict = {'session': session, 'cis':cis}
    return render_to_response('classes/incl/view_session.html', render_dict
        , context_instance=RequestContext(request))


@login_required
def create_class(request):
    if request.method == 'POST':
        form = MakeCourseForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            prereqs = form.cleaned_data['prerequisites']
            #from_date = form.cleaned_data['from_date']
            #institution = form.cleaned_data['institution']
            url = form.cleaned_data['url']
            #instructors = form.cleaned_data['instructors']
            new_ci = CourseInfo(title=title, description=description, prereqs=prereqs, url=url) 
            new_ci.save()
            ci_admin = CourseInfoEditor(editor=request.user, course_info=new_ci, creator=True)
            ci_admin.save()
            return HttpResponseRedirect('/c/edit/%s/' % (int_to_base36(new_ci.pk)))
    else:
        form = MakeCourseForm()
    #editors = course.editor.all()
    #editors = [editor.editor for editor in editors]
    return render_to_response('classes/edit.html', {'form': form, 'creating': True, }
        , context_instance=RequestContext(request))

from course_miners import youtube_playlist_to_course
@login_required
def create_class_from_playlist(request):
    course_info = youtube_playlist_to_course(request.GET['playlistbox'])
    return HttpResponseRedirect('/h/create/%s/' % (int_to_base36(course_info.pk)))

from course_miners import fetch_youtube_video
from urllib import unquote
from django.core import serializers
from django.utils import simplejson
def fetch_video_info(request):
    video_url = unquote(request.GET['q'])
    print video_url
    data = fetch_youtube_video(video_url)
    return HttpResponse(simplejson.dumps(data), mimetype='application/javascript; charset=utf8')#serializers.serialize('json', data), mimetype='application/json')

def small_info(request):
    reqid = request.GET['q']
    course = get_object_or_404(CourseInfo, pk=reqid)
    if course.published:
        return render_to_response("course/small_info.html", {'course': course})

@login_required
def add_editor(request, course_b36, username=None):
    course_id = base36_to_int(course_b36)
    course = get_object_or_404(CourseInfo, pk=course_id)
    if course.is_editor(request.user):
        contacts = list(request.user.contact.all())
        editors = course.editor.all()
        editors = [editor.editor for editor in editors]
        # slowwwwwwwwwwwwwww ^n
        contacts = filter(lambda x: not x.to_contact in editors, contacts)
        if username and username in [c.username for c in contacts]:
            req_user = get_object_or_404(User, username=username)
            cie, created = CourseInfoEditor.objects.get_or_create(editor=req_user, course_info=course)
            if created:
                cie.save()
        render_dict = { 'course': course, 'editors':editors, 'contacts':contacts, 'add_editoring':True, 'session':True }
        return render_to_response('classes/edit.html', render_dict
        , context_instance=RequestContext(request))
    raise Http404

@login_required
def new_session(request, course_b36):
    course_id = base36_to_int(course_b36)
    from classes.forms import SessionForm
    course = CourseInfo.objects.get(pk=course_id)
    if course.is_editor(request.user):
        if request.method == 'POST':
            form = SessionForm(request.POST)
            session_aux_form = SessionAuxForm(request.POST)
            if form.is_valid() and session_aux_form.is_valid():
                add_links = []
                for key in request.POST:
                    keysp = key.split('_')
                    value = request.POST[key]
                    if keysp[0] == 'add':
                        add_links.append((value, request.POST['title_'+keysp[1]+'_'+keysp[2]]))
                new_session = form.save(session=None, add_links=add_links)
                cis = CourseInfoSession.objects.create(session=new_session, course_info=course, session_number=form.cleaned_data['session_number'])
                cis.save()
                return HttpResponseRedirect('/c/edit-session/%s/%s/' % (course_b36, cis.pk))
        else:
            form = SessionForm()
            session_aux_form = SessionAuxForm({'session_number': len(course.course_info_session.all())+1})
        render_dict = { 'course': course, 'form': form, 'session':True, 'session_aux_form':session_aux_form }
        editors = course.editor.all()
        editors = [editor.editor for editor in editors]
        render_dict['editors'] = editors
        return render_to_response('classes/edit.html', render_dict
            , context_instance=RequestContext(request))
