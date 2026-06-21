from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.db import connections
from django.test import SimpleTestCase

import core.management.commands.erp as erp_module
from core.management.commands.erp import Command, DatabaseChoice


class ErpCommandTests(SimpleTestCase):
    def test_ensure_database_alias_registers_server_only_database(self):
        with patch.object(
            erp_module,
            "settings",
            SimpleNamespace(
                DATABASES={
                    "default": {
                        "ENGINE": "django.db.backends.mysql",
                        "NAME": "db_erp_registry",
                        "USER": "root",
                        "PASSWORD": "secret",
                        "HOST": "127.0.0.1",
                        "PORT": "3306",
                    }
                }
            ),
        ), patch.dict(connections.databases, {}, clear=True):
            command = Command()
            choice = DatabaseChoice(alias="db_erp_sample", name="db_erp_sample")

            ensured = command._ensure_database_alias(choice)

            self.assertEqual(ensured, choice)
            self.assertIn("db_erp_sample", erp_module.settings.DATABASES)
            self.assertIn("db_erp_sample", connections.databases)
            self.assertEqual(erp_module.settings.DATABASES["db_erp_sample"]["NAME"], "db_erp_sample")

    def test_available_databases_are_discovered_from_mysql_server(self):
        with patch.object(
            erp_module,
            "settings",
            SimpleNamespace(
                DATABASES={
                    "default": {
                        "ENGINE": "django.db.backends.mysql",
                        "NAME": "db_erp_registry",
                        "USER": "root",
                        "PASSWORD": "secret",
                        "HOST": "127.0.0.1",
                        "PORT": "3306",
                    },
                    "hamrogym": {
                        "ENGINE": "django.db.backends.mysql",
                        "NAME": "db_erp_hamrogym",
                        "USER": "root",
                        "PASSWORD": "secret",
                        "HOST": "127.0.0.1",
                        "PORT": "3306",
                    },
                }
            ),
        ), patch.dict(connections.databases, {}, clear=True):
            cursor = MagicMock()
            cursor.fetchall.return_value = [
                ("db_erp_hamrogym",),
                ("db_erp_registry",),
                ("db_erp_sample",),
            ]
            connection = MagicMock()
            connection.cursor.return_value = cursor

            with patch("core.management.commands.erp.Command._load_mysql_driver") as mocked_driver_loader:
                mocked_driver_loader.return_value = SimpleNamespace(connect=MagicMock(return_value=connection))

                command = Command()
                databases = command._available_databases()

            self.assertEqual(
                databases,
                [
                    DatabaseChoice(alias="hamrogym", name="db_erp_hamrogym"),
                    DatabaseChoice(alias="default", name="db_erp_registry"),
                    DatabaseChoice(alias="db_erp_sample", name="db_erp_sample"),
                ],
            )
