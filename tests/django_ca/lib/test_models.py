import pytest

from django_ca.accounts.models import Organisation, User


class TestBaseModel:
    """Tests for the base model.

    The BaseModel is an abstract model, so we will test it
    via the user model.
    """

    @property
    def emails(self) -> set[str]:
        return {
            "user1@gmail.com",
            "user2@gmail.com",
            "user3@gmail.com",
        }

    @pytest.fixture(autouse=True)
    def _create_users(self) -> None:
        organisation = Organisation.objects.create(
            country="UK",
            province="England",
            locality="London",
            name="Ellipse Engineering Ltd",
            email="george.rastapopoulos@ellipse.com",
        )
        users = [
            User(
                email=email,
                is_superuser=False,
                is_staff=False,
                default_organisation=organisation,
            )
            for email in self.emails
        ]
        User.objects.bulk_create(users)

    @pytest.mark.django_db
    def test_bulk_create(self) -> None:
        assert User.objects.count() == 3

    @pytest.mark.django_db
    def test_random(self) -> None:
        assert User.objects.random().email in self.emails

    @pytest.mark.django_db
    def test_flat_values(self) -> None:
        assert set(User.objects.flat_values("email")) == self.emails

    @pytest.mark.django_db
    def test_update(self) -> None:
        User.objects.all().update(is_staff=True)
        assert User.objects.filter(is_staff=True).count() == 3

    @pytest.mark.django_db
    def test_bulk_update(self) -> None:
        users = []
        for user in User.objects.all():
            user.is_staff = True
            users.append(user)

        updated_users = User.objects.bulk_update(users, fields=["is_staff"])
        assert updated_users == 3
        assert User.objects.filter(is_staff=True).count() == 3
