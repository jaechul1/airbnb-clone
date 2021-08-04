from django.views.generic import ListView, DetailView, View
from django.shortcuts import render
from django.core.paginator import Paginator, Page
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
