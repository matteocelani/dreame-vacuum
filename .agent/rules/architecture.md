---
trigger: always_on
---

# Architecture

These rules decide where a change is allowed to live. A review that finds a violation here fails the change even when the behavior is correct.

## Two layers

- The **shell** is the Home Assistant integration package at `custom_components/<domain>/`. It may import `homeassistant`. It owns lifecycle, flows, the coordinator, platforms, entities, services, diagnostics, translations, and the manifest.
- The **device core** is the pure-Python code that talks to a vacuum. It must not import `homeassistant`, `voluptuous`, or any other Home Assistant helper. It must be importable by pytest with only the manifest's third-party requirements installed.

A file that imports `homeassistant` and also parses a wire payload, decodes a map, or builds a cloud request is in the wrong layer. Split it. The shell calls the core. The core never calls the shell.

## Families

- One device family is one package inside the integration package. Dreame (including the MOVA, Mijia, and TROUVER transports that share its protocol) is the family that exists today.
- A new family is a sibling package. It is not a mode flag inside the existing family. Adding a family is a council decision.
- Family packages must not import each other. Shared code moves to a neutral package that also does not import `homeassistant`, in the same change that creates the second caller.
- Do not create that neutral package, or an empty family package, in advance.

## What the shell may know

- Platform modules declare entities. They read a facade the family publishes for the shell, and they call coordinator methods. They do not encode property ids, action ids, or map bytes.
- The entity base translates core failures into Home Assistant errors. It does not reimplement device rules.
- The coordinator is the only shell object that holds the live device object and the only object that polls or subscribes.
- Config flow collects credentials and options. It does not construct entities, and it does not keep a long-lived device connection after the flow finishes.

## Models are data

- Support for a model is a capability record: the properties, actions, and features that model exposes.
- Call sites ask the device or the capability record. A comparison against a model name, product code, or marketing string inside a platform module, an entity, or a service handler is forbidden.
- One model has one record. Do not duplicate a record to special-case a single entity.

## Placement

- Used by one module: keep it in that module.
- Used by one family: keep it in that family.
- Used by two families: promote it in the pull request that adds the second use.
- Used only by tests: it belongs under `tests/`, not in the integration package.

## Domain identity

- The integration domain is a single constant defined once and imported everywhere else.
- Inside the integration package, imports are package-relative (see `.agent/rules/imports.md`). An absolute import that spells today's domain name is forbidden, because the planned rename would have to edit every such line.
- Repository files outside the package (tests, workflows) may import `custom_components.<domain>` using the manifest's current domain. When the domain changes, those imports change in the rename pull request, not before.

## Boundaries that require the council

Stop and convene the council before:

- adding a package at the integration root, or a new top-level directory in the repository;
- introducing a facade, a registry, or a plugin mechanism intended for more than the family that exists;
- moving a module between the shell and the device core;
- renaming the domain or splitting the integration into two HACS components.

## Forbidden

- A `utils` module with no domain. Name the concept (`map_geometry`, `cloud_session`) or inline the helper.
- Re-exporting Home Assistant types from the device core "for convenience".
- Importing a platform module from the device core, the coordinator, or another platform module. Platforms are leaves.
- Caching a `HomeAssistant` instance, a config entry, or an entity on a device-core object.
