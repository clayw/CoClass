import os
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template
import settings
#from settings import MEDIA_ROOT
#from settings import DEBUG

admin.autodiscover()

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

urlpatterns = patterns('',
  (r'^admin/(.*)', admin.site.root),
  #(r'^user/(?P<user_id>\d+)/$', 'accounts.views.profile'),
  (r'^users/(?P<username>[a-zA-Z0-9]+)/$', 'accounts.views.profile'),
  (r'^users/(?P<username>[a-zA-Z0-9]+)/classes', 'accounts.views.profile_classes'),
  #(r'^user/(?P<user_id>\d+)/classes/$', 'accounts.views.profile_classes'),
  url(r'^users/(?P<username>[a-zA-Z0-9]+)/expert/$', 'accounts.views.expert_profile', name='expert-profile'),
  url(r'^users/(?P<username>[a-zA-Z0-9]+)/hire/$', 'accounts.views.expert_hire', name='expert-hire'),
  url(r'^users/(?P<username>[a-zA-Z0-9]+)/add/$', 'accounts.views.add_contact', name='add-contact'),
  (r'^place/edit/$', 'places.views.edit_place'),
  (r'^$', 'CoClass.index.views.index'),
  # includes
  (r'^s/', include('search.urls')),
  (r'^c/', include('classes.urls')),
  (r'^h/', include('host.urls')),
  (r'^accounts/', include('accounts.urls')),
  (r'^accounts/auth/', include('socialauth.urls')),
  (r'^about/', include('about.urls')),
  (r'^req/', include('invite.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
      (r'^robots.txt$', 'django.views.generic.simple.direct_to_template', {'template': 'robots.txt'}),
      (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
      (r'^favicon.png$', 'django.views.static.serve', {'document_root': SITE_ROOT + '/template/', 'path': 'favicon.png'}),
    )
