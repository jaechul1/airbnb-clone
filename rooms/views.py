from django.http import Http404
from django.views.generic import ListView, DetailView, View, UpdateView, CreateView
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator, Page
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from users import mixins
from . import models, forms


class HomeView(ListView):
    """Home view"""

    model = models.Room
    paginate_by = 12
    paginate_orphans = 5
    ordering = "created"
    context_object_name = "rooms"


class RoomDetail(DetailView):
    """Room detail view"""

    model = models.Room


class SearchView(View):
    """Room search view"""

    def get(self, request):

        country = request.GET.get("country")

        if country:

            form = forms.SearchForm(request.GET)

            if form.is_valid():

                populated_data = form.cleaned_data

                city = populated_data.get("city")
                country = populated_data.get("country")
                room_type = populated_data.get("room_type")
                price = populated_data.get("price")
                guests = populated_data.get("guests")
                bedrooms = populated_data.get("bedrooms")
                beds = populated_data.get("beds")
                baths = populated_data.get("baths")
                instant_book = populated_data.get("instant_book")
                superhost = populated_data.get("superhost")
                amenities = populated_data.get("amenities")
                facilities = populated_data.get("facilities")

                filter_args = {}

                if city != "Anywhere":
                    filter_args["city__startswith"] = city

                filter_args["country"] = country

                if room_type is not None:
                    filter_args["room_type"] = room_type

                if price is not None:
                    filter_args["price__lte"] = price

                if guests is not None:
                    filter_args["guests__gte"] = guests

                if bedrooms is not None:
                    filter_args["bedrooms__gte"] = bedrooms

                if beds is not None:
                    filter_args["beds__gte"] = beds

                if baths is not None:
                    filter_args["baths__gte"] = baths

                if instant_book is True:
                    filter_args["instant_book"] = True

                if superhost is True:
                    filter_args["host__superhost"] = True

                qs = models.Room.objects.filter(**filter_args)

                for amenity in amenities:
                    qs = qs.filter(amenities=amenity)

                for facility in facilities:
                    qs = qs.filter(facilities=facility)

                qs = qs.order_by("-created")

                paginator = Paginator(qs, 10)

                page = int(request.GET.get("page", 1))

                rooms = paginator.get_page(page)

        else:

            form = forms.SearchForm()
            rooms = Page(
                [], number=0, paginator=Paginator([], 10)
            )  # just an empty Page for type match with if-case

        return render(request, "rooms/search.html", {"form": form, "rooms": rooms})


class EditRoomView(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):

    model = models.Room
    template_name = "rooms/room_edit.html"
    fields = (
        "name",
        "description",
        "price",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    )
    success_message = "Room updated."

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room


class RoomPhotosView(mixins.LoggedInOnlyView, DetailView):

    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room


@login_required
def delete_photo(request, room_pk, photo_pk):
    user = request.user
    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            messages.error(request, "You can't access this page.")
            return redirect(reverse("core:home"))
        else:
            models.Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Photo deleted.")
            return redirect(reverse("rooms:photos", kwargs={"pk": room_pk}))
    except models.Room.DoesNotExist:
        return redirect(reverse("core:home"))


class EditPhotoView(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):

    model = models.Photo
    template_name = "rooms/photo_edit.html"
    pk_url_kwarg = "photo_pk"
    success_message = "Photo updated."
    fields = ("caption",)

    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photos", kwargs={"pk": room_pk})


class AddPhotoView(mixins.LoggedInOnlyView, CreateView):

    model = models.Photo
    template_name = "rooms/photo_add.html"
    fields = ("caption", "file")

    def form_valid(self, form):
        pk = self.kwargs.get("pk")
        form.instance.room = models.Room.objects.get(pk=pk)
        form.save()
        messages.success(self.request, "Photo uploaded.")
        return redirect(reverse("rooms:photos", kwargs={"pk": pk}))


class CreateRoomView(mixins.LoggedInOnlyView, CreateView):

    model = models.Room
    template_name = "rooms/room_create.html"
    fields = (
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    )

    def form_valid(self, form):
        form.instance.host = self.request.user
        room = form.save()
        messages.success(self.request, "Room created.")
        return redirect(reverse("rooms:detail", kwargs={"pk": room.pk}))
