import pyutilkit.date_utils

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import django_ca.accounts.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Organisation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=pyutilkit.date_utils.now, editable=False
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        default=pyutilkit.date_utils.now, editable=False
                    ),
                ),
                ("country", models.CharField(max_length=2)),
                ("province", models.CharField(max_length=255)),
                ("locality", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("ca_rights", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=pyutilkit.date_utils.now, editable=False
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        default=pyutilkit.date_utils.now, editable=False
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("is_ca", models.BooleanField(default=False)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
                (
                    "default_organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="users",
                        to="accounts.organisation",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
                "swappable": "AUTH_USER_MODEL",
            },
            managers=[
                ("objects", django_ca.accounts.models.UserManager()),
            ],
        ),
    ]
