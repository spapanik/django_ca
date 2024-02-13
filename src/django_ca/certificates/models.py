from __future__ import annotations

from hashlib import sha256
from typing import ClassVar

from django.conf import settings
from django.db import models

from django_ca.accounts.models import Organisation, User
from django_ca.certificates.utils import (
    generate_csr,
    generate_rsa_key,
    generate_self_signed_certificate,
    sign_csr,
)
from django_ca.lib.models import BaseModel, BaseQuerySet


class ServerNameManager(models.Manager.from_queryset(BaseQuerySet["ServerName"])):  # type: ignore[misc]
    pass


class ServerManager(models.Manager.from_queryset(BaseQuerySet["Server"])):  # type: ignore[misc]
    def get_or_create_for_ca(self, ca: User) -> tuple[Server, bool]:
        try:
            server = self.get(user=ca)
        except Server.DoesNotExist:
            server = self.create(
                user=ca,
                organisation=ca.default_organisation,
                common_name=settings.CA_NAME,
            )
            created = True
        else:
            created = False
        return server, created

    def get_or_create_for_alt_names(
        self, user: User, alternative_names: list[str]
    ) -> tuple[Server, bool]:
        if user.is_ca:
            return self.get_or_create_for_ca(user)
        alternative_names = sorted(set(alternative_names))
        common_name = sha256(
            "".join([user.email, *alternative_names]).encode()
        ).hexdigest()
        try:
            server = self.get(common_name=common_name)
        except Server.DoesNotExist:
            server = self.create(
                user=user,
                organisation=user.default_organisation,
                common_name=common_name,
            )
            created = True
            for alternative_name in alternative_names:
                ServerName.objects.create(server=server, name=alternative_name)
        else:
            created = False
        return server, created


class KeyManager(models.Manager.from_queryset(BaseQuerySet["Key"])):  # type: ignore[misc]
    def get_or_create_server_key(self, server: Server) -> tuple[Key, bool]:
        try:
            key = self.get(server=server)
        except Key.DoesNotExist:
            key = self.create(server=server, private_key=generate_rsa_key())
            created = True
        else:
            created = False
        return key, created


class CertificateManager(models.Manager.from_queryset(BaseQuerySet["Certificate"])):  # type: ignore[misc]
    def get_or_create_server_cert(
        self, server: Server, *, self_signed: bool = False
    ) -> tuple[Certificate, bool]:
        try:
            key = self.get(server=server)
        except Certificate.DoesNotExist:
            info = self._get_cert_info(server, self_signed=self_signed)
            key = self.create(
                server=server,
                self_signed=self_signed,
                csr=info["csr"],
                certificate=info["certificate"],
            )
            created = True
        else:
            created = False
        return key, created

    def _get_cert_info(self, server: Server, *, self_signed: bool) -> dict[str, str]:
        if self_signed:
            csr = ""
            certificate = generate_self_signed_certificate(
                country=server.organisation.country,
                province=server.organisation.province,
                locality=server.organisation.locality,
                organisation=server.organisation.name,
                common_name=settings.CA_NAME,
                email_address=server.organisation.email,
                private_key=server.key.private_key,
            )
            return {"csr": "", "certificate": certificate}
        ca_cert = self.get(self_signed=True)
        csr = generate_csr(
            country=server.organisation.country,
            province=server.organisation.province,
            locality=server.organisation.locality,
            organisation=server.organisation.name,
            common_name=server.common_name,
            email_address=server.organisation.email,
            alternative_names=server.alternative_names.flat_values("name"),
            private_key=server.key.private_key,
        )
        certificate = sign_csr(csr, ca_cert.certificate, ca_cert.server.key.private_key)
        return {"csr": csr, "certificate": certificate}


class Server(BaseModel):
    user = models.ForeignKey(
        User, related_name="certificates", on_delete=models.CASCADE
    )
    organisation = models.ForeignKey(
        Organisation, on_delete=models.PROTECT, related_name="certificates"
    )
    common_name = models.CharField(max_length=2047, unique=True)

    objects: ClassVar[ServerManager] = ServerManager()

    def __str__(self) -> str:
        alternative_names = self.alternative_names.flat_values("name")
        if alternative_names.exists():
            return ", ".join(alternative_names)
        return self.common_name


class ServerName(BaseModel):
    server = models.ForeignKey(
        Server, on_delete=models.CASCADE, related_name="alternative_names"
    )
    name = models.CharField(max_length=2047)

    objects: ClassVar[ServerManager] = ServerManager()

    class Meta:
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["server", "name"], name="unique_server_name"
            )
        ]

    def __str__(self) -> str:
        return self.name


class Key(BaseModel):
    server = models.OneToOneField(Server, on_delete=models.CASCADE)
    private_key = models.CharField(max_length=3272)

    objects: ClassVar[KeyManager] = KeyManager()

    def __str__(self) -> str:
        return self.server.common_name


class Certificate(BaseModel):
    server = models.OneToOneField(Server, on_delete=models.CASCADE)
    self_signed = models.BooleanField(default=False)
    csr = models.TextField()
    certificate = models.TextField()

    objects: ClassVar[CertificateManager] = CertificateManager()

    def __str__(self) -> str:
        return self.server.common_name
