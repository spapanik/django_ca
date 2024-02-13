from __future__ import annotations

from typing import Any, ClassVar

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from django_ca.lib.models import BaseModel, BaseQuerySet, ForeignKey


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
        self, email: str, password: str | None, **extra_fields: Any
    ) -> User:
        if not email:
            msg = "An email must be set"
            raise ValueError(msg)

        email = self.normalize_email(email)
        is_ca = extra_fields.setdefault("is_ca", False)
        if is_ca:
            password = None
        organisation, _ = Organisation.objects.get_or_create_default_org(for_ca=is_ca)
        extra_fields.setdefault("default_organisation", organisation)
        user: User = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> User:
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            msg = "Superuser must have is_staff=True."
            raise ValueError(msg)
        if extra_fields.get("is_superuser") is not True:
            msg = "Superuser must have is_superuser=True."
            raise ValueError(msg)

        return self._create_user(email, password, **extra_fields)


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
    default_organisation = ForeignKey(
        Organisation, on_delete=models.PROTECT, related_name="users"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    objects: ClassVar[UserManager] = UserManager()

    class Meta(AbstractUser.Meta):  # type: ignore[name-defined,misc]
        swappable = "AUTH_USER_MODEL"

    def __str__(self) -> str:
        return self.email
