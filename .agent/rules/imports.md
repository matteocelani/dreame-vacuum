---
trigger: always_on
---

# Imports

## Order

Every new or rewritten module orders imports in this exact sequence, with one blank line between groups and no blank line inside a group:

1. `from __future__ import annotations`
2. The standard library
3. Third-party packages (`numpy`, `pycryptodome`, `miio`, `paho.mqtt`, and the rest of the manifest)
4. `homeassistant` and `voluptuous` (shell modules only)
5. Package-relative imports

Ruff's isort settings in `.agent/rules/formatting.md` enforce this. Do not hand-sort against that contract.

## Relative imports

- Same-package imports are explicit and relative: `from .const import DOMAIN`, `from .dreame.device import DreameVacuumDevice`.
- Parent imports are forbidden. `from ..`, `from ...`, and any form that climbs out of the current package fail review. If a module needs a parent, it is in the wrong package, or the shared code belongs beside it (see `.agent/rules/architecture.md`).
- Absolute imports that name the integration (`custom_components.<domain>...`) are forbidden inside the integration package. Tests outside the package may use them.

## Banned forms

- `import *` and `from module import *`.
- A relative import written `import .const` or any other form Ruff does not treat as an explicit import list.
- Importing a platform module from anywhere except the integration's setup module, which forwards the platform list.
- Importing `homeassistant` from the device core.
- A lazy import inside a function. The only exception is an import cycle that cannot be broken by moving a shared type. The comment names both modules in the cycle. One exception per module. A second cycle means the modules are fused and must be split.
- An import of a package that is not in the standard library, the manifest `requirements`, or Home Assistant itself. A test-only dependency is declared in the project metadata, never imported "because CI has it".

## Facade

- Code outside a device family imports that family's public facade (the family's package init), not its internal modules.
- Code inside the family imports the defining module, not the facade. The facade must not become a cycle hub.
- A name is added to the facade only when a module outside the family uses it in the same change. Unused re-exports are dead code.
