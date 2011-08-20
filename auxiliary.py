import cStringIO as StringIO
import re
import Image
import hashlib
import os
import settings

from django.utils.encoding import force_unicode
from django.core.files.base import ContentFile
from django.core.files import File
from django.db.models.fields.files import ImageFieldFile

rx_whitespace = re.compile('\s+', re.UNICODE)
rx_notsafe = re.compile('\W+', re.UNICODE)
rx_underscore = re.compile('_+', re.UNICODE)
rx_colondash = re.compile('[:-]', re.UNICODE)
def title_to_url(title, max_length = 50):
    """Takes a string and makes it suitable for use in URLs"""
    title = force_unicode(title)    
    title = rx_whitespace.sub('_', title)
    title = rx_colondash.sub('_', title)
    title = rx_notsafe.sub('', title)   
    title = rx_underscore.sub('_', title)  
    title = title.strip('_')
    title = title.lower()
    if len(title) > max_length:
        title = title[:max_length]
        last_word = title.rfind('_')
        if (last_word > 0):
            title = title[:last_word]
    return title

def base36_to_int(s):
    """ convert base36 to int for urls """
    return int(s, 36)

def int_to_base36(i):
    """ convert int value to base36 """
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    factor = 0
    # Find starting factor
    while True:
        factor += 1
        if i < 36 ** factor:
            factor -= 1
            break
    base36 = []
    # Construct base36 representation
    while factor >= 0:
        j = 36 ** factor
        base36.append(digits[i / j])
        i = i % j
        factor -= 1
    return ''.join(base36)



def generic_handle_pic(image_data):
    """ 
    Takes raw image data from web and 
    saves a copy of the full image (to be non-retrievable)
    """
    unsizefile  = StringIO.StringIO(image_data.read())  
    unsizeImage = Image.open(unsizefile)  
    filename = hashlib.sha1(unsizefile.getvalue()).hexdigest()+'.jpg'  
    unsizeimagefile = open(os.path.join(settings.MEDIA_ROOT, 'p/' + filename), 'w')  
    unsizeImage.save(unsizeimagefile,'JPEG')
    unsimagefile = open(os.path.join(settings.MEDIA_ROOT, 'p/' + filename), 'r')  
    content = File(unsimagefile)
    return filename, content 

from django.conf import settings
from django.http import HttpResponseRedirect

def secure_required(view_func):
    """Decorator makes sure URL is accessed over https."""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.is_secure():
            if getattr(settings, 'HTTPS_SUPPORT', True):
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(secure_url)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

