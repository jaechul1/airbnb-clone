from django.db import models
from . import managers


class AbstractTimestamp(models.Model):
    """Abstract Timestamp Model for model extensions"""

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = managers.CustomModelManager()

    class Meta:
        abstract = True
