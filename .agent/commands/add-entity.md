---
trigger: manual
---

# /add-entity

**Triggers:** `/add-entity`, "expose this as a sensor", "add a switch for".

Adds one Home Assistant entity for a capability the device core already exposes.

## Preconditions

- The value or action already exists on the device core, or `/add-device` has landed first.
- The Home Assistant platform (sensor, binary sensor, switch, button, number, select, vacuum, camera, time) is the right one. Do not put a writable control on a sensor, or a measurement on a switch.
- Adding a platform the integration does not have yet is in scope only when no existing platform can represent the feature. Say why in the pull request.

## Steps

1. Read `AGENTS.md`, `.agent/rules/ha-integration.md`, `.agent/rules/architecture.md`, `.agent/rules/typing.md`, `.agent/rules/async-ha.md`, and `.agent/rules/naming.md`.
2. Add one description to the existing description list for that platform. The existence predicate calls a capability check. It does not compare model names.
3. Set `unique_id` from the config entry id plus a stable key (capability key, or the device-supplied room id for a per-room entity). Do not use the display name, a list index, or a translated string.
4. Add the `translation_key` and its English strings to `strings.json` for the name and, when the platform needs them, state values. Skip a hardcoded `_attr_name` unless the name is supplied by the device.
5. If the entity writes to the vacuum, the handler calls the device core. Blocking work uses `hass.async_add_executor_job`. Failure raises `HomeAssistantError` with a translation key. The handler does not open its own socket and does not import the protocol module beyond the family facade.
6. Declare any new state attribute explicitly. Do not spread a protocol dict into attributes. If the attribute can identify a home or an account, redact it in diagnostics in the same change.
7. When the entity is dynamic, make sure a stale registry entry is removed by stable id when the capability disappears.
8. If this change adds a platform module, register it in the integration's platform list and in `async_setup_entry`'s forward list, and add the platform strings.
9. Add the test `/gate` requires: a device-core assertion if the predicate depends on new parsing, and a shell test if a new service, flow branch, or registry migration was introduced.
10. Run `/gate`, then `/review`.

## Done

- One description, one stable `unique_id` scheme, one `strings.json` entry.
- No new model-string branch, no new `homeassistant` import in the device core, no secret in attributes.
- `/review` reports PASS.
- The pull request says which platform, which capability key, and whether the entity is enabled by default.

## NEVER

- Change the `unique_id` of an existing entity in this command. That is a migration and a council decision.
- Create a new entity class per model.
- Register a service as a side effect. Services are `/council` if they add a schema, otherwise a separate change that updates `services.yaml`, the voluptuous schema, and `strings.json` together.
- Edit locale catalogs by hand for a single language as part of adding the entity.
