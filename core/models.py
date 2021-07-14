from django.db import models


class AbstractTimestamp(models.Model):
    """Abstract Timestamp Model for model extensions"""

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
