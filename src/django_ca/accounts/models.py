from __future__ import annotations

from typing import ClassVar

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from django_ca.lib.models import BaseModel, BaseQuerySet


class OrganisationManager(models.Manager.from_queryset(BaseQuerySet["Organisation"])):  # type: ignore[misc]
    def get_or_create_default_org(self, *, for_ca: bool) -> tuple[Organisation, bool]:
        try:
            organisation = self.get(ca_rights=for_ca)
        except Organisation.DoesNotExist:
            organisation = self.model(
                country=settings.DEFAULT_COUNTRY,
                province=settings.DEFAULT_PROVINCE,
                locality=settings.DEFAULT_LOCALITY,
                name=settings.CA_NAME if for_ca else settings.SERVER_NAME,
                email=settings.CA_EMAIL if for_ca else settings.SERVER_EMAIL,
                ca_rights=for_ca,
            )
            organisation.save(using=self._db)
            created = True
        except Organisation.MultipleObjectsReturned:
            organisation = self.filter(ca_rights=for_ca).first()
            created = False
        else:
            created = False
        return organisation, created


class UserManager(BaseUserManager.from_queryset(BaseQuerySet["User"])):  # type: ignore[misc]
    use_in_migrations = True

    def _create_user(
        self,
        email: str,
        password: str | None,
        *,
        is_superuser: bool,
        is_staff: bool,
        is_active: bool,
        is_ca: bool,
        organisation: Organisation | None,
    ) -> User:
        if not email:
            msg = "An email must be set"
            raise ValueError(msg)

        email = self.normalize_email(email)
        if organisation is None:
            organisation, _ = Organisation.objects.get_or_create_default_org(
                for_ca=is_ca
            )
        if is_ca:
            password = None
        user: User = self.model(
            email=email,
            is_superuser=is_superuser,
            is_staff=is_staff,
            default_organisation=organisation,
            is_active=is_active,
            is_ca=is_ca,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_ca(
        self,
        email: str,
        password: str | None = None,
        *,
        is_active: bool = True,
        organisation: Organisation | None = None,
    ) -> User:
        return self._create_user(
            email=email,
            password=password,
            is_superuser=False,
            is_staff=False,
            is_ca=True,
            is_active=is_active,
            organisation=organisation,
        )

    def create_user(
        self,
        email: str,
        password: str | None = None,
        *,
        is_active: bool = True,
        organisation: Organisation | None = None,
    ) -> User:
        return self._create_user(
            email=email,
            password=password,
            is_superuser=False,
            is_staff=False,
            is_ca=False,
            is_active=is_active,
            organisation=organisation,
        )

    def create_staff(
        self,
        email: str,
        password: str | None = None,
        *,
        is_active: bool = True,
        organisation: Organisation | None = None,
    ) -> User:

        return self._create_user(
            email=email,
            password=password,
            is_staff=True,
            is_superuser=False,
            is_ca=False,
            is_active=is_active,
            organisation=organisation,
        )

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        *,
        is_active: bool = True,
        organisation: Organisation | None = None,
    ) -> User:

        return self._create_user(
            email=email,
            password=password,
            is_superuser=True,
            is_staff=True,
            is_ca=False,
            is_active=is_active,
            organisation=organisation,
        )


class Organisation(BaseModel):
    country = models.CharField(max_length=2)
    province = models.CharField(max_length=255)
    locality = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    ca_rights = models.BooleanField(default=False)

    objects: ClassVar[OrganisationManager] = OrganisationManager()

    def __str__(self) -> str:
        return self.name


class User(AbstractUser, BaseModel):
    username = None  # type: ignore[assignment]
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = models.EmailField(unique=True)
    is_ca = models.BooleanField(default=False)
    default_organisation = models.ForeignKey(
        Organisation, on_delete=models.PROTECT, related_name="users"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    objects: ClassVar[UserManager] = UserManager()

    class Meta(AbstractUser.Meta):  # type: ignore[name-defined,misc]
        swappable = "AUTH_USER_MODEL"

    def __str__(self) -> str:
        return self.email
