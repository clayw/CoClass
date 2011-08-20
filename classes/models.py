from django.db import models
from django.contrib.auth.models import User
import StringIO
import Image, ImageOps
import hashlib
import os
import django.core.files
from datetime import datetime

from django_extensions.db import fields

import course_miners 
from logicaldelete.models import LogicalDeleteModel, UUIDModel
from auxiliary import int_to_base36
from auxiliary import title_to_url
from django.utils.safestring import mark_safe

class CourseInfo(LogicalDeleteModel):
    previous_version = models.ForeignKey('CourseInfo', null=True, blank=True)
    title = models.CharField(max_length=500)
    description = models.TextField()
    prereqs = models.TextField(null=True, blank=True)
    from_date = models.CharField(max_length=20, null=True, blank=True)
    course_number = models.CharField(max_length=20, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    published = models.BooleanField(default=False)

    def instructors(self):
        instructors = [cis.instructor.name for cis in self.course_instructor.all()]
        return ", ".join(instructors)
    def insitutions(self):
        institutions = [cis.institution.name for cis in self.course_institution.all()]
        return ", ".join(institutions)

    def get_rating(self):
        # 2 * N 
        num_ratings = self.rating.count()
        if num_ratings > 0:
            ratings = float(sum([r.rating for r in self.rating.all()])) / num_ratings
            return ratings
        else:
            return num_ratings

    def in_order_sessions(self):
        session_links = list(self.course_info_session.order_by('session_number'))
        return [sl.session for sl in session_links]

    def b36(self):
        return (int_to_base36(self.pk))

    def get_absolute_url(self):
        return '/c/v/%s/%s/' % (int_to_base36(self.pk), self)

    def is_editor(self, user):
        try:
            return self.editor.get(editor=user)
        except:
            return None

    def __unicode__(self):
        cnv = self.title
        if self.course_number:
            cnv = self.course_number + ' ' + cnv        
        if self.from_date:
            cnv += ' ' + self.from_date
        return title_to_url(cnv)

    class Meta:
        pass
        #order_by = ['']

class Category(models.Model):
    """ Categories have a hierarchical structure """
    name = models.CharField(max_length=200, primary_key=True)
    parent_category = models.ForeignKey('Category', related_name='children', null=True, blank=True)

    def __unicode__(self):
        return ' '.join([sp[0].upper() + sp[1:] for sp in self.name.split('_')])

    def get_parent_html(self):
        par = self.parent_category
        if par:
            return mark_safe('<a href="%s">%s</a>' % (par.get_absolute_url, par.name))
        else:
            return mark_safe('<a href="/c/directory/">Main</a>')

    def get_absolute_url(self):
        par = self.parent_category
        pc = [self.name]
        while par:
            pc.append(par.name) 
            par = par.parent_category
        pc.reverse()
        return '/c/directory/' + '/'.join(pc)

class CourseCategory(models.Model):
    """ A course can have multiple categories """
    courseinfo = models.ForeignKey('CourseInfo', related_name='coursecategory')
    category = models.ForeignKey('Category', related_name='coursecategory')

    class Meta:
        unique_together = (('courseinfo', 'category'),)

class CourseInfoEditor(models.Model):
    """ The "admin" object """
    editor = models.ForeignKey(User, related_name="course_info_editor")
    course_info = models.ForeignKey('CourseInfo', related_name="editor")
    creator = models.BooleanField(default=False)

class CourseInfoRating(models.Model):
    course_info = models.ForeignKey('CourseInfo', related_name="rating")
    user = models.ForeignKey(User, related_name='rating')
    rating = models.PositiveIntegerField() # change to 1-5 scale

    class Meta:
        unique_together = (('course_info', 'user'))

class CourseInfoSession(UUIDModel):
    """ This only needs to be used if the course is published for searching and rating"""
    course_info = models.ForeignKey(CourseInfo, related_name='course_info_session')
    session = models.ForeignKey('Session', related_name='course_info_session')
    session_number = models.PositiveIntegerField()

    def get_absolute_url(self):
        return '%s/%s/' % (self.course_info.get_absolute_url, self.uuid)

    class Meta:
        ordering = ['session_number']

class Session(UUIDModel):
    previous_version = models.ForeignKey('Session', null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_url = models.URLField()

    def url(self):
        return self.video_url

    def get_absolute_url(self):
        return '/c/v/%s/' % (self.pk)

class SessionLink(UUIDModel):
    session = models.ForeignKey('Session', related_name='link')
    url = models.URLField()
    title = models.CharField(max_length=100)

#class SessionVideo(models.Model):
#    course_info_session = models.ForeignKey('Session', related_name='video')
#    url = models.URLField()
#    #main = models.BooleanField(default=False)
#
#class SessionAssignment(models.Model):
#    session = models.ForeignKey(Session, related_name='assignment')
#    url = models.URLField()
#
#class SessionReading(models.Model):
#    session = models.ForeignKey(Session, related_name='reading')
#    text = models.TextField()

class Institution(models.Model):
    name = models.CharField(max_length=200) # e.g., stanford
    def __str__(self):
        return self.name

class CourseInstitution(models.Model):
    course_info = models.ForeignKey('CourseInfo', related_name='course_institution')
    institution = models.ForeignKey('Institution', related_name='course_institution')

class Instructor(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class CourseInstructor(models.Model):
    """ courses may have more than one instructor, guest lecturer, etc """
    course_info = models.ForeignKey('CourseInfo', related_name='course_instructor')
    instructor = models.ForeignKey('Instructor', related_name='course_instructor')

    def __str__(self):
        return str(self.instructor)

