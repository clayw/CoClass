from django.shortcuts import render_to_response
from django.http import Http404#ResponseNotFound
from django.template import RequestContext, TemplateDoesNotExist

def generic(request, page):
    page = page.lower()
    try:
        return render_to_response('about/%s.html' % page, {}, context_instance=RequestContext(request))
    except TemplateDoesNotExist:
        raise Http404
