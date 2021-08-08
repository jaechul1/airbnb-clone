from django import template
from django.contrib.auth.decorators import login_required
from lists import models as list_models


register = template.Library()


@login_required
@register.simple_tag(takes_context=True)
def on_favs(context, room):
    user = context.request.user
    the_list = list_models.List.objects.get_or_none(user=user, name="Favorite Rooms")
    if not the_list:
        return False
    return room in the_list.rooms.all()
