# nepanest ERP Folder Structure

This project is growing into a large ERP platform.

The goal is:

- `nepanest` = company namespace and reusable ERP engine
- `HamroGym` = one sellable product/domain built on top of nepanest shared modules
- product-specific code should stay separate from reusable ERP modules
- technical utilities should not be mixed with business/domain models

## Recommended Top-Level Structure

```text
hamrogym/
├── manage.py
├── config/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── prod.py
│   │   └── test.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── nepanest/
│   ├── common/
│   │   ├── mixins/
│   │   ├── helpers/
│   │   ├── middlewares/
│   │   ├── utils/
│   │   ├── validators/
│   │   └── management/
│   ├── foundation/
│   │   ├── parties/
│   │   ├── organization/
│   │   ├── geography/
│   │   ├── approvals/
│   │   ├── fiscal/
│   │   └── masterdata/
│   ├── modules/
│   │   ├── accounting/
│   │   ├── finance/
│   │   ├── billing/
│   │   ├── assets/
│   │   ├── people/
│   │   ├── payroll/
│   │   ├── recruitment/
│   │   ├── leave/
│   │   ├── attendance/
│   │   ├── projects/
│   │   └── tasks/
│   ├── platform/
│   │   ├── tenancy/
│   │   ├── subscriptions/
│   │   ├── licensing/
│   │   ├── branding/
│   │   └── app_registry/
│   └── products/
│       ├── hamrogym/
│       │   ├── members/
│       │   ├── plans/
│       │   ├── trainers/
│       │   ├── classes/
│       │   ├── checkins/
│       │   ├── dashboard/
│       │   └── urls.py
│       └── ...
├── templates/
├── static/
├── media/
├── docs/
└── requirements/
```

## Directory Responsibilities

### `nepanest/common`

Keep only technical/shared framework code here:

- mixins
- base helpers
- middleware
- validators
- utility functions
- management commands

Do not keep business models here.

### `nepanest/foundation`

Keep core ERP master entities here. These are reused by many modules:

- party, customer, vendor, supplier
- organization, branch, brand
- country, state, location
- fiscal year, currency
- approval engine
- shared master data

This layer is stable and should be reusable by every product.

### `nepanest/modules`

Keep reusable business modules here:

- accounting
- finance
- billing
- assets
- people/hr
- payroll
- recruitment
- leave
- attendance
- projects
- tasks

These modules should work for many domains, not only gym.

### `nepanest/platform`

Keep platform-level SaaS features here:

- tenant management
- subscription plans
- product licensing
- white-label branding
- customer/app provisioning

This is important if nepanest will generate multiple apps/domains from the same engine.

### `nepanest/products`

Keep domain-specific sellable apps here:

- `hamrogym`
- future products like school, hospital, restaurant, retail, etc.

Only product-specific workflows should live here.

## Current Project To Future Mapping

### Shared technical code

Current:

- `core/helpers`
- `core/middlewares`
- `core/mixins`
- `core/utils`
- `core/validators`
- `core/management`

Move to:

- `nepanest/common/...`

### Foundation apps

Current `core/models` should be split into proper apps instead of staying inside `core`.

#### `nepanest/foundation/parties`

Move:

- `core/models/party.py`
- `core/models/party_role.py`
- `core/models/party_type.py`

Why:

- party is a shared ERP entity used by finance, billing, assets, CRM, vendor, supplier, and customers

#### `nepanest/foundation/organization`

Move:

- `core/models/organization.py`
- `core/models/organization_settings.py`
- `core/models/branch.py`
- `core/models/brand.py`
- `core/models/erp_entity.py`

Why:

- organization structure is a platform-wide dependency

#### `nepanest/foundation/geography`

Move:

- `core/models/country.py`
- `core/models/state.py`
- `core/models/location.py`
- `core/models/location_type.py`

Why:

- geography is shared reference data

#### `nepanest/foundation/fiscal`

Move:

- `core/models/fiscal_year.py`
- `core/models/curency.py`

Why:

- these are core accounting and cross-module references

#### `nepanest/foundation/approvals`

Move:

- `core/models/approval_entities.py`
- `core/models/approval_workflow.py`

## Current Implemented ERP Map

The repo now follows this ERP split in code, not only in planning:

- `nepanest/common`
  - shared helpers, mixins, middleware, validators, upload/date utilities
- `nepanest/foundation`
  - `parties`
  - `organization`
  - `geography`
  - `fiscal`
  - `approvals`
- `nepanest/modules`
  - `accounting`
  - `finance`
  - `billing`
  - `assets`
  - `human_resources`
    - `people`
    - `recruitment`
    - `leave`
    - `attendance`
    - `payroll`
    - `loans`
    - `policies`
  - `projects`
  - `tasks`
- `nepanest/platform`
  - `tenancy`
  - `subscriptions`
  - `licensing`
  - `branding`
  - `app_registry`
- `nepanest/products`
  - `hamrogym`

## Compatibility Strategy

To keep migrations and existing imports stable during the refactor, two compatibility layers still exist:

- `core`
  - now mainly acts as a legacy bridge while foundation/common code lives in `nepanest`
- `nepanest/modules/human_resources`
  - now acts as a compatibility shell over the HR capability modules

This is intentional. It lets the ERP architecture become clean first, without breaking existing forms, migrations, or app labels.

## Ready For Product Layer

At this point, the reusable ERP side is strong enough to start product work under `nepanest/products/hamrogym`.

Recommended product rule:

- if a feature is reusable across many businesses, keep it in `nepanest/modules`
- if a feature is gym-specific, keep it in `nepanest/products/hamrogym`
- if a model is master/reference data used by many modules, keep it in `nepanest/foundation`

Why:

- approval should be a reusable engine, not an HR-only concern

### Reusable business modules

#### `nepanest/modules/accounting`

Current:

- `nepanest/modules/accounting`

Keep here:

- chart of accounts
- ledgers
- journal entries
- voucher types
- financial reports

Rename suggestion:

- `account` -> `accounting`

#### `nepanest/modules/finance`

Current:

- `nepanest/modules/finance`

Keep here:

- tax
- discounts
- rounding
- payments
- credits
- payment methods

#### `nepanest/modules/billing`

Current:

- `nepanest/modules/billing`

Keep here:

- billing profile
- invoice/billing documents
- bill items

#### `nepanest/modules/assets`

Current:

- `nepanest/modules/assets`

Keep here:

- asset registry
- assignment
- maintenance
- depreciation
- status/condition/type/category

#### `nepanest/modules/tasks`

Current:

- `nepanest/modules/tasks`

Split into:

- `nepanest/modules/projects`
- `nepanest/modules/tasks`

Why:

- project portfolio and task execution usually grow differently in large ERPs

Suggested split:

- `project.py` -> `projects`
- `task.py`, `checklist.py`, `task_status.py`, `task_type.py`, `task_module.py`, `task_label.py` -> `tasks`

#### HR should not remain one giant app

Current:

- `nepanest/modules/human_resources`

Recommended split:

- `nepanest/modules/people`
- `nepanest/modules/recruitment`
- `nepanest/modules/attendance`
- `nepanest/modules/leave`
- `nepanest/modules/payroll`

Suggested mapping:

##### `people`

- employee
- employee profile
- employee contact
- employee address
- employee bank
- employee legal
- employee work
- employee emergency
- department
- designation
- team
- team role
- employment type
- shift
- employee shift

##### `recruitment`

- applicant
- job posting
- job requisition
- job position
- hiring plan
- interview
- interview stage
- job offer
- hire
- job category
- job skill
- skill level

##### `attendance`

- attendance
- attendance adjustment
- holiday calendar
- holiday
- weekly off rule
- overtime request
- overtime record

##### `leave`

- leave type
- leave policy
- leave balance
- leave accrual
- leave ledger
- leave request

##### `payroll`

- salary component
- salary structure
- payroll run
- payroll approval
- payslip
- provident fund
- SSF contribution
- tax slab
- employee tax declaration
- payroll settings
- report templates
- loan models if loans are HR payroll-linked

### Product-specific app

Current:

- `nepanest/products/hamrogym`

Move to:

- `nepanest/products/hamrogym`

Keep here only:

- gym dashboard
- memberships
- plans/packages
- member check-ins
- trainer assignment
- class scheduling
- gym billing rules specific to the gym business

Do not keep general ERP entities here.

## Recommended Naming Rules

- use lowercase package names
- prefer full names over short names
- avoid overloaded names like `core`, `models.py`, `utils.py` for business-heavy code
- keep one module per business domain
- let app names describe the bounded context

Examples:

- `account` -> `accounting`
- `hr` -> split by business capability
- `core` -> only technical/common code, or remove completely after migration

## Settings Structure

Current:

- `config/settings.py`

Recommended:

```text
config/settings/
├── __init__.py
├── base.py
├── local.py
├── prod.py
└── test.py
```

Purpose:

- `base.py` for shared settings
- `local.py` for development
- `prod.py` for deployment
- `test.py` for CI/tests

## URL Structure

Current routing mixes product and shared modules directly in one file.

Recommended pattern:

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("nepanest.products.hamrogym.urls")),
    path("erp/accounting/", include("nepanest.modules.accounting.urls")),
    path("erp/finance/", include("nepanest.modules.finance.urls")),
    path("erp/assets/", include("nepanest.modules.assets.urls")),
    path("erp/people/", include("nepanest.modules.people.urls")),
    path("erp/tasks/", include("nepanest.modules.tasks.urls")),
]
```

Benefits:

- product entrypoint stays separate
- reusable ERP modules have stable URLs
- future products can plug in cleanly

## How `INSTALLED_APPS` Should Evolve

Example target shape:

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "nepanest.foundation.organization",
    "nepanest.foundation.parties",
    "nepanest.foundation.geography",
    "nepanest.foundation.fiscal",
    "nepanest.foundation.approvals",

    "nepanest.modules.accounting",
    "nepanest.modules.finance",
    "nepanest.modules.billing",
    "nepanest.modules.assets",
    "nepanest.modules.people",
    "nepanest.modules.recruitment",
    "nepanest.modules.attendance",
    "nepanest.modules.leave",
    "nepanest.modules.payroll",
    "nepanest.modules.projects",
    "nepanest.modules.tasks",

    "nepanest.products.hamrogym",
]
```

## Migration Order

Do not move everything at once.

Recommended order:

1. Split settings into `base/local/prod/test`
2. Create `nepanest/common` and move technical helpers from `core`
3. Split `core/models` into `foundation` apps
4. Move `nepanest/modules/accounting` into its final modular ownership
5. Split `nepanest/modules/human_resources` into smaller modules
6. Split `nepanest/modules/tasks` into `projects` and `tasks`
7. Keep product code under `nepanest/products/hamrogym`
8. Add `platform` apps for tenancy/subscription/licensing

## Practical Rule For Future Development

Before creating any new model, ask:

1. Is this reusable across many products?
2. Is this a foundation entity used by many modules?
3. Is this platform-level SaaS logic?
4. Is this specific only to HamroGym?

Then place it in:

- `foundation` if it is a base ERP entity
- `modules` if it is a reusable business capability
- `platform` if it manages tenants/subscriptions/licensing
- `products/hamrogym` if it is gym-only

## Final Recommendation

For a very large complete ERP:

- keep `nepanest` as the reusable engine namespace
- keep `HamroGym` as one product under `products`
- break `core` apart
- break `hr` apart
- separate foundation entities from business modules
- plan for platform multi-tenant and subscription features early

This structure will scale much better than keeping everything in `core`, `hr`, and product apps mixed together.
