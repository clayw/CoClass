from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from auxiliary import generic_handle_pic
from logicaldelete.models import LogicalDeleteModel, UUIDModel, LocationSearchModel

import geopy.distance
from geopy import geocoders
def place_pic_uploader(place, files_data):
    if files_data:
        for file in files_data:
            pp = PlacePic(place=place)
            image_data=files_data[file]
            filename, ctx = generic_handle_pic(image_data)
            pp.pic.save(filename, ctx)
            pp.save()

class Place(LocationSearchModel):

    user = models.ForeignKey(User, related_name='place')
    name = models.CharField(max_length=200) 
    #country = models.CharField(max_length=200) # change to select field
    street = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=5)
    apt = models.CharField(max_length=20)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    details = models.TextField()

    def save(self):
        if not (self.latitude and self.longitude):
            #geocoder = geocoders.GeocoderDotUS()
                
            geocoder = geocoders.Google(GOOGLE_API_KEY)
            geocoding_results = None

            if self.street:
                # try the full address
                query = '%(street)s, %(city)s, %(state)s %(zip)s' % self.__dict__
                geocoding_results = list(geocoder.geocode(query, exactly_one=False))

            # then just city/state/zip
            if not geocoding_results and self.city:
                query = '%(city)s, %(state)s %(zip)s' % self.__dict__
                geocoding_results = list(geocoder.geocode(query, exactly_one=False))

            # and finally just zip
            if not geocoding_results and self.zip:
                query = '%(zip)s' % self.__dict__
                geocoding_results = list(geocoder.geocode(query, exactly_one=False))

            if geocoding_results:
                place, (latitude, longitude) = geocoding_results[0]
                self.latitude = latitude
                self.longitude = longitude
        super(Place, self).save()

    def get_full_address(self):
        """ returns a human readable address """
        return self.street + ', ' + self.city + ', ' + self.state + ' ' + self.zip

    def display_address(self):
        # prune street number from address
        import re
        m = re.search('^\d+ (.*)', self.street)
        try:
            return m.group(1) + ', ' + self.city
        except:
            return self.city 

class PlacePic(models.Model):
    place = models.ForeignKey(Place, related_name='pic')
    pic = models.ImageField(upload_to='p/')

