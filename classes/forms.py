from django import forms

from classes.models import Session
from classes.models import SessionLink

class SessionForm(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    video_url = forms.CharField(max_length=100, required=False)

    def save(self, session=None, del_links=None, add_links=None):
        new_session = Session(title=self.cleaned_data['title'], description=self.cleaned_data['description'], video_url=self.cleaned_data['video_url'])
        if session:
            new_session.previous_version = session
            links = session.link.all()
        else:
            links = []
        new_session.save()
        for link in links:
            if not link.uuid in del_links:
                SessionLink(url=link.url, title=link.title, session=new_session).save()
        for url, title in add_links:
            SessionLink(url=url, title=title, session=new_session).save()

        return new_session

class SessionAuxForm(forms.Form):
    session_number = forms.IntegerField(min_value=1, max_value=1000, required=False)
