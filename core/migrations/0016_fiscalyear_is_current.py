from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_approval_process_engine"),
    ]

    operations = [
        migrations.AddField(
            model_name="fiscalyear",
            name="is_current",
            field=models.BooleanField(default=False),
        ),
    ]
