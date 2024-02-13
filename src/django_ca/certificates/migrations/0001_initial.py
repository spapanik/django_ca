import pyutilkit.date_utils

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Server",
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
                ("common_name", models.CharField(max_length=2047, unique=True)),
                (
                    "organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="certificates",
                        to="accounts.organisation",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="certificates",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Key",
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
                ("private_key", models.CharField(max_length=3272)),
                (
                    "server",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="certificates.server",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Certificate",
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
                ("self_signed", models.BooleanField(default=False)),
                ("csr", models.TextField()),
                ("certificate", models.TextField()),
                (
                    "server",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="certificates.server",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ServerName",
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
                ("name", models.CharField(max_length=2047)),
                (
                    "server",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="alternative_names",
                        to="certificates.server",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("server", "name"), name="unique_server_name"
                    )
                ],
            },
        ),
    ]
