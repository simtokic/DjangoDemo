import re

from django import template
from django.urls import NoReverseMatch, reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    try:
        pattern = '^' + reverse(pattern_or_urlname) + '$'
    except NoReverseMatch:
        pattern = pattern_or_urlname
    path = context['request'].path
    if re.search(pattern, path):
        return 'active'
    return ''


@register.simple_tag
def progress_color_class(progress):
    color_class = ''
    if progress >= 0 and progress <= 25:
        color_class = 'progress-bar-danger'
    elif progress > 25 and progress <= 50:
        color_class = 'progress-bar-yellow'
    elif progress > 50 and progress <= 75:
        color_class = 'progress-bar-primary'
    elif progress > 75 and progress <= 100:
        color_class = 'progress-bar-success'

    return color_class


@register.simple_tag
def badge_color_class(progress):
    color_class = ''
    if progress >= 0 and progress <= 25:
        color_class = 'bg-red'
    elif progress > 25 and progress <= 50:
        color_class = 'bg-yellow'
    elif progress > 50 and progress <= 75:
        color_class = 'bg-light-blue'
    elif progress > 75 and progress <= 100:
        color_class = 'bg-green'

    return color_class


@register.simple_tag
def text_weight_class(condition):
    text_class = ''
    if not condition:
        text_class = 'text-bold-600'

    return text_class
