from datetime import datetime
from django.db import models
from django_extensions.db import fields


class LogicalDeleteManager(models.Manager):
    def get_query_set(self):
        if self.model:
            return super(LogicalDeleteManager, self).get_query_set().filter(date_removed__isnull=True)

    def everything(self):
        if self.model:
            return super(LogicalDeleteManager, self).get_query_set()

    def only_deleted(self):
        if self.model:
            return super(LogicalDeleteManager, self).get_query_set().filter(date_removed__isnull=False)

    def get(self, *args, **kwargs):
        ''' if a specific record was requested, return it even if it's deleted '''
        return self.everything().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        ''' if pk was specified as a kwarg, return even if it's deleted '''
        if 'pk' in kwargs:
            return self.everything().filter(*args, **kwargs)
        return self.get_query_set().filter(*args, **kwargs)


class LogicalDeleteModel(models.Model):
    date_created  = models.DateTimeField(default=datetime.now)
    date_modified = models.DateTimeField(default=datetime.now)
    date_removed  = models.DateTimeField(null=True, blank=True)

    objects    = LogicalDeleteManager()
    deleted    = LogicalDeleteManager().only_deleted()
    everything = LogicalDeleteManager().everything()
    
    def active(self):
        return self.date_removed == None
    active.boolean = True

    def delete(self):
        self.date_removed = datetime.now()
        self.save()

    class Meta:
        abstract = True

from geopy import geocoders
import geopy.distance
from settings import GOOGLE_API_KEY
class LocationSearchManager(LogicalDeleteManager):
    def search(self, get):
        location = get.get('addr', '')
        what = get.get('what', '')

        try:
            distance = int(get['distance'])
        except:
            distance = 100

        if not (location and distance):
            return []

        queryset = super(LocationSearchManager, self).get_query_set()
        geocoder = geocoders.Google(GOOGLE_API_KEY)
        geocoding_results = None
        geocoding_results = list(geocoder.geocode(location, exactly_one=False))
        if geocoding_results:
            place, (latitude, longitude) = geocoding_results[0]
        else: 
            return []

        counter = 0
        objs = []
        for obj in queryset:
            location = obj.place
            if location.latitude and location.longitude:
                exact_distance = geopy.distance.distance((latitude, longitude), (location.latitude, location.longitude))
                if exact_distance.miles <= distance and obj.is_searchable():
                    obj.letter = chr(65 + counter)
                    objs.append(obj)
                    counter += 1

        return objs

PRIVACY_CHOICES = ( ('a', 'Total access'), ('b', 'Not searchable'), ('c', 'Restricted to select group') )
class LocationSearchModel(LogicalDeleteModel):
    objects = LocationSearchManager()

    privacy = models.CharField(max_length=1, choices=PRIVACY_CHOICES)

    def is_searchable(self):
        return self.privacy == 'a'

    class Meta:
        abstract = True

class UUIDModel(LogicalDeleteModel):
    uuid = fields.UUIDField(primary_key=True)

    class Meta:
        abstract = True
