from django.db import migrations, models


def seed_muscle_groups(apps, schema_editor):
    MuscleGroup = apps.get_model('hamrogym', 'MuscleGroup')
    MuscleGroup.objects.bulk_create([
        MuscleGroup(name='Chest', is_active=True, remarks='Chest muscles'),
        MuscleGroup(name='Back', is_active=True, remarks='Back muscles'),
        MuscleGroup(name='Legs', is_active=True, remarks='Leg muscles'),
        MuscleGroup(name='Arms', is_active=True, remarks='Arm muscles'),
        MuscleGroup(name='Shoulders', is_active=True, remarks='Shoulder muscles'),
        MuscleGroup(name='Core', is_active=True, remarks='Core muscles'),
        MuscleGroup(name='Full Body', is_active=True, remarks='Full body muscles'),
    ], ignore_conflicts=True)  # Safer for re-runs or existing data


class Migration(migrations.Migration):

    dependencies = [
        ('hamrogym', '0016_trainer_module'),
    ]

    operations = [
        migrations.CreateModel(
            name='MuscleGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('remarks', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],  # Only Meta options go here
            },
        ),
        # RunPython must be a separate operation AFTER the model is created
        migrations.RunPython(seed_muscle_groups, migrations.RunPython.noop),
    ]