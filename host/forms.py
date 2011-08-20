from django import forms
from django.forms.extras.widgets import SelectDateWidget
import datetime

from widgets import SelectTimeWidget


class MakeHostForm(forms.Form):
    course = forms.CharField(max_length=100) # required

class CourseSessionForm(forms.Form):
    check_monday = forms.BooleanField(required=False)
    check_tuesday = forms.BooleanField(required=False)
    check_wednesday = forms.BooleanField(required=False)
    check_thursday = forms.BooleanField(required=False)
    check_friday = forms.BooleanField(required=False)
    check_saturday = forms.BooleanField(required=False)
    check_sunday = forms.BooleanField(required=False)
    
    privacy = forms.CharField(required=True, max_length=1)
    starting_date = forms.DateField(required=True, widget=SelectDateWidget, initial=datetime.datetime.now())
    time = forms.TimeField(widget=SelectTimeWidget(minute_step=5, twelve_hr=True), initial=datetime.time(19,30))

    next = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        m = cleaned_data['check_monday']
        tu = cleaned_data['check_tuesday']
        w = cleaned_data['check_wednesday']
        th = cleaned_data['check_thursday']
        f = cleaned_data['check_friday']
        sa = cleaned_data['check_saturday']
        su = cleaned_data['check_sunday']

        days_of_week = []
        if m: days_of_week.append(1)
        if tu: days_of_week.append(2)
        if w: days_of_week.append(3)
        if th: days_of_week.append(4)
        if f: days_of_week.append(5)
        if sa: days_of_week.append(6)
        if su: days_of_week.append(7)
        cleaned_data['days_of_week'] = days_of_week
        if m or tu or w or th or f or sa or su:
            return cleaned_data
        else:
            raise forms.ValidationError("Pick at least one day of the week")

    def save(self, course=None, place=None, host_class=None):
        cleaned_data = self.cleaned_data
        m = cleaned_data['check_monday']
        tu = cleaned_data['check_tuesday']
        w = cleaned_data['check_wednesday']
        th = cleaned_data['check_thursday']
        f = cleaned_data['check_friday']
        sa = cleaned_data['check_saturday']
        su = cleaned_data['check_sunday']
        dt = cleaned_data['time'] 
        privacy = cleaned_data['privacy'] 
        st_date = cleaned_data['starting_date']
        next = cleaned_data['next']
        try:
            created = False
        except:
            created = True
        from host.models import HostClass
        if host_class:
            host_class.course = course
            host_class.place = place
            host_class.meeting_time = dt
            host_class.monday=m
            host_class.tuesday=tu
            host_class.wednesday=w
            host_class.thursday=th
            host_class.friday=f
            host_class.saturday=sa
            host_class.sunday=su
            host_class.disp_start_date=st_date
            host_class.created=created
            host_class.privacy = privacy
        else:
            host_class = HostClass(course=course, place=place, meeting_time=dt, \
               monday=m, tuesday=tu, wednesday=w, thursday=th, friday=f, saturday=sa, sunday=su, \
               disp_start_date=st_date, privacy=privacy, created=created)
        host_class.save()
        return host_class

class MakeCourseForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    prerequisites = forms.CharField(widget=forms.Textarea, required=False)
    #from_date = forms.CharField(max_length=20, required=False)
    #institution = forms.CharField(max_length=200,required=False)
    #course_number = forms.CharField(max_length=20, required=False)
    url = forms.URLField(required=False)
    #instructors = forms.CharField(max_length=1000, required=False)

class SessionEditForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    video_url = forms.CharField(max_length=100, required=False)
    date = forms.DateField(widget=SelectDateWidget, required=False)
    time = forms.TimeField(widget=SelectTimeWidget(minute_step=5, twelve_hr=True), required=False)

    def save(self, host_class, host_session=None, del_links=None, add_links=None):
        from classes.models import Session
        from host.models import HostClassSession
#        if host_session:
#            session = host_session.course_session
#            session.title = self.cleaned_data['title']
#            session.description = self.cleaned_data['description']
#            session.video_url = self.cleaned_data['video_url']
#
#        else:
        if host_session:
            course_session = host_session.course_session #
        else:
            course_session = None
        session = Session(title=self.cleaned_data['title'], description=self.cleaned_data['description'], video_url=self.cleaned_data['video_url'], previous_version=course_session)
        session.save()
        links = session.link.all()
        for link in links:
            if not link.uuid in del_links:
                SessionLink(url=link.url, title=link.title, session=session).save()
        for url, title in add_links:
            SessionLink(url=url, title=title, session=session).save()

        date = self.cleaned_data['date']
        time = self.cleaned_data['time']
        if host_session:
            host_session.date = datetime.datetime.combine(date,time)
            host_session.course_session = session
        else: 
            host_session = HostClassSession(course_session=session, host_class=host_class, date=datetime.datetime.combine(date,time))
        host_session.save()

        #for key in request.GET:
        #    try:
        #        type, number = key.split('_')
        #        if type == 'video':
        #            session_video = SessionLink(session=course_session, url=video_url)
        #    except:
        #        pass

        return host_session

class InviteForm(forms.Form):
    pass
    #body = 
