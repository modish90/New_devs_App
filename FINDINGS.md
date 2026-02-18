# Property Revenue Dashboard - Findings

## Bugs Discovered and How They Were Found
1. Cross-tenant revenue leakage. I traced this by looking at the cache key and then logging in as Tenant A and Tenant B for the same property ID. The totals swapped after refresh.
2. Monthly totals were off for March, plus a timezone edge case. I compared the seed data (Feb 29, 23:30 UTC) to the March totals and saw it was excluded when it should count for Paris.
3. Cents-off precision drift. The schema stores `NUMERIC(10,3)` but the app was converting to float without a stable rounding step.
4. Backend always fell back to mock data. The logs showed `Database pool not available`, which explained why values looked “made up.”
5. UI property dropdown shows other-tenant properties. Logging in as Tenant B showed Tenant A property IDs in the dropdown.

## Root Cause of Each Issue
1. Cache key was only `revenue:{property_id}` and did not include `tenant_id`.
2. Month boundaries were computed without using the property’s timezone.
3. Aggregation and conversion used floats without consistent decimal quantization.
4. Async DB pool was misconfigured and `get_session()` was async but used as a context manager without awaiting.
5. Frontend property list is hardcoded and not tenant-aware.

## Fix for Each Problem
1. Cache key now includes tenant + property + period.  
File: `backend/app/services/cache.py`

2. Revenue queries now compute month boundaries in the property’s timezone and convert to UTC before querying.  
File: `backend/app/services/reservations.py`

3. Totals are quantized to 2 decimals with `Decimal` before returning.  
Files: `backend/app/services/reservations.py`, `backend/app/api/v1/dashboard.py`

4. DB pool uses async engine defaults and `get_session()` returns a session synchronously.  
File: `backend/app/core/database_pool.py`
