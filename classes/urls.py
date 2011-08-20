from django.conf.urls.defaults import *

urlpatterns = patterns('classes.views',
  (r'^new/', 'create_class'),
  (r'^playlist', 'create_class_from_playlist'),
  (r'^rate/(?P<course_b36>[a-z0-9]+)/(?P<rating>\d+)/', 'rate_class'),
  (r'^rate/(?P<course_b36>[a-z0-9]+)/(?P<rating>\d+)/(?P<username>[a-zA-Z0-9]+)/', 'rate_class'),
  url(r'^v/(?P<course_b36>[a-z0-9]+)/(?P<session_uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/', 'view_class', name='view-session'),
  (r'^v/(?P<course_b36>[a-z0-9]+)/(.*)/(?P<session_uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})/', 'view_class'),
  (r'^v/(?P<course_b36>[a-z0-9]+)/', 'view_class'),
  (r'^s/(?P<session_uuid>[A-Z0-9\-a-z]+)/', 'ajax_view_session'),
  url(r'edit/(?P<course_b36>[a-z0-9]+)/', 'edit_class', name='edit-class'),
  url(r'edit-session/(?P<course_b36>[a-z0-9]+)/(?P<session_id>[a-zA-Z0-9\-]+)/', 'edit_session', name='edit-session'),
  (r'^i/', 'small_info'), # this is a lookup command
  (r'^vi/', 'fetch_video_info'), # this is a lookup command
  (r'^add_editor/(?P<course_b36>[a-z0-9]+)/$', 'add_editor'),
  (r'^add_editor/(?P<course_b36>[a-z0-9]+)/(?P<username>[a-zA-Z0-9]+)/$', 'add_editor'),
  (r'^new_session/(?P<course_b36>[a-z0-9]+)/$', 'new_session'),
  url(r'^directory/$', 'directory', name='main-directory'),
  url(r'^directory/(.*)', 'directory', name='directory'),
)
