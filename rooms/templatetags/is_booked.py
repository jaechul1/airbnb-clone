from django import template
from reservations.models import Reservation

register = template.Library()


@register.simple_tag()
def is_booked(room, day):
    reservations = Reservation.objects.filter(room=room)
    for reservation in reservations:
        if day in reservation.booked_days():
            return True
    return False
