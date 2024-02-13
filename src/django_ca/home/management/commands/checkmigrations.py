from collections import defaultdict

from django.conf import settings
from django.core.management.base import CommandError, CommandParser
from django.db.migrations.loader import MigrationLoader

from django_ca.home.management.commands.makemigrations import Command as MakeMigrations
from django_ca.lib.utils import hash_migrations


class Command(MakeMigrations):
    help = "Check if migrations are as expected"

    def add_arguments(self, parser: CommandParser) -> None:
        pass

    @staticmethod
    def check_hashes() -> None:
        actual_hashes = hash_migrations()
        with settings.MIGRATION_HASHES_PATH.open() as file:
            saved_hashes = [line.strip() for line in file.readlines()]
        if actual_hashes != saved_hashes:
            msg = "Migration hashes have changed!"
            raise CommandError(msg)

    @staticmethod
    def check_naming() -> None:
        loader = MigrationLoader(None, ignore_no_migrations=True)
        nodes = loader.graph.nodes
        app_migrations = defaultdict(list)
        for node in nodes:
            try:
                migration_number = int(node[1].lstrip("0").split("_")[0])
            except (IndexError, ValueError) as exc:
                msg = f"Migration {node[1]} has an invalid name"
                raise CommandError(msg) from exc
            app_migrations[node[0]].append(migration_number)

        for app_name, migration_numbers in app_migrations.items():
            n = len(migration_numbers)
            if len(set(migration_numbers)) != n:
                msg = f"Two migrations in {app_name} have the same prefix"
                raise CommandError(msg)
            migration_numbers.sort()
            if migration_numbers[-1] != n:
                msg = f"There is a skipped prefix in {app_name}"
                raise CommandError(msg)

    def handle(self, *args: object, **options: object) -> None:
        options["check_changes"] = True
        options["dry_run"] = True
        options["interactive"] = False
        options["merge"] = False
        options["empty"] = False
        options["name"] = ""
        options["include_header"] = False
        options["scriptable"] = False
        options["update"] = False
        try:
            super().handle(*args, **options)
        except SystemExit as exc:
            msg = "There are model changes not reflected in migrations"
            raise CommandError(msg) from exc
        self.check_naming()
        self.check_hashes()
