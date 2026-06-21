from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("business_name", models.CharField(max_length=255)),
                ("client_code", models.CharField(max_length=50, unique=True)),
                ("contact_email", models.EmailField(max_length=254)),
                ("contact_phone", models.CharField(blank=True, max_length=30)),
                ("address", models.TextField(blank=True)),
                (
                    "plan",
                    models.CharField(
                        choices=[("starter", "Starter"), ("professional", "Professional"), ("enterprise", "Enterprise")],
                        default="starter",
                        max_length=30,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("suspended", "Suspended"), ("cancelled", "Cancelled"), ("trial", "Trial")],
                        default="trial",
                        max_length=20,
                    ),
                ),
                ("registered_on", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Client",
                "verbose_name_plural": "Clients",
                "ordering": ["-registered_on"],
                "db_table": "app_registry_clients",
            },
        ),
    ]
