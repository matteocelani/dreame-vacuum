---
trigger: manual
---

# /add-device

**Triggers:** `/add-device`, "add a model", "support this vacuum".

Adds one model to an existing device family. A new family, a new transport, or a new integration domain is not this command. Stop and run `/council`.

## Preconditions

- The model code is the code the device reports, not a marketing name. The task states that code.
- The family package already exists. Today that is the Dreame protocol family.
- The behavior the model needs is expressible as capability data: properties, actions, and feature flags. If the model needs a new wire exchange, this command still applies, but the exchange is device-core code with a test, not a branch in a platform module.
- No config-entry key, entity `unique_id` scheme, or service schema has to change. If one does, stop and run `/council`.

## Steps

1. Read `AGENTS.md`, `.agent/rules/architecture.md`, `.agent/rules/typing.md`, `.agent/rules/tests.md`, and `.agent/rules/security.md`.
2. Find the single capability table the family already uses. Edit that table. Do not open a second table for one model.
3. Add the model code once. List the properties, actions, and features it exposes. Reuse existing enum members. A new wire code is a new enum member with the vendor's numeric or string value, named for the semantic state.
4. Search the shell for comparisons against model names or product codes. Do not add one. If the feature cannot be reached through a capability predicate, the design is wrong: extend the capability record, or stop and run `/council`.
5. If the user will see a new label, add the English key to `strings.json`. Do not hardcode the label in a platform module.
6. Add a device-core test that loads the record for this model code and asserts one real decode or state transition. Use fake credentials and no network.
7. Run `/gate`, then `/review`.

## Done

- The model code appears in exactly one capability record.
- No platform module, entity, or service handler gained a model-string comparison.
- The device core still does not import `homeassistant`.
- A test covers the new record and one behavior, and `/review` reports PASS.
- The pull request names the model code and the capabilities it turned on.

## NEVER

- Copy a neighboring model and hope the flags are close enough. Unverified flags are how the wrong switch appears for a real robot.
- Commit a packet capture, a token, a cloud response, or a map from hardware.
- Start a domain rename, a second family package, or a dependency add inside this change.
- Refactor the inherited integration while adding the row.
