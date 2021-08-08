import datetime
from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_date
from core.models import AbstractTimestamp


class Reservation(AbstractTimestamp):
    """Reservation Model"""

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELED, "Canceled"),
    )

    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    check_in = models.DateField()
    check_out = models.DateField()
    guest = models.ForeignKey(
        "users.User", related_name="reservations", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        "rooms.Room", related_name="reservations", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.room} - {self.check_in}"

    def in_progress(self):
        now = get_local_now()
        return now >= self.check_in and now <= self.check_out

    in_progress.boolean = True

    def is_finished(self):
        now = get_local_now()
        return now > self.check_out

    is_finished.boolean = True

    def booked_days(self):
        if self.status == self.STATUS_CANCELED:
            return []
        else:
            if self.check_in and self.check_out:
                booked_days = []
                diff = (self.check_out - self.check_in).days
                for day in range(diff):
                    booked_day = self.check_in + datetime.timedelta(days=day)
                    booked_days.append(booked_day)
                return booked_days
            else:
                return []


def get_local_now():
    return parse_date(timezone.localtime().strftime("%Y-%m-%d"))
