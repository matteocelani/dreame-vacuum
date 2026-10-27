---
trigger: manual
---

# /add-device

**Triggers:** `/add-device`, "add a model", "support this vacuum".

Adds one model to an existing device family. A new family, a new transport, or a new integration domain is not this command. Stop and run `/council`.

## Preconditions

- The model code is the code the device reports, not a marketing name. The task states that code.
- The family already exists. Dreame, MOVA, Mijia, and TROUVER share the Dreame base. A Xiaomi model uses the Xiaomi base in the sibling package. A new family is not this command.
- The behavior the model needs is expressible as capability data: properties, actions, and feature flags. If the model needs a new wire exchange, this command still applies, but the exchange is device-core code with a test, not a branch in a platform module.
- No config-entry key, entity `unique_id` scheme, or service schema has to change. If one does, stop and run `/council`.

## Steps

1. Read `AGENTS.md`, `.agent/rules/architecture.md`, `.agent/rules/typing.md`, `.agent/rules/tests.md`, `.agent/rules/security.md`, and council records 0001, 0002, and 0004.
2. Pick the base. Do not open a second table for one model.
   - Dreame, MOVA, Mijia, or TROUVER: one row in the Dreame catalog. `resolve_family` stays `None`. Mijia models reported as `xiaomi.vacuum.*` (`c102cn`, `c102gl`, `d103cn`, `d110ch`) stay on this base.
   - Xiaomi: register the model on `resolve_family`. Declare only property and action addresses the spec documents. Leave every other address unmapped. Flags come from `apply_capabilities`. A flag stays off until the address it reads is mapped. That includes wash-base, station cleaning, and lidar.
3. Add the model code once. Reuse existing enum members. A new wire code is a new enum member with the vendor's numeric or string value, named for the semantic state.
4. Search the shell for comparisons against model names or product codes. Do not add one. If the feature cannot be reached through a capability predicate or a mapped address, the design is wrong: extend the capability record, or stop and run `/council`.
5. If the user will see a new label, add the English key to `strings.json`. Do not hardcode the label in a platform module.
6. Add a device-core test that loads the record and asserts one real decode or state transition, plus the flags the base derives. Use fake credentials and no network. A Dreame test asserts the catalog row. A Xiaomi test asserts the derived flags and that an unmapped Dreame address is absent.
7. Run `/gate`, then `/review`.

## Done

- The model code appears in exactly one capability record on its base.
- No platform module, entity, or service handler gained a model-string comparison.
- The device core still does not import `homeassistant`.
- A test covers the new record and one behavior, and `/review` reports PASS.
- The pull request names the model code, the base, and the capabilities it turned on.

## NEVER

- Copy a neighboring model and hope the flags are close enough. Unverified flags are how the wrong switch appears for a real robot.
- Copy a Dreame capability row onto a Xiaomi model, or leave a Xiaomi model on the Dreame default property map.
- Commit a packet capture, a token, a cloud response, or a map from hardware.
- Start a domain rename, a second family package, a shared package, or a dependency add inside this change.
- Turn on map, room, or zone support for a Xiaomi model in this command. That is its own change.
- Refactor the inherited integration while adding the row.
