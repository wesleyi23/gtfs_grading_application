from django import template

from gtfs_grading_app.models import gtfs_field

register = template.Library()


@register.filter
def field_name_to_label(value):
    value = value.replace('_', ' ')
    return value.title()


@register.filter
def addition(value, add_amount):
    value = int(value) + add_amount
    return value


@register.filter
def get_gtfs_field_name_from_id(gtfs_field_id):
    return gtfs_field.objects.get(id=gtfs_field_id).field_name_to_label


@register.filter()
def score_display_round(score):
    if float(score).is_integer():
        return round(score, 0)
    else:
        return score


@register.filter()
def plus1(number):
    return number + 1
