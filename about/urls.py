from django.conf.urls.defaults import *

urlpatterns = patterns('django.views.generic.simple',
  ('^blog/$', 'redirect_to', {'url': 'http://coclass.posterous.com/'}),
)
urlpatterns += patterns('about.views',
  (r'^$', 'generic', {'page': 'main'}),
  (r'^(.*)/$', 'generic'),
)
