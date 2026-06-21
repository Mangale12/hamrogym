# Performance Optimization Summary for Licenses Endpoint

## Problem Identified
The `/registry/licenses/` endpoint was causing the Django server to crash due to excessive memory/resource usage. This was caused by inefficient database queries in the datatable view.

## Root Causes

### 1. Inefficient BaseDataTableView Implementation
**File**: `core/datatables/views.py`

**Issues**:
- **Double COUNT(*) queries**: Every request executed two full table scans:
  - One to count total records
  - One to count filtered records
- **No error handling**: Queries that took too long would crash without graceful degradation
- **Unoptimized search**: Multiple OR conditions on non-indexed fields
- **Missing timeout handling**: No protection against long-running queries

### 2. Missing Database Indexes
**Models affected**: License, Client, TenantDB, Subscription, LoginHistory

The search and ordering columns lacked database indexes, causing full table scans for every search/filter/sort operation.

### 3. N+1 Query Problem
The original `get_queryset()` didn't use `.only()` to limit fetched fields, causing unnecessary data transfer and memory usage.

## Solutions Implemented

### 1. Optimized BaseDataTableView
**Changes**:
- Added `get_count_safe()` method with error handling
- Added exception handling with logging
- Added timeout protection
- Improved memory efficiency

**Code location**: `/var/www/django_projects/hamrogym/core/datatables/views.py`

### 2. Optimized License Datatables
**Changes**:
- Added `.select_related("client")` for efficient JOINs
- Added `.only()` to fetch only necessary fields
- Updated `orderable_columns` from "client" to "client__business_name"

**Files**:
- `/var/www/django_projects/hamrogym/nepanest/platform/app_registry/datatables/license_data_table.py`
- `/var/www/django_projects/hamrogym/nepanest/platform/app_registry/datatables/client_data_table.py`
- `/var/www/django_projects/hamrogym/nepanest/platform/app_registry/datatables/tenant_db_data_table.py`
- `/var/www/django_projects/hamrogym/nepanest/platform/app_registry/datatables/subscription_data_table.py`

### 3. Database Indexes Added
**Migration 0004**: Indexes for License and LicenseRenewHistory
- License.client_id
- License.plan
- License.is_current
- License.expires_on
- License.(client_id, is_current) [composite index]
- LicenseRenewHistory.license_id
- LicenseRenewHistory.renewed_at
- LicenseRenewHistory.created_at

**Migration 0005**: Indexes for all other models
- Client: business_name, client_code, status, plan, registered_on
- TenantDB: client_id, db_name, status
- Subscription: client_id, status, interval, (period_start, period_end)
- LoginHistory: client_id, logged_in_at, is_successful

## Performance Improvements

### Before Optimization
- Every datatable request: 2x COUNT(*) queries on full table
- No field limiting: All model fields fetched from database
- Potential crashes on large datasets (1000+ records)
- Inefficient search queries without indexes

### After Optimization
- Error handling prevents crashes
- Efficient index-based queries
- Reduced data transfer with `.only()`
- Composite queries use most efficient JOINs
- Graceful error handling with logging

## Testing the Fix

To verify the performance improvement:

```bash
# Test the endpoint
curl http://127.0.0.1:8001/registry/licenses/

# Monitor database queries (enable Django debug toolbar or query logging)
# Check for indexes in database:
SHOW INDEX FROM app_registry_license;
SHOW INDEX FROM app_registry_client;

# Performance test with large dataset
python manage.py shell
>>> from nepanest.platform.app_registry.models import License
>>> License.objects.count()  # Should be fast with indexes
>>> # Try searching/filtering - should be instant
```

## Best Practices for Future Development

### 1. Always Use select_related() for ForeignKeys
```python
# Good
queryset = Model.objects.select_related('foreign_key_field')

# Bad - causes N+1 queries
queryset = Model.objects.all()
```

### 2. Always Use only() to Limit Fields
```python
# Good - fetch only needed fields
queryset = Model.objects.only('id', 'name', 'email')

# Bad - fetches all fields
queryset = Model.objects.all()
```

### 3. Create Indexes on Searchable/Orderable Columns
```python
# In models.py
class Meta:
    indexes = [
        models.Index(fields=['search_field'], name='search_idx'),
        models.Index(fields=['client_id', 'is_current'], name='composite_idx'),
    ]
```

### 4. Add Error Handling to Heavy Operations
```python
try:
    count = queryset.count()
except OperationalError:
    logger.error("Database timeout")
    return 0
```

## Related Files Modified
1. `/var/www/django_projects/hamrogym/core/datatables/views.py` - Base datatable view
2. `/var/www/django_projects/hamrogym/nepanest/platform/app_registry/datatables/license_data_table.py` - License table
3. `/var/www/django_projects/hamrogym/nepanest/platform/app_registry/datatables/client_data_table.py` - Client table
4. `/var/www/django_projects/hamrogym/nepanest/platform/app_registry/datatables/tenant_db_data_table.py` - TenantDB table
5. `/var/www/django_projects/hamrogym/nepanest/platform/app_registry/datatables/subscription_data_table.py` - Subscription table
6. `/var/www/django_projects/hamrogym/nepanest/platform/app_registry/migrations/0004_add_indexes_for_performance.py` - Database indexes
7. `/var/www/django_projects/hamrogym/nepanest/platform/app_registry/migrations/0005_add_more_indexes.py` - Additional indexes

## Monitoring and Maintenance

### Enable Django Query Logging
```python
# In settings/base.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Use django-extensions for Performance Analysis
```bash
pip install django-extensions
# Run queries and see execution time
python manage.py runserver --pdb-on-exception
```

### Monitor Index Usage
```sql
-- MySQL: Check if indexes are being used
EXPLAIN SELECT * FROM app_registry_license WHERE plan = 'starter';

-- Check index statistics
SHOW INDEX FROM app_registry_license;
```

## Conclusion
The `/registry/licenses/` endpoint should now be significantly faster and won't crash with large datasets. The optimizations follow Django ORM best practices and ensure scalability as data grows.
