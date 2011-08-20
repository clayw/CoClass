from django.shortcuts import render_to_response
import datetime
from django.template import RequestContext
from haystack.query import SearchQuerySet
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from accounts.models import Expert
from geopy import geocoders
import geopy.distance
from django.db import models
from host.models import HostClass
from classes.models import CourseInfo
from django.db.models import Q
from places.models import Place
from settings import GOOGLE_API_KEY

def search_main(request):
    get_data = request.GET
    num_per_page = 10
    tab = get_data.get('tab','meetings')
    what = get_data.get('what', '')
    where = get_data.get('addr', '')
    startdate = get_data.get('startdate','')
    results_per_page = int(get_data.get('n', '10'))
    radius = int(get_data.get('radius', '30'))
    sqs = SearchQuerySet()
    try:
        hc_id = get_data['hc']
        host_class = HostClass.objects.get(pk=hc_id)
        if host_class.privacy == 'a' or  host_class.is_member(request.user):
            where = host_class.place.get_full_address()
    except:
        pass

    if what in ['What?', ''] or tab in ['meetings']:
        what = 'What?'
    else:
        sqs = sqs.auto_query(what)
    lat = None
    long = None
    if where in ['Where?', ''] or tab in ['classes']:
        where = 'Where?'
    else:
        geocoder = geocoders.Google(GOOGLE_API_KEY)
        geocoding_results = None
        geocoding_results = list(geocoder.geocode(where, exactly_one=False))
        if geocoding_results:
            place, (latitude, longitude) = geocoding_results[0]
            lat = float(latitude)
            long = float(longitude)
            sqs = sqs.spatial(lat=lat, long=long, radius=radius)

    if tab == 'meetings': 
        sqs = sqs.models(HostClass)
        if startdate and startdate != 'mm/dd/yyyy':
            mm, dd, yyyy = startdate.split('/')
            from datetime import date
            try:
                sqs = sqs.filter(start_date__gte=date(yyyy, mm, dd))
            except:
                pass
    elif tab == 'experts': 
        sqs = sqs.models(Expert)
    elif tab == 'classes': 
        sqs = sqs.models(CourseInfo).order_by('-rating')
    try:
        page = int(get_data.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(sqs, results_per_page)

    try:
        search_results = paginator.page(page)
    except (EmptyPage, InvalidPage):
        search_results = paginator.page(paginator.num_pages)
    i = 0
    for result in search_results.object_list:
        result.letter = chr(65+i)
        i += 1
    url_params = notab_params = ''
    starter = '?'
    save_params = [('what', 'What?'), 
            ('addr', 'Where?'), 
            ('tab', 'meetings'), 
            ('startdate', 'mm/dd/yyyy')]
    for (param, default) in save_params:
        add_params = '%c%s=%s' % (starter, param, request.GET.get(param, default))
        if param != 'tab':
            notab_params += add_params
        url_params += add_params
        starter = '&'
    mod_path = request.path + url_params
    tab_path = request.path + notab_params
    dict = { 
            'paginator': paginator,
            'search_results': search_results,
            'addr': where,
            'what': what,
            'mod_path': mod_path, 
            'tab_path': tab_path, 
            'tab': tab, 
            'startdate': startdate, 
            'results_per_page': results_per_page,
            'sqs': sqs,
            'gcode_lat': lat,
            'gcode_lng': long,
           }
    url = 'search/' + {'meetings': 'meetings.html', 'experts': 'experts.html', 'classes': 'classes.html'}[tab]
    return render_to_response(url, dict, context_instance=RequestContext(request))

def course_list(request):
    query = request.GET.get('q', '')
    results = SearchQuerySet().models(CourseInfo).auto_query(query)
    return render_to_response("search/course_list.html", {'results': results})

