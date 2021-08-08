from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.contrib.auth.decorators import login_required
from rooms import models as room_models
from . import forms


@login_required
def create_review(request, room_pk):
    if request.method == "POST":
        form = forms.CreateReviewForm(request.POST)
        room = room_models.Room.objects.get_or_none(pk=room_pk)
        if not room:
            return redirect(reverse("core:home"))
        if form.is_valid():
            review = form.save()
            review.room = room
            review.user = request.user
            review.save()
            messages.success(request, "Review submitted.")
            return redirect(reverse("rooms:detail", kwargs={"pk": room_pk}))
