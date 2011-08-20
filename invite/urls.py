
from django.conf.urls.defaults import *
urlpatterns = patterns('invite.views',
  (r'^(?P<func>(hire|signup|invite))/(?P<host_b36>[a-z0-9]+)/(?P<to_user>[a-zA-Z0-9]+)/(?P<from_user>[a-zA-Z0-9]+)/', 'req_base'),
)
