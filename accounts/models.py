from django.db import models
from django.contrib.auth.models import User
from django_messages.models import Message

from django.db import models
from django.db.models import signals
from CoClass.logicaldelete.models import LocationSearchModel
from CoClass.logicaldelete.models import LogicalDeleteModel

import CoClass.settings
from django.core.mail import send_mail

from django_extensions.db import fields
from django.template import loader, Context

## Helper functions up here, models below
def create_account_from_email(email):
    """ 
    Creates an account for people that only enter email
    it generates a password and waits for first and last name later 
    Accounts remain limited from doing stuff until it has first and last name
    """
    passwd = User.objects.make_random_password(length=8)
    return create_account('', '', email, passwd), passwd

def create_account(first_name, last_name, username, email, password):
    import re
    username_re = re.compile('^[a-zA-Z][a-zA-Z0-9]+')
    if username_re.match(username):
        user = User.objects.create_user(username, email, password)
        if first_name:
            new_first = first_name[0].upper() + first_name[1:]
            user.first_name = new_first
        if last_name:
            new_last = last_name[0].upper()
            new_last = last_name[0].upper() + last_name[1:]
            user.last_name = new_last
        user.save()

        user_profile = UserProfile(user=user)
        user_profile.save()

        template = loader.get_template('email/registration.txt')
        context = Context({'user': user, })
        render = template.render(context)
        send_mail('Welcome to CoClass', render, 'clay@coclass.com', [user.email], fail_silently=False)

        return user
    else:
        raise Exception('Invalid username')

def reset_pass(email):
    user = User.objects.get(email=email)
    passwd = User.objects.make_random_password(length=8)
    user.set_password(passwd)
    template = loader.get_template('email/resetpass.txt')
    context = Context({'user': user, 'passwd': passwd })
    send_mail('CoClass.com: Password reset', template.render(context), 'clay@coclass.com', [user.email], fail_silently=False)

## Models below
class UserProfile(LogicalDeleteModel):
    user = models.ForeignKey(User, related_name='profile', unique=True)
    background = models.TextField()
    interests = models.TextField()
    user_pic = models.ImageField(upload_to='p/', default='p/questionmark.jpg')

    def __unicode__(self):  
        return self.user.id

    def get_absolute_url(self):
        return '/user/%d/' % (self.user.id)

    def get_expert(self):
        try:
            return self.expert.all()[0]
        except:
            return None

class Expert(LocationSearchModel):
    place = models.ForeignKey('places.Place', null=True)

    user = models.ForeignKey(User, related_name='expert', unique=True)
    bio = models.TextField(null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    availability = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(null=True, blank=True, max_length=6)
    homepage_url = models.URLField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    active = models.BooleanField(default=False)

from CoClass.invite.models import Request
class ExpertInvite(Request):
    pass
class ExpertSignup(Request):
    pass

class Contact(models.Model):
    """ this creates a unidirectional friend system """
    from_contact = models.ForeignKey(User, related_name='contact')
    to_contact = models.ForeignKey(User, related_name='contact_of')
    #to_from_contact = models.CharField(primary_key=True, max_length=61)

    class Meta:
        unique_together = (('from_contact', 'to_contact'),)

