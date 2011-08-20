from django.contrib.auth.models import User

class EmailBackend(object):
    def authenticate(self, **credentials):
        if 'username' in credentials:
            return self.authenticate_by_username(**credentials)
        else:
            return self.authenticate_by_email(**credentials)
    def authenticate_by_username(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def authenticate_by_email(self, username=None, password=None):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class FacebookBackend(object):
    """ merge this in with django_socialauth """
    def authenticate(self, request):
        fb_user = facebook.get_user_from_cookie(self.request.cookies, FACEBOOK_API_KEY, FACEBOOK_API_SECRET)
        print fb_user
        if fb_user:
            graph = facebook.GraphAPI(fb_user["oauth_access_token"])
            print graph

            try:
                profile = FacebookUser.objects.get(facebook_uid = str(fb_user))
                return profile.user
            except FacebookUserProfile.DoesNotExist:
                fb_data = graph.get_objects(["uid", 'me', 'first_name', 'last_name', 'pic_big', 'pic', 'pic_small', 'current_location', 'profile_url'])
                print fb_data
                if not fb_data:
                    return None
                fb_data = fb_data[0]

                username = 'FB:%s' % fb_data['uid']
                #user_email = '%s@example.facebook.com'%(fb_data['uid'])
                user = User.objects.create(username = username)
                user.first_name = fb_data['first_name']
                user.last_name = fb_data['last_name']
                user.save()
                location = str(fb_data['current_location'])
                about_me = str(fb_data['about_me'])
                url = str(fb_data['profile_url'])
                fb_profile = FacebookUserProfile(facebook_uid = str(fb_data['uid']), user = user, profile_image_url = fb_data['pic'], profile_image_url_big = fb_data['pic_big'], profile_image_url_small = fb_data['pic_small'], location=location, about_me=about_me, url=url)
                fb_profile.save()
                auth_meta = AuthMeta(user=user, provider='Facebook').save()
                return user
            except Exception, e:
                print str(e)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

