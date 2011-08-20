from django.conf.urls.defaults import *

urlpatterns = patterns('search.views',
  (r'^$', 'search_main'),
  (r'^d/', 'course_list'),
)
