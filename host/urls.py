from django.conf.urls.defaults import *
urlpatterns = patterns('host.views',
  url(r'^search/$', 'host_search', name="host-search"),
  url(r'^create/(?P<course_b36>[0-9a-zA-Z\-]+)/$', 'host_create', name="host-create"),
  url(r'^invite/(?P<host_b36>[a-zA-Z0-9]+)/$', 'invite', name="host-invite"),
  url(r'^members/(?P<host_b36>[a-zA-Z0-9]+)/$', 'members', name="host-members"),
  #url(r'^members/(?P<host_b36>[a-zA-Z0-9]+)/$', 'members', name="host-members"),
  url(r'^meetings/(?P<host_b36>[a-zA-Z0-9]+)/$', 'edit_calendar', name="host-meetings"),
  url(r'^chx/(?P<host_b36>[a-zA-Z0-9]+)/(?P<change>(remove|add))/(?P<status>(admin|expert))/(?P<username>[a-zA-Z0-9]+)/$', 'change_status', name="host-change-status"),

  url(r'^comment/delete/(?P<comment_id>[a-zA-Z\-0-9]+)/$', 'delete_comment', name="delete-comment"),
  url(r'fork/(?P<host_b36>[a-zA-Z0-9]+)/$', 'fork_class', name='fork_class'),

#  url(r'^signup/(?P<host_b36>[a-zA-Z0-9]+)/$', 'signup', name="host-signup"),
  url(r'^e/(?P<host_b36>[a-zA-Z0-9]+)/$', 'edit_class', name="edit-host-class"),
  (r'^sf/$', 'ajax_search_form'),

  url(r'^v/(?P<host_b36>[a-zA-Z0-9]+)/', 'host_class', name="host-class"),
  url(r'^view/(?P<host_b36>[a-zA-Z0-9]+)/', 'host_class', name="host-class"),
  url(r'^p/(?P<host_b36>[a-zA-Z0-9]+)/$', 'ajax_place', name="ajax-place"),
  url(r'^s/(?P<host_b36>[a-zA-Z0-9]+)/$', 'ajax_sessions', name="ajax-session"),
  #url(r'^s/(?P<host_b36>[a-zA-Z0-9]+)/(?P<session_id>\d+)/$', 'ajax_sessions', name="ajax-session-num"),
  url(r'^s/(?P<host_b36>[a-zA-Z0-9]+)/(?P<session_pk>[a-zA-Z\-0-9]+)$', 'ajax_sessions', name="ajax-session-pk"),

  url(r'^se/(?P<host_b36>[a-zA-Z0-9]+)/$', 'ajax_session_edit', name="ajax-session-new"),
  url(r'^se/(?P<host_b36>[a-zA-Z0-9]+)/(?P<session_id>[a-zA-Z\-0-9]+)/$', 'ajax_session_edit', name="ajax-session-edit"),

  url(r'^se_post/(?P<host_b36>[a-zA-Z0-9]+)/$', 'ajax_session_post', name="ajax-session-new-post"),
  url(r'^se_post/(?P<host_b36>[a-zA-Z0-9]+)/(?P<session_id>[a-zA-Z\-0-9]+)/$', 'ajax_session_post', name="ajax-session-edit-post"),
  url(r'^se_del/(?P<host_b36>[a-zA-Z0-9]+)/(?P<session_id>[a-zA-Z\-0-9]+)/$', 'ajax_session_delete', name="ajax-session-delete"),
  url(r'^se_propagate/(?P<host_b36>[a-zA-Z0-9]+)/(?P<session_id>[a-zA-Z\-0-9]+)/$', 'ajax_session_propagate', name="ajax-session-propagate"),

  url(r'^c/(?P<host_b36>[a-zA-Z0-9]+)/$', 'ajax_calendar', name="ajax-calendar"),
)

urlpatterns += patterns('',
  url(r'^signup/(?P<host_b36>[a-zA-Z0-9]+)/$', 'host.views.signup', name="host-signup"),
)
