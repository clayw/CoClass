from django.contrib import admin
from models import UserProfile
from models import Expert
from socialauth.models import AuthMeta
from socialauth.models import FacebookUserProfile


class UserProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserProfile, UserProfileAdmin)


class ExpertAdmin(admin.ModelAdmin):
    pass
admin.site.register(Expert, ExpertAdmin)
