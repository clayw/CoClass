from django import forms
from django.contrib.auth import authenticate
import settings
import captcha

class SignUpForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(render_value=False))


class LostPassForm(forms.Form):
    email = forms.EmailField()
        
class SignInForm(forms.Form):
    username = forms.EmailField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), max_length=20)
    remember = forms.BooleanField(required=False)

    def clean(self):
        data = self.cleaned_data
        username = data['username']
        data['email']
        email = data['email']
        password = data['password']
        user = authenticate(username=username, password=password) 
        if user is None:
            raise forms.ValidationError("Wrong username/password")
        elif not user.is_active:
            raise forms.ValidationError("User inactive")
        data['user'] = user
        return data
    
class ProfileForm(forms.Form):
    interests = forms.CharField(widget=forms.Textarea, max_length=2000, required=False)
    background = forms.CharField(widget=forms.Textarea, max_length=400, required=False)

class PreferencesForm(forms.Form):
    first_name = forms.CharField(max_length=25)
    last_name = forms.CharField(max_length=25)
    email = forms.EmailField()
    old_password = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False)
    new_password = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(render_value=False), required=False)

    def clean(self):
        try:
            confirm_new_password, new_password = self.cleaned_data['confirm_new_password'], self.cleaned_data['new_password']
            if confirm_new_password != new_password:
                raise Exception
        except KeyError:
            pass

class VenueForm(forms.Form):
    name = forms.CharField(max_length=200) 
    addr = forms.CharField(max_length=300)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=2)
    zip = forms.CharField(max_length=5)
    apt = forms.CharField(max_length=20, required=False)

    def save(self, request):
        from places.models import Place, PlacePic, place_pic_uploader
        cleaned_data = self.cleaned_data
        name = cleaned_data['name']
        street = cleaned_data['addr']
        city = cleaned_data['city']
        state = cleaned_data['state']
        zip = cleaned_data['zip']
        apt = cleaned_data['apt']
        location = "%s %s, %s %s" % (street, city, state, zip)
        from geopy import geocoders
        geocoder = geocoders.Google('ABQIAAAA4HDqD8t_GwFAvzzFapPlGRQ_R5Qiphk1phJft3u3QNxBad8fLRRA-q4ZSxjFfS9SK2wsDFMnz3jl7g')
        geocoding_results = None
        geocoding_results = list(geocoder.geocode(location, exactly_one=False))
        if geocoding_results:
            place, (latitude, longitude) = geocoding_results[0]
        try:
            if post_data['email']:
                username, password = create_account_from_email(post_data['email'])
                user = authenticate(username=username, password=password) 
                login(request, user)
        except:
            pass
        place = Place(user=request.user, name=name, street=street, city=city, \
             state=state, zip=zip, apt=apt, latitude=latitude, longitude=longitude)
        place.save()
        place_pic_uploader(place, request.FILES)
        return place
from models import Expert
class ExpertForm(forms.ModelForm):
    class Meta:
        model = Expert
        exclude = ('user', 'place', 'privacy', 'date_created', 'date_modified', )

#class ExpertkkForm(forms.Form):
#    bio = forms.CharField(required=False, widget=forms.Textarea)
#    skills = forms.CharField(required=False, widget=forms.Textarea)
#    availability = forms.CharField(max_length=100, required=False)
#    price = forms.FloatField(required=False)
#    linkedin_url = forms.URLField(required=False)
#    active = forms.BooleanField()

