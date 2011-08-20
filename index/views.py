from django.shortcuts import render_to_response
from django.template import RequestContext
from classes.models import CourseInfo

def index(request):
    try:
        featured_class = CourseInfo.objects.get(pk=12)
    except:
        featured_class = None
    return render_to_response('index.html', {'featured_class': featured_class}, context_instance=RequestContext(request))

