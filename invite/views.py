from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from host.models import HostClassInvite
from host.models import HostClassSignup
from host.models import HostClassMember
from host.models import HostClass
from accounts.models import ExpertSignup
from django.contrib.auth.models import User
from auxiliary import base36_to_int

def req_base(request, func, host_b36, to_user, from_user):

    if from_user == request.user.username:
        hctf = ','.join([host_b36, to_user, from_user])
        if func == 'hire':
            req = get_object_or_404(ExpertSignup, pk=hctf)
            host_class=HostClass.objects.get(pk=base36_to_int(host_b36))
            hcm, c = HostClassMember.objects.get_or_create(user=request.user, host_class=host_class)
            hcm.expert = True
            hcm.save()
        elif func == 'invite':
            req = get_object_or_404(HostClassInvite, pk=hctf)
            host_class=HostClass.objects.get(pk=base36_to_int(host_b36))
            hcm, created = HostClassMember.objects.get_or_create(user=request.user, host_class=host_class)

        elif func == 'signup':
            req = get_object_or_404(HostClassSignup, pk=hctf)
            print 'signing up', req
            host_class=HostClass.objects.get(pk=base36_to_int(host_b36))
            hcm, created = HostClassMember.objects.get_or_create(user=User.objects.get(username=to_user), host_class=host_class)
            print 'signed up', hcm, created

        req.acceptance = True
        req.save()
        return HttpResponseRedirect('/h/v/%s/' % (host_b36))
    raise Http404

