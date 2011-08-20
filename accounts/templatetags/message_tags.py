from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.filter
def request_from_message(message):
    url = ''
    try:
        if message.subject.startswith('I would like to hire you as an expert'):
            req = message.req_expertsignup.all()[0]
            url = '/req/hire/'
        elif message.subject.startswith('Request to take'):
            req = message.req_hostclassinvite.all()[0]
            url = '/req/invite/'
        elif message.subject.startswith('Request to join'):
            req = message.req_hostclasssignup.all()[0]
            url = '/req/signup/'
        else:
            return ''
    except:
        return ''
    if req.acceptance:
        result = 'ACCEPTED'
    else:
        hc, to_user, from_user = req.host_class_to_from.split(',')
        url += '/'.join([hc, to_user, from_user])
        result = '<a href="%s">ACCEPT</a>' % (url,)
    return mark_safe(result)

        

    


