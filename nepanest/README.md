# nepanest Package Layout

This package is the long-term home for the reusable nepanest ERP engine.

The migration is intentionally staged:

- current live apps still run from staged lowercase locations and `core/...`
- new shared structure starts here under lowercase `nepanest/`
- future refactors should move code into this package gradually, module by module

High-level structure:

- `common`: technical shared utilities
- `foundation`: base ERP entities shared across modules
- `modules`: reusable business capabilities
- `platform`: SaaS tenancy and licensing concerns
- `products`: product-specific domain apps such as HamroGym
