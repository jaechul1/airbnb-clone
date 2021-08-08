import datetime
from django.http import Http404
from django.views.generic import View
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from rooms import models as room_models
from reviews import forms as review_forms
from . import models
from cal import Date_with_past


class CreateError(Exception):
    pass


def create(request, pk, year, month, day):
    try:
        date_obj = Date_with_past(year, month, day)
        room = room_models.Room.objects.get(pk=pk)
        reservations = models.Reservation.objects.filter(room=room)
        booked_days = set()
        for reservation in reservations:
            booked_days.update(reservation.booked_days())
        if date_obj in booked_days:
            raise CreateError()
    except (room_models.Room.DoesNotExist, CreateError):
        messages.error(request, "Reservation failed.")
        return redirect(reverse("core:home"))
    datetime_obj = datetime.datetime(year, month, day)
    reservation = models.Reservation.objects.create(
        guest=request.user,
        room=room,
        check_in=datetime_obj,
        check_out=datetime_obj + datetime.timedelta(days=1),
    )
    messages.success(request, "Reservation created.")
    return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))


class ReservationDetailView(View):
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        reservation = models.Reservation.objects.get_or_none(pk=pk)
        if not reservation or (
            reservation.guest != self.request.user
            and reservation.room.host != self.request.user
        ):
            raise Http404()
        form = review_forms.CreateReviewForm()
        return render(
            self.request,
            "reservations/reservation_detail.html",
            {"reservation": reservation, "form": form},
        )


def edit_reservation(request, pk, verb):
    reservation = models.Reservation.objects.get_or_none(pk=pk)
    if not reservation or (
        reservation.guest != request.user and reservation.room.host != request.user
    ):
        raise Http404()
    if verb == "confirm":
        reservation.status = models.Reservation.STATUS_CONFIRMED
    elif verb == "cancel":
        reservation.status = models.Reservation.STATUS_CANCELED
    reservation.save()
    messages.success(request, "Reservation updated.")
    return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))
