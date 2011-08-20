from django.contrib import admin
from models import CourseInfo
from models import CourseInfoSession
from models import Institution
from models import Instructor
from models import CourseInstructor
from models import CourseInfoEditor
from models import CourseCategory
from models import Category
from django import forms

class CourseInfoAdminForm(forms.ModelForm):
    class Meta:
        model = CourseInfo

class CourseInfoAdmin(admin.ModelAdmin):
    pass
admin.site.register(CourseInfo, CourseInfoAdmin)

class CourseInfoSessionAdmin(admin.ModelAdmin):
    pass
admin.site.register(CourseInfoSession, CourseInfoSessionAdmin)

class InstitutionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Institution, InstitutionAdmin)

class InstructorAdmin(admin.ModelAdmin):
    pass
admin.site.register(Instructor, InstructorAdmin)

class CourseInstructorAdmin(admin.ModelAdmin):
    pass
admin.site.register(CourseInstructor, CourseInstructorAdmin)

class CourseInfoEditorAdmin(admin.ModelAdmin):
    pass
admin.site.register(CourseInfoEditor, CourseInfoEditorAdmin)

class CourseCategoryAdmin(admin.ModelAdmin):
    pass
admin.site.register(CourseCategory, CourseCategoryAdmin)

class CategoryAdmin(admin.ModelAdmin):
    pass
admin.site.register(Category, CategoryAdmin)
