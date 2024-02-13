from collections import defaultdict

import pytest

from django.test import override_settings

from django_ca.lib import utils


@override_settings(BASE_APP_DOMAIN="192.168.1.128", BASE_APP_PORT=80)
@pytest.mark.parametrize(
    ("path", "kwargs", "expected"),
    [
        ("relative/path", {}, "http://192.168.1.128/relative/path"),
        ("/absolute/path", {}, "http://192.168.1.128/absolute/path"),
        (
            "relative/path",
            {"foo": "bar"},
            "http://192.168.1.128/relative/path?foo=bar",
        ),
    ],
)
def test_get_app_url(path: str, kwargs: dict[str, str], expected: str) -> None:
    assert utils.get_app_url(path, **kwargs).string == expected


def test_hash_migrations() -> None:
    hashed_migrations = defaultdict(list)
    for hashed_migration in utils.hash_migrations():
        app, name, _ = hashed_migration.split("::")
        hashed_migrations[app].append(name)
    assert "accounts" in hashed_migrations
    assert "0001_initial" in hashed_migrations["accounts"]
