from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
import geopy.distance

from django_extensions.db import fields
from CoClass.places.models import Place
from CoClass.logicaldelete.models import LocationSearchModel, LogicalDeleteModel, UUIDModel
from auxiliary import int_to_base36

def send_invite_letters(to_users, from_user, host_class, body):
    subject = 'Request to take ' + host_class.course.title
    for to_user in to_users:
        hci = HostClassInvite.objects.create(host_class=host_class, sender=from_user, recipient=to_user, subject=subject, body=body)
    # send mail message


class HostClass(LocationSearchModel):
    created = models.BooleanField()

    course = models.ForeignKey('classes.CourseInfo')
    place = models.ForeignKey(Place)


    # times and dates
    meeting_time = models.TimeField()
    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()
    created_date = models.DateTimeField(auto_now_add=True)
    disp_start_date = models.DateField()

    def get_absolute_url(self):
        return "/h/v/%s/" % (int_to_base36(self.id))
    def b36(self):
        return int_to_base36(self.id)

    def is_member(self, user):
        if self.members.filter(user__exact=user.id):
            return True
        else:
            return False

    def is_admin(self, user):
        try:
            return self.members.filter(user__exact=user.id)[0].editor
        except:
            pass
        return False

    def get_session_by_number(self, number):
        try:
            return self.dates.order_by('date')[number]
        except:
            return []

    def first_session(self):
        try:
            return self.dates.order_by('date')[0]
        except:
            return None
    
    def next_session(self):
        import datetime
        try:
            return self.dates.filter(date__gte=datetime.datetime.now()).order_by('date')[0]
        except Exception:
            return []

    def last_session(self):
        try:
            return self.dates.order_by('-date')[0]
        except:
            return None

    def next_available_date(self):
        try:
            last_date = self.last_session().date
        except:
            last_date = self.disp_start_date
	from datetime import timedelta
	delta_one = timedelta(1)
        print delta_one
        last_date += delta_one

        days_of_week = []
        if self.monday: days_of_week.append(1)
        if self.tuesday: days_of_week.append(2)
        if self.wednesday: days_of_week.append(3)
        if self.thursday: days_of_week.append(4)
        if self.friday: days_of_week.append(5)
        if self.saturday: days_of_week.append(6)
        if self.sunday: days_of_week.append(7)

        # safety check
        if len(days_of_week) == 0:
            return last_date
        while not (last_date.isoweekday() in days_of_week):
            last_date += delta_one
        return last_date
    def render_progress(self):
        import datetime
        curr = datetime.datetime.now()
        meetings = self.dates.filter(date__gte=curr)
        if meetings:
            progress = 1 - (float(len(meetings)) / len(self.dates.all()))
            return progress * 100
        else: 
            return 100


    def render_days_all(self):
        return self.render_days(True)
    def render_days(self, all=False):
        ret_sm = []
        ret_big = []
        ret_med = []
        if self.sunday:
            ret_sm.append('Su')
            ret_med.append('Sun')
            ret_big.append('Sunday')
        if self.monday:
            ret_sm.append('M')
            ret_med.append('Mon')
            ret_big.append('Monday')
        if self.tuesday:
            ret_sm.append('Tu')
            ret_med.append('Tues')
            ret_big.append('Tuesday')
        if self.wednesday:
            ret_sm.append('We')
            ret_med.append('Wed')
            ret_big.append('Wednesday')
        if self.thursday:
            ret_sm.append('Th')
            ret_med.append('Thur')
            ret_big.append('Thursday')
        if self.friday:
            ret_sm.append('Fr')
            ret_med.append('Fri')
            ret_big.append('Friday')
        if self.saturday:
            ret_sm.append('Sa')
            ret_med.append('Sat')
            ret_big.append('Saturday')
        from django.utils.safestring import mark_safe
        if all:
            return mark_safe(', '.join(ret_big))
        if len(ret_sm) < 3:
            return mark_safe(' and '.join(ret_med))
        elif len(ret_sm) == 3:
            return mark_safe(', '.join(ret_med))
        elif len(ret_sm) == 4:
            return mark_safe(', '.join(ret_sm))
        else:
            return mark_safe(''.join(ret_sm))

class HostClassMember(models.Model):
    user = models.ForeignKey(User, related_name='takings')
    host_class = models.ForeignKey('HostClass', related_name='members')
    editor = models.BooleanField(default=False)
    expert = models.BooleanField(default=False)
    host = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user','host_class'),)

#class HostClassEditor(models.Model):
    #host_class_member = models.ForeignKey(HostClassMember, related_name='admin', unique=True)
    #host = models.BooleanField(default=False)
    #host_class = models.ForeignKey(HostClass)

class HostClassSession(models.Model):
    uuid = fields.UUIDField(primary_key=True)
    host_class = models.ForeignKey('HostClass', related_name='dates')
    date = models.DateTimeField()
    course_session = models.ForeignKey('classes.Session')
    
    def session_number(self):
        order = self.host_class.dates.order_by('date')
        for i, ses in enumerate(order):
            if ses.date == self.date:
                return i+1

    def render_hidden_input(self):
        from django.utils.safestring import mark_safe
        return mark_safe('<input type="hidden" id="h_%s" name="h_%s" value="%s" class="hidden-out" />' % (self.uuid, self.uuid, self.date.strftime("%a_%b_%d_%Y %H:%M:%S")))

class HostClassComment(UUIDModel):
    host_class = models.ForeignKey('HostClass', related_name='comments')
    host_member = models.ForeignKey(HostClassMember)
    time = models.DateTimeField(auto_now=True)
    comment = models.TextField()

from invite.models import Request
class HostClassInvite(Request):
    pass
class HostClassSignup(Request):
    pass

#class HostClassExpert(models.Model):
    #host_class_member = models.ForeignKey(HostClassMember, related_name="expert")
    #expert = models.ForeignKey(User, related_name="expert_host")
    #host_class = models.ForeignKey(HostClass, related_name="expert")

    #pay / paid
    #etc

    #class Meta:
        #unique_together = (('expert','host_class'),)


class HostClassAdmin(admin.ModelAdmin):
    pass
admin.site.register(HostClass, HostClassAdmin)
class HostClassInviteAdmin(admin.ModelAdmin):
    pass
admin.site.register(HostClassInvite, HostClassInviteAdmin)
class HostClassSignupAdmin(admin.ModelAdmin):
    pass
admin.site.register(HostClassSignup, HostClassSignupAdmin)
class HostClassMemberAdmin(admin.ModelAdmin):
    pass
admin.site.register(HostClassMember, HostClassMemberAdmin)
class HostClassSessionAdmin(admin.ModelAdmin):
    pass
admin.site.register(HostClassSession, HostClassSessionAdmin)
class HostClassCommentAdmin(admin.ModelAdmin):
    pass
admin.site.register(HostClassComment, HostClassCommentAdmin)

