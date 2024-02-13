from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from django_ca.accounts.models import User


class Command(BaseCommand):
    help = "Create a CA"

    def handle(self, *_args: Any, **_options: Any) -> None:
        if User.objects.filter(is_ca=True).exists():
            self.stdout.write("CA already exists")
            return
        User.objects.create_user(email=settings.CA_EMAIL, is_ca=True)
