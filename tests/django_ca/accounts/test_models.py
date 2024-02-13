from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from django_ca.accounts.models import User

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_django import DjangoAssertNumQueries


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("method", "is_superuser", "is_staff", "is_ca", "is_active"),
    [
        (User.objects.create_ca, False, False, True, True),
        (User.objects.create_user, False, False, False, True),
        (User.objects.create_staff, False, True, False, True),
        (User.objects.create_superuser, True, True, False, True),
    ],
)
def test_user_created(
    method: Callable,
    is_superuser: bool,
    is_staff: bool,
    is_ca: bool,
    is_active: bool,
    django_assert_num_queries: DjangoAssertNumQueries,
) -> None:
    email = "carl.sagan@kuma.ai"
    with django_assert_num_queries(3):
        user = method(email=email)

    assert str(user) == email
    assert user.is_superuser is is_superuser
    assert user.is_staff is is_staff
    assert user.is_ca is is_ca
    assert user.is_active is is_active
    assert user.default_organisation.ca_rights is is_ca


@pytest.mark.django_db
@pytest.mark.parametrize("superuser", [True, False])
def test_user_needs_email(superuser: bool) -> None:
    method = User.objects.create_superuser if superuser else User.objects.create_user
    with pytest.raises(ValueError, match="An email must be set"):
        method(email="")
