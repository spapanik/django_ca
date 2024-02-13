from django.core.management.base import BaseCommand

from django_ca.accounts.models import User
from django_ca.certificates.models import Certificate, Key, Server


class Command(BaseCommand):
    help = "Create a CA Certificate"

    def handle(self, *_args: object, **_options: object) -> None:
        if Certificate.objects.filter(self_signed=True).exists():
            self.stdout.write("CA certificate already exists")
            return
        ca = User.objects.get(is_ca=True)
        server, _ = Server.objects.get_or_create_for_ca(ca)
        key, _ = Key.objects.get_or_create_server_key(server)
        Certificate.objects.get_or_create_server_cert(server, self_signed=True)
