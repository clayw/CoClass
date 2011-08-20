from django import forms
from django.contrib.auth import authenticate

from places.models import Place, PlacePic, place_pic_uploader

class PlaceForm(forms.Form):
    name = forms.CharField(max_length=200) 
    addr = forms.CharField(max_length=300)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=2)
    zip = forms.CharField(max_length=5)
    apt = forms.CharField(max_length=20, required=False)

    def save(self, request, place=None):
        cleaned_data = self.cleaned_data
        name = cleaned_data['name']
        street = cleaned_data['addr']
        city = cleaned_data['city']
        state = cleaned_data['state']
        zip = cleaned_data['zip']
        apt = cleaned_data['apt']
        location = "%s %s, %s %s" % (street, city, state, zip)
        from geopy import geocoders
        try:
            geocoder = geocoders.Google('ABQIAAAA4HDqD8t_GwFAvzzFapPlGRQ_R5Qiphk1phJft3u3QNxBad8fLRRA-q4ZSxjFfS9SK2wsDFMnz3jl7g')
            geocoding_results = None
            geocoding_results = list(geocoder.geocode(location, exactly_one=False))
        except:
            # no internet??
            # log failure for db update
            latitude = longitude = -1
        if geocoding_results:
            address, (latitude, longitude) = geocoding_results[0]
        try:
            if post_data['email']:
                username, password = create_account_from_email(post_data['email'])
                user = authenticate(username=username, password=password) 
                login(request, user)
        except:
            pass
        if place: #request.REQUEST['place'] == '-1':
            print 'place', place
            place.name = name
            place.zip = zip
            place.apt = apt
            place.street = street
            place.city = city
            place.latitude = latitude
            place.longitude = longitude
            # delete pics ? 
        else:
            place = Place(user=request.user, name=name, street=street, city=city, \
                 state=state, zip=zip, apt=apt, latitude=latitude, longitude=longitude)
        place.save()
        place_pic_uploader(place, request.FILES)
        return place
