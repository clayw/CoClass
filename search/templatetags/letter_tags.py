from django import template
from django.utils.translation import ungettext, ugettext as _
import re
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def render_with_letter(result):
    try:
        fst, snd = result.rendered.split('<div class="ltr"></div>')
        new_result = fst + '<div class="ltr">' + result.letter + '</div>' + snd
        return mark_safe(new_result)
    except:
        return mark_safe(result.rendered)

