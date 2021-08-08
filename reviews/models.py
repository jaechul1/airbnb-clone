from django.db import models
from core.models import AbstractTimestamp


class Review(AbstractTimestamp):
    class Meta:
        ordering = ("-created",)

    RATE_CHOICES = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    )

    review = models.TextField()
    accuracy = models.IntegerField(choices=RATE_CHOICES, default=5)
    communication = models.IntegerField(choices=RATE_CHOICES, default=5)
    cleanliness = models.IntegerField(choices=RATE_CHOICES, default=5)
    location = models.IntegerField(choices=RATE_CHOICES, default=5)
    check_in = models.IntegerField(choices=RATE_CHOICES, default=5)
    value = models.IntegerField(choices=RATE_CHOICES, default=5)
    user = models.ForeignKey(
        "users.User", related_name="reviews", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        "rooms.Room", related_name="reviews", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.review} - {self.room}"

    def rating_average(self):
        avg = (
            self.accuracy
            + self.communication
            + self.cleanliness
            + self.location
            + self.check_in
            + self.value
        ) / 6
        return round(avg, 2)
