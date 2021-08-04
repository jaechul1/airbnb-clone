from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField
from core.models import AbstractTimestamp


class AbstractItem(AbstractTimestamp):
    """Abstract Item"""

    name = models.CharField(max_length=80)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class RoomType(AbstractItem):
    """RoomType Model"""

    class Meta:
        verbose_name = "Room Type"
        ordering = ["name"]


class Amenity(AbstractItem):
    """Amenity Model"""

    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ["name"]


class Facility(AbstractItem):
    """Facility Model"""

    class Meta:
        verbose_name_plural = "Facilities"
        ordering = ["name"]


class HouseRule(AbstractItem):
    """HouseRule Model"""

    class Meta:
        verbose_name = "House Rule"
        ordering = ["name"]


class Photo(AbstractTimestamp):
    """Photo Model"""

    caption = models.CharField(max_length=80)
    file = models.ImageField(upload_to="rooms")
    room = models.ForeignKey("Room", related_name="photos", on_delete=models.CASCADE)

    def __str__(self):
        return self.caption


class Room(AbstractTimestamp):
    """Room Model"""

    name = models.CharField(max_length=140)
    description = models.TextField()
    country = CountryField()
    city = models.CharField(max_length=80)
    price = models.IntegerField()
    address = models.CharField(max_length=140)
    guests = models.IntegerField(help_text="How many guests will be staying?")
    beds = models.IntegerField()
    bedrooms = models.IntegerField()
    baths = models.IntegerField()
    check_in = models.TimeField()
    check_out = models.TimeField()
    instant_book = models.BooleanField(default=False)
    host = models.ForeignKey(
        "users.User", related_name="rooms", on_delete=models.CASCADE
    )
    room_type = models.ForeignKey(
        "RoomType", related_name="rooms", on_delete=models.SET_NULL, null=True
    )
    amenities = models.ManyToManyField("Amenity", related_name="rooms", blank=True)
    facilities = models.ManyToManyField("Facility", related_name="rooms", blank=True)
    house_rules = models.ManyToManyField("HouseRule", related_name="rooms", blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.city = self.city.title()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("rooms:detail", kwargs={"pk": self.pk})

    def total_rating(self):
        all_reviews = self.reviews.all()
        all_ratings = [review.rating_average() for review in all_reviews]
        try:
            total_avg = sum(all_ratings) / len(all_ratings)
            return round(total_avg, 2)
        except ZeroDivisionError:
            return 0

    def first_photo(self):
        photo, = self.photos.all()[:1]
        return photo.file.url