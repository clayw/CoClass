from django.db import models
from django_extensions.db import fields as ext_fields
from django.contrib.auth.models import User
from django_messages.models import Message
from host.models import HostClass
from django.utils.translation import ugettext_lazy as _

import re
import random
import datetime


SHA1_RE = re.compile('^[a-f0-9]{40}$')

def create_pseudouser_or_get_user(email):
    """ If the user email exists in database, just send an invite to the email
        otherwise make pseudouser and send join request
    """
    user = User.objects.get(email=email)
    if user:
        return user
    else:
        return create_user(username=email, email=email)

class PseudoManager(models.Manager):
    def create(self, email):
        import hashlib
        ctr = 0
        while ctr < 5:
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            activation_key = hashlib.sha1(salt+email).hexdigest()
            #try:
            return PseudoUser(email=email,
                                   activation_key=activation_key,
                                   expiration_date = datetime.datetime.now() + datetime.timedelta(7))
            #except:
                #pass
            ctr += 1  # this should never happen
        raise Exception('serious problem: failed to generate unique key after 5 tries')

    def delete_expired_users(self):
        for profile in self.all():
            if profile.expiration_date > datetime.datetime.now():
                profile.delete()

class PseudoUser(models.Model):
    #user = models.ForeignKey(User, primary_key=True)
    objects = PseudoManager()

    email = models.EmailField()
    activation_key = models.CharField(_('activation key'), max_length=40, primary_key=True)
    expiration_date = models.DateField()
    #request = models.ForeignKey('invite.Request', null=True)
    host_class_to = models.CharField(max_length=120) # request

class RequestManager(models.Manager):
    def create(self, host_class, sender, recipient, subject, body):
        from auxiliary import int_to_base36
        print 'creating ', host_class, sender, recipient, subject, body
        host_class_to_from = ','.join([int_to_base36(host_class.pk), sender.username, recipient.username])
        m, c = self.get_or_create(host_class_to_from=host_class_to_from)
        if c:
            message = Message(sender=sender,recipient=recipient,subject=subject,body=body)
            message.save()
            m.message=message
            m.save()
            print 'created', m
        return m

class Request(models.Model):
    requests = RequestManager()

    host_class_to_from = models.CharField(max_length=120, primary_key=True) # separated by comma
    #uuid = ext_fields.UUIDField(primary_key=True)
    #host_class = models.ForeignKey(HostClass, null=True)
    #message object has all the info I want, date, sender recipient, etc
    message = models.ForeignKey(Message, related_name='req_%(class)s', null=True, unique=True)
    acceptance = models.BooleanField(default=False)
    
    class Meta:
        abstract = True
        #unique_together = (('host_class','sender','recipient'),)

