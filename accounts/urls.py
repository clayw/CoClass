from django.conf.urls.defaults import *

urlpatterns = patterns('accounts.views',
  (r'^profile/$', 'edit_profile'),
  (r'^edit/$', 'edit_profile'),
  (r'^preferences/$', 'preferences'),
  (r'^place/$', 'place'),
  (r'^classes/$', 'classes'),

  (r'^expert/$', 'expert_settings'),
  (r'^expert-agreement/$', 'expert_agreement'),
  (r'^new_place/$', 'edit_place'),
  (r'^edit_place/(?P<place_id>\d+)/$', 'edit_place'),

  url(r'^signup/', 'signup', name='signup'),
  url(r'^contacts/', 'contact_list', name='contact_list'),

  # messages 
  url(r'^$', 'main', name='messages_inbox'),
  (r'^reply/$', 'reply'),
  url(r'^logout/', 'logout', name='logout'),
)
urlpatterns += patterns('',

  (r'^lostpass/$', 'django.contrib.auth.views.password_reset', {'template_name':'accounts/password_reset_form.html', 'email_template_name':'email/reset_pass.html'}),
  (r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done'), #, {'template_name':'accounts/password_reset_done.html'}),
  (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name':'accounts/password_reset_confirm.html'}),
  (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'), #, {'template_name':'accounts/password_reset_complete.html'}),

  url(r'^signin/', 'django.contrib.auth.views.login', {'template_name': 'accounts/signin.html'}, name='login'),
  url(r'^login/', 'django.contrib.auth.views.login', {'template_name': 'accounts/signin.html'}, name='login-r'),
  url(r'^reply/(?P<message_id>[\d]+)/$', 'django_messages.views.reply', {'template_name': 'accounts/compose.html'}, name='messages_reply'),
  url(r'^compose/(?P<recipient>\w+)/$', 'django_messages.views.compose', {'template_name': 'accounts/compose.html'}, name='send-message'),
  url(r'^messages/(?P<message_id>[\d]+)/$', 'django_messages.views.view', {'template_name': 'accounts/view.html'}, name='messages_detail'),
  (r'^messages/delete/(?P<message_id>[\d]+)/$', 'django_messages.views.delete'),
)
