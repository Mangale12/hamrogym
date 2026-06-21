from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app_registry", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TenantDB",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("db_name", models.CharField(max_length=100, unique=True)),
                ("db_user", models.CharField(max_length=100)),
                ("db_password", models.CharField(max_length=200)),
                ("db_host", models.CharField(default="127.0.0.1", max_length=200)),
                ("db_port", models.CharField(default="3306", max_length=10)),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("suspended", "Suspended"), ("expired", "Expired"), ("trial", "Trial")],
                        default="trial",
                        max_length=20,
                    ),
                ),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="tenant_dbs",
                        to="app_registry.client",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tenant DB",
                "verbose_name_plural": "Tenant DBs",
                "ordering": ["db_name"],
                "db_table": "app_registry_tenant_dbs",
            },
        ),
    ]
