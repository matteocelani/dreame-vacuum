---
trigger: always_on
---

# Module layout

Every new Python module is structured in this order. A module rewritten for a task adopts the order in the same change. A one-line edit does not reorder an inherited file.

1. Module docstring, one sentence, English.
2. `from __future__ import annotations`.
3. Imports, in the groups from `.agent/rules/imports.md`.
4. Module constants.
5. Types: type aliases, `TypedDict`s, frozen dataclasses, enums, protocols.
6. Public functions and classes.
7. Private helpers.

## Classes

- A class declares, in order: class variables and docstring, `__init__`, public methods, private methods.
- Home Assistant entity classes declare the `_attr_*` class attributes that do not depend on the device, then `__init__`, then the callbacks Home Assistant invokes (`async_added_to_hass`, state properties, action handlers).
- Do not mix entity classes into a device-core module, or protocol parsers into a platform module.

## Size

- A new module that covers two unrelated concepts is two modules. "Unrelated" means a reviewer cannot state one reason the file changes.
- Splitting is by concept (protocol, capability table, map geometry), not by visibility (`models.py` plus `models_internal.py`) and not to satisfy a line count.
- Platform modules stay declarative. When a platform module grows behavior, the behavior moves to the entity base or the device core, and the platform file keeps the description list and `async_setup_entry`.

## Package init

- A package init is either empty or a facade of explicit re-exports. It contains no business logic, no I/O, and no registration side effects.
- Setup side effects belong in `async_setup` / `async_setup_entry` of the integration package, nowhere else.

## Encoding

- UTF-8, LF line endings, a trailing newline, no trailing whitespace.
- No byte-order mark, no encoding cookie. The module docstring is not a place for a changelog.
