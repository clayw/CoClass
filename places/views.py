from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from forms import PlaceForm
from django.shortcuts import render_to_response, redirect, HttpResponseRedirect
from django.template import RequestContext

@login_required
def edit_place(request):
    user = request.user
    place_id = request.REQUEST['place']
    if place_id != '-1':
        try:
            place = user.place.get(pk=place_id)
        except:
            # user does not own place
            raise Http404
    else:
        place = None


    if request.method == 'POST':
        form = PlaceForm(request.POST) 
        if form.is_valid():
            print 'form is valid', place
            form.save(request, place) 
            print 'form saved'
            return HttpResponseRedirect('/accounts/place/') # Redirect after POST
        print form.errors
    else:
        if place:
            form = PlaceForm({'name': place.name, 'addr':place.street,
                'zip':place.zip, 'apt':place.apt, 'city': place.city,  'state':place.state })
        else:
            form = PlaceForm()
    return render_to_response('places/edit_place.html', {
        'place_form': form, 'place': place
    }, context_instance=RequestContext(request))
    
