---
trigger: always_on
---

# Naming

Names are English, descriptive, and stable once they are part of a Home Assistant surface.

## Python

- Packages and modules: `snake_case`. No `utils`, `helpers`, `misc`, or `common`.
- Classes and exceptions: `PascalCase`. Exceptions end in `Error` (shell, Home Assistant types) or `Exception` (device core, matching the existing core hierarchy — pick the suffix the layer already uses, and do not invent a third).
- Functions and methods: `snake_case`.
- A coroutine's name starts with `async_`. A function decorated with Home Assistant's `@callback` is synchronous and must not use that prefix.
- Constants and config-entry keys: `UPPER_SNAKE_CASE`. Keys persisted in a config entry are prefixed `CONF_` and live in the shell constant module.
- Type variables: `PascalCase`, short (`CoordinatorT`), not `T1`.
- Booleans start with `is_`, `has_`, `should_`, or `can_`. A boolean named `status`, `flag`, or `check` fails review.
- Private helpers and module-private constants start with a single underscore. Name mangling (`__name`) is forbidden.

## Wire values and models

- Enum members name the semantic state (`SWEEPING`), not the wire integer (`STATE_5`) and not the marketing sentence.
- A model record is keyed by the stable model code the device reports, not by a display name that vendors localize.
- Display names, including room names that come from the device, are data. They are never part of a `unique_id`, a service name, or a translation key.

## Home Assistant surfaces

These names, once released, are a migration to change:

- The integration domain.
- Service names and service field names.
- Event names and event payload keys.
- Entity `unique_id`s and device-registry identifiers.
- Config-entry keys and options keys.
- Translation keys that existing entity registry entries store.

A new entity's `unique_id` is the config entry id plus a stable key chosen from the capability or the device-supplied room id. It is not the translated name, the entity id, a list index, or a Python class name.

## Tests

- Files are `test_<module>.py` under `tests/`, mirroring the package path.
- Functions are `test_<behavior>_<condition>`, for example `test_sweeping_state_decodes_when_status_code_is_cleaning`.
- Fixtures are named for the value they return (`vacuum_device`), not `fixture`, `data`, or `mock`.
