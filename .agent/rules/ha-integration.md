---
trigger: always_on
---

# Home Assistant integration conventions

The integration is a HACS custom component. It follows Home Assistant's config-entry architecture. YAML configuration is not added. `CONFIG_SCHEMA` stays `config_entry_only_config_schema`.

## Manifest and HACS

- `manifest.json` `domain` matches the package directory name.
- `config_flow` stays `true`.
- `iot_class` is honest. Use `local_polling` or `local_push` only when the feature works with no cloud account. A single cloud-only path means the class stays `cloud_polling` until the council accepts a split.
- `requirements` lists every third-party import. Versions are pinned with a lower bound when behavior or a fix depends on it. Unbounded ranges and URL dependencies are forbidden.
- `version` in the manifest is the integration version. Any second copy (a constant in the device core) is updated in the same commit. Do not let them drift. Collapsing them to one source is a dedicated change, not a drive-by.
- `hacs.json` `homeassistant` is the minimum version that was actually tested. Raising it is a breaking change: say so in the pull request, and do not raise it "to use a newer helper" when the current floor already provides one.
- Documentation and issue-tracker URLs change only in a pull request whose purpose is the move. Do not retarget them while editing unrelated code.
- The HACS zip contains the integration package and nothing else. Tests, `.agent`, and workflows stay outside `custom_components/`.

## Config flow

- Subclass `ConfigFlow`. Set `VERSION`. A storage-format change increments `VERSION` and implements `async_migrate_entry`. Shipping a format change without the migration fails review.
- Call `async_set_unique_id` with the stable device id (MAC or vendor device id, already normalized) before creating an entry, and abort if that id is already configured. Discovery may update the host of an existing entry. It must not create a second entry for the same vacuum.
- User mistakes return `errors` / abort reasons whose keys exist under the flow in `strings.json`.
- Credentials are written into the config entry data. Preferences the user can change later are options, edited through an options flow. Do not ask the user to delete and re-add the device to change a preference.
- Re-authentication uses a reauth step on the existing entry. It does not create a parallel entry.
- The flow does not import platform modules.

## Coordinator and device registry

- One coordinator per config entry, constructed in `async_setup_entry`, removed in `async_unload_entry`.
- One Home Assistant device per vacuum. Identifiers are stable across restarts and across host changes. Connections include the normalized MAC when one is known.
- `sw_version`, model, and manufacturer come from the device core. They are not a place to stash a token or an account email.

## Entities

- Repeated entities use a description object and a single entity class. Copy-pasted entity classes that differ by a constant are a defect.
- `unique_id` follows `.agent/rules/naming.md`. Changing a scheme requires an entity-registry migration in the same release and a council record. Home Assistant does not recover history for an orphaned `unique_id`.
- Names and icons that the integration owns come from a `translation_key` in `strings.json`. A hardcoded English `_attr_name` is allowed only for a name the device itself supplied.
- `available` is false when the coordinator's last update failed or when the device core reports the feature as unavailable. Do not leave a switch looking actionable against an offline vacuum.
- Entity attributes are an explicit, documented set. Spreading the raw device dict into `extra_state_attributes` is forbidden: it bloats the recorder and leaks protocol fields the user did not ask to store.
- An entity that exists only for some capabilities must remove its stale registry entry when the capability is gone, addressed by `unique_id` or translation key, not by matching a display name.
- Disable-by-default (`entity_registry_enabled_default = False`) is for diagnostic noise, not for hiding a feature the integration failed to model.

## Services and events

- Every service is declared in `services.yaml`, described in `strings.json`, and registered with a voluptuous schema that matches the YAML field for field. A field present in only one of the three is a review failure.
- Service handlers check that the targeted entity belongs to this integration before acting.
- Events carry a typed, documented payload. Payload keys are stable. A new key is optional for one release if listeners may not know it; removing a key is a breaking change and needs the council.
- Do not register services inside `async_setup_entry`. Services are domain-level, registered once, and they look up the coordinator from `hass.data`.

## Diagnostics

- `diagnostics.py` redacts every field listed in `.agent/rules/security.md` before returning data.
- A new state field that can identify a household, a home's floor plan, or an account is added to the redaction list in the same pull request.

## Quality bar specific to Home Assistant

- hassfest and the HACS action are part of done for any change to the manifest, `hacs.json`, `strings.json`, services, or the platform list. Local `/gate` does not replace them.
- Do not vendor a chunk of Home Assistant core. If a helper exists at the current minimum version, use it.
- Do not reach into private Home Assistant modules (`homeassistant.components.*.` private names, underscore helpers) when a public helper exists. A private import needs a comment naming the public API that is missing and the minimum version that will remove the import.
