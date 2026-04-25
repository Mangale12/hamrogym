# People Module

`nepanest.modules.people` is the workforce master-data boundary inside the
modular nepanest architecture.

It currently acts as a staged facade over the legacy `nepanest.modules.human_resources`
implementation so new code can depend on the modular namespace first.

Primary ownership:

- employees and employee profile sub-records
- departments and designations
- teams and team roles
- employment types
- workforce-facing selectors and navigation

Boundary notes:

- attendance-specific workflows still live in `nepanest.modules.attendance`
- leave, payroll, loans, recruitment, and policies stay in their own modules
- `nepanest.modules.human_resources` remains the aggregate compatibility app

Migration rule:

- new imports should prefer `nepanest.modules.people.*`
- legacy `nepanest.modules.human_resources.*` remains the backing implementation until models,
  routes, and views are fully split by module
