from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):

        users = User.objects.all()
        for user in users:
            user.avatar = None
            user.save()
