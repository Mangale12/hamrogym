# Additional migration to add indexes on Client, TenantDB, and Subscription models

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_registry', '0004_add_indexes_for_performance'),
    ]

    operations = [
        # Add indexes to Client model
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['business_name'], name='client_business_name_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['client_code'], name='client_code_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['status'], name='client_status_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['plan'], name='client_plan_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['registered_on'], name='client_registered_on_idx'),
        ),
        
        # Add indexes to TenantDB model
        migrations.AddIndex(
            model_name='tenantdb',
            index=models.Index(fields=['client_id'], name='tenantdb_client_idx'),
        ),
        migrations.AddIndex(
            model_name='tenantdb',
            index=models.Index(fields=['db_name'], name='tenantdb_db_name_idx'),
        ),
        migrations.AddIndex(
            model_name='tenantdb',
            index=models.Index(fields=['status'], name='tenantdb_status_idx'),
        ),
        
        # Add indexes to Subscription model
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['client_id'], name='subscription_client_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['status'], name='subscription_status_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['interval'], name='subscription_interval_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['period_start', 'period_end'], name='subscription_period_idx'),
        ),
        
        # Add indexes to LoginHistory model
        migrations.AddIndex(
            model_name='loginhistory',
            index=models.Index(fields=['client_id'], name='loginhistory_client_idx'),
        ),
        migrations.AddIndex(
            model_name='loginhistory',
            index=models.Index(fields=['logged_in_at'], name='loginhistory_logged_in_at_idx'),
        ),
        migrations.AddIndex(
            model_name='loginhistory',
            index=models.Index(fields=['is_successful'], name='loginhistory_is_successful_idx'),
        ),
    ]
