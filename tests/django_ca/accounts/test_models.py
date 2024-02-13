from collections.abc import Callable
from typing import Any

import pytest

from django_ca.accounts.models import User


@pytest.mark.django_db
@pytest.mark.parametrize("superuser", [True, False])
def test_user_created(
    superuser: bool, django_assert_num_queries: Callable[[int], Any]
) -> None:
    email = "carl.sagan@kuma.ai"
    method = User.objects.create_superuser if superuser else User.objects.create_user
    with django_assert_num_queries(3):
        user = method(email=email)

    assert user.is_active is True
    assert str(user) == email


@pytest.mark.django_db
@pytest.mark.parametrize("conflicting_attribute", ["is_staff", "is_superuser"])
def test_superuser_is_staff_and_superuser(conflicting_attribute: str) -> None:
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            email="carl.sagan@kuma.ai",
            **{conflicting_attribute: False},  # type: ignore[arg-type]
        )


@pytest.mark.django_db
@pytest.mark.parametrize("superuser", [True, False])
def test_user_needs_email(superuser: bool) -> None:
    method = User.objects.create_superuser if superuser else User.objects.create_user
    with pytest.raises(ValueError):
        method(email="")
