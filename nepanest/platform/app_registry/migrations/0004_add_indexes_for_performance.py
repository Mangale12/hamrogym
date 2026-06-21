# Generated migration to add database indexes for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_registry', '0003_alter_tenantdb_db_name_alter_client_table_and_more'),
    ]

    operations = [
        # Add indexes to License model for faster searches and sorting
        migrations.AddIndex(
            model_name='license',
            index=models.Index(fields=['client_id'], name='license_client_idx'),
        ),
        migrations.AddIndex(
            model_name='license',
            index=models.Index(fields=['plan'], name='license_plan_idx'),
        ),
        migrations.AddIndex(
            model_name='license',
            index=models.Index(fields=['is_current'], name='license_is_current_idx'),
        ),
        migrations.AddIndex(
            model_name='license',
            index=models.Index(fields=['expires_on'], name='license_expires_on_idx'),
        ),
        migrations.AddIndex(
            model_name='license',
            index=models.Index(fields=['client_id', 'is_current'], name='license_client_current_idx'),
        ),
        
        # Add indexes to LicenseRenewHistory model
        migrations.AddIndex(
            model_name='licenserenewhistory',
            index=models.Index(fields=['license_id'], name='license_history_license_idx'),
        ),
        migrations.AddIndex(
            model_name='licenserenewhistory',
            index=models.Index(fields=['renewed_at'], name='license_history_renewed_at_idx'),
        ),
        migrations.AddIndex(
            model_name='licenserenewhistory',
            index=models.Index(fields=['created_at'], name='license_history_created_at_idx'),
        ),
    ]
