import subprocess

from django.conf import settings
from django.core.management.base import CommandError, CommandParser
from django.core.management.commands.makemigrations import Command as MakeMigrations
from django.db.migrations import Migration
from django.db.migrations.writer import MigrationWriter

from django_ca.lib.utils import hash_migrations


class Command(MakeMigrations):
    help = "Creates new migration(s) for apps."

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)

    def handle(self, *args: object, **options: object) -> None:
        if not settings.DEBUG:
            msg = "Creating new migrations is only allowed in development"
            raise CommandError(msg)

        options["include_header"] = False
        super().handle(*args, **options)
        with settings.MIGRATION_HASHES_PATH.open("w") as file:
            for migration_hash in hash_migrations():
                file.write(f"{migration_hash}\n")

    def format_migration(self, migration: Migration) -> None:
        writer = MigrationWriter(migration, self.include_header)
        subprocess.run(["black", writer.path], check=True)  # noqa: S603,S607
        subprocess.run(  # noqa: S603
            ["ruff", "check", "--fix-only", writer.path], check=True  # noqa: S607
        )

    def write_migration_files(
        self,
        changes: dict[str, list[Migration]],
        update_previous_migration_paths: dict[str, str] | None = None,
    ) -> None:
        super().write_migration_files(changes, update_previous_migration_paths)
        if self.dry_run:
            return

        for app_label, app_migrations in changes.items():
            if self.verbosity >= 1:
                self.stdout.write(
                    self.style.MIGRATE_HEADING(
                        f"Reformatting migrations for '{app_label}':"
                    )
                )

            for migration in app_migrations:
                self.format_migration(migration)
