# 0004 — Where do the Dreame and Xiaomi capability bases live?

- Status: accepted
- Date: 2026-10-27
- Supersedes: none
- Superseded by: none

## Brief

**Question.** Where do two capability bases live, one for the Dreame family and one for the Xiaomi family, and how does a model select its base, so a new Xiaomi model declares only spec-backed property and action mappings plus the flags those mappings justify?

**Why now.** Council 0002 put `xiaomi.vacuum.b108gl` and `xiaomi.vacuum.d109gl` in the Dreame catalog by copying a Mijia Dreame capability list. Council 0003 then said not to re-derive those flags in that shipping change. The owner now wants the opposite for flags: the project stays Dreame-compatible, and adding a Xiaomi model must not inherit Dreame defaults or copy a Dreame row. The copied list still turns on `mop_pad_lifting`, `new_state`, `obstacles`, `auto_emptying`, `mopping_after_sweeping`, and `mop_clean_frequency` for both models. `self_wash_base` is not in that list today, but the inherited `xiaomi.vacuum.` block sets `station_cleaning` from `self_wash_base`, so a wash-base property read would show station and self-wash buttons. Official MIoT specs for these two models are already in `tests/xiaomi/specs/`. This record does not supersede 0003. It replaces only the sentence that forbade re-deriving capability flags. The 5.0 second Xiaomi property timeout, the 2 second shared miIO timeout, the parser guards, and the refusal of map, room, and zone support stay in force.

**Constraints.**

- Installed users. Domain stays `dreame_vacuum` (council 0001). No config-entry key, entity `unique_id`, device identifier, or service schema changes. `xiaomi.vacuum.c102gl`, `c102cn`, `d103cn`, and `d110ch` are Mijia Dreame robots. They stay on the Dreame base. A branch on the prefix `xiaomi.vacuum.` or on `capability.mijia` is still forbidden (council 0002).
- Home Assistant floor. `hacs.json` stays `2024.2.0`. No new runtime dependency.
- HACS. One integration. The Xiaomi package stays a sibling under `custom_components/dreame_vacuum/`. Families do not import each other. No new shared package and no new top-level directory.
- Secrets. No token, host, device id, or map dump in source, tests, or logs. The local token stays on the transport. The spec fixtures already in the tree stay free of credentials.
- Selection today. `resolve_family` returns a codec for `b108gl` and `d109gl` and `None` for every other model, including `c102gl`. `apply_family` installs explicit property and action maps and the local miIO transport before `capability.load` runs. Unmapped addresses are already omitted from those maps.

**Unknowns.**

- No robot is on this network. The spec files name services and addresses. They do not prove which Home Assistant entities a live S20+ or X20 Max should show.
- `AUTO_EMPTY_FREQUENCY` on `d109gl` is mapped. Whether its wire values match the Dreame `1x` / `2x` / `3x` select is not known. This decision does not switch that entity onto the Dreame auto-empty mode enum.
- Whether a later Xiaomi model has a real wash base. The spec files for these two models do not map `SELF_WASH_BASE_STATUS` or `START_WASHING`.

**Options.**

1. Keep both bases in the packages that already exist. The Dreame base is today's `capability.load` plus the full Dreame property and action maps, and it is what runs when the resolver returns `None`. The Xiaomi base is the explicit maps, the local miIO transport, and a fail-closed flag set on the Xiaomi codec. At the end of `capability.load`, if the device's codec is not `None`, the codec replaces the catalog bools with flags justified by that model's mapped names, then rebuilds `capability.list`. The catalog row stays so the flow still accepts the model. No new package. No storage change. Revert is a commit revert. Replaces only the flag sentence of 0003.
2. Add a shared package both families import, and rewrite Dreame `capability.load` to call it. Revert is a commit revert and does not move storage. The inherited Dreame path changes shape, so a mistake changes installed Dreame robots.
3. Remove `b108gl` and `d109gl` from `DEVICE_INFO` and select a second capability object in the shell by model string. Revert does not move storage. The flow rejects a model that is missing from the catalog. A second capability class duplicates the object the entities already read.
4. Do nothing. The copied capability list stays. A new Xiaomi model still inherits Dreame defaults, and a wash-base property read can still show station and self-wash buttons.

## Positions

### Architect

- Option: 1
- Owns: `custom_components/dreame_vacuum/xiaomi/` owns the Xiaomi base: explicit maps, value conversion, the local transport, and the flag derivation. `dreame/` owns the Dreame base and the three-line hook that calls `apply_capabilities` on the codec the shell already injected. The shell keeps owning resolver injection. Neither family imports the other. No shared package.
- Because: Option 2 is a shared framework whose Dreame caller would be a rewrite of the inherited load path. Option 3 is a second capability object with one caller, and it puts a model string in the shell. The codec method is not a plugin registry: Dreame does not look up a base by name, and a model with no codec stays on the catalog path. Hard-coding `dreame_vacuum` is not part of this option. A later family remains a sibling package with its own codec, not a condition inside Dreame.
- Cost: Dreame entities still render Xiaomi values, so a wrong derived flag still looks like a normal entity. The catalog row and the runtime flags disagree for these two models until load finishes.
- Would change my mind if: the two models used the Dreame siid/piid table and the Dreame value domain, so a catalog row was the whole base.

### Pragmatist

- Option: 1
- User impact: none for an already-configured Dreame, MOVA, Mijia, or TROUVER vacuum. Same config entry, same entities, same history. S20+ and X20 Max are not in a release; losing a copied switch is the fix, not a repair flow.
- Because: The user-visible hole is flags copied from a Dreame row. Clearing them does not need a new package, a storage migration, or a second device class. The hook does not run when the codec is `None`, so installed robots keep today's `capability.list`. A revert does not touch storage. I am deferring the ten-family picture to the Architect and the token handling to Security. The slice that lands now is the hook, the derivation, these two models, and a test that freezes a Dreame list and the `c102gl` list.
- Cost: The Dreame load function gains a codec call. A Xiaomi flag that the spec supports but the derivation table omits stays off until a later row names that address.
- Would change my mind if: `DreameVacuumDevice` cannot represent the Xiaomi base without a new config entry for a vacuum the user already added.

### Security

- Veto: no
- Option: 1
- Because: Option 1 adds no endpoint, no dependency, and no TLS change. Nothing new leaves the house. The token stays on the transport. Flag derivation reads mapped names, not property values, so it has nothing new to log. The spec fixtures are already in the tree and must stay free of tokens, hosts, and device ids. I will veto an implementation that logs a token, a property body, or a datagram, disables TLS, or commits a capture from a real robot to justify a flag. Option 2's rewrite is not a secret exposure. It is not the proposal I support.
- Cost: The safer call is the same awkward boundary as 0002: the Dreame device holds a codec it does not import. Diagnostics redaction is unchanged.
- Would change my mind if: the flags cannot be derived without logging a property value or without a new parser dependency.

### Home Assistant conventions

- Option: 1
- HA surface: none. The coordinator, the flow, and the entity registry stay as they are. Which entities exist still follows capability flags and mapped properties, which is the surface these two models already use.
- Because: Config-entry identity, `unique_id`s, device identifiers, `services.yaml`, and `strings.json` stay put. One coordinator per entry. `iot_class` stays `cloud_polling`. The floor stays `2024.2.0`. No new flow error and no new entity name, so no new translation key. hassfest and the HACS zip have nothing new to judge if the manifest, `hacs.json`, strings, services, and the platform list stay untouched. Dropping a copied flag removes an entity that the spec does not support. It does not change the `unique_id` of an entity that remains.
- Cost: A user who installed this branch before the fix can see station or feature entities disappear on upgrade. That branch is not a release, and the entities were the wrong ones. This option does not add a repair flow for them.
- Would change my mind if: the base required a second config entry, a service field, or a helper that Home Assistant 2024.2.0 does not provide.

## Rebuttals

### Architect

No change. The Pragmatist is right that the hook is a small diff. That does not make option 2 a smaller risk. The Dreame path stays the path with no codec.

### Pragmatist

No change. Option 1 is the smallest change that drops the copied row without retuning `c102gl`. I am not asking for a shared package.

### Security

No change. The veto line stands. Option 1 does not cross it.

### Home Assistant conventions

No change. A device-core flag rewrite keeps a single coordinator and does not raise the floor.

## Verdict

- Recommendation: Option 1. The Dreame base is `capability.load` and the full Dreame maps, selected when `resolve_family` returns `None`. The Xiaomi base is the explicit maps, the hardened local miIO transport, and fail-closed flags on the Xiaomi codec. At the end of `capability.load`, a non-`None` codec replaces catalog bools and rebuilds `capability.list`. `apply_family` calls the same method when the capability is already loaded. `mijia` stays true on the Xiaomi base because local batches are 10. `disable_sensor_cleaning` stays true unless `SENSOR_DIRTY_LEFT` is mapped. `lidar_navigation` stays false unless `MAP_DATA` or `MAP_SAVING` is mapped. `self_wash_base` stays false unless `SELF_WASH_BASE_STATUS` or `START_WASHING` is mapped. `station_cleaning` stays false unless `WASHBOARD_CLEANING_STATUS` is mapped. `auto_empty_base` and `auto_emptying` stay false unless `START_AUTO_EMPTY` is mapped. `detergent` stays false unless both `DETERGENT_LEFT` and `RESET_DETERGENT` are mapped. `dnd` follows `DND` or `DND_TASK`. `carpet_recognition` follows only `CARPET_RECOGNITION`, because the status path reads that property. Other feature bools stay false unless their own property or action is mapped. `robot_type` stays lidar unless a derived wash base says otherwise. Do not add a package, a model-string branch, a map, or a timeout change. Domain stays `dreame_vacuum`.
- Rejected: Option 2, because rewriting Dreame load through a shared package can change installed robots and is a framework this change does not need. Option 3, because the flow uses the catalog and a second capability object invites a model branch. Option 4, because the copied flags stay and a new Xiaomi model still inherits them.
- Dissent: none
- Security veto: none
- Kill criteria: `capability.list` for a Dreame model, or for `xiaomi.vacuum.c102gl`, changes when the codec is `None`. `self_wash_base` or `station_cleaning` is true for `b108gl` or `d109gl`. A feature flag is true with no mapped address, other than `mijia` and the fail-closed `disable_sensor_cleaning`. An installed Mijia Dreame robot changes task status, cleaning mode, or property routing. A map, room, or zone command is presented as supported. The shared miIO timeout moves off 2 seconds or the Xiaomi transport moves off 5.0 seconds. Any of those reconvenes the council.
- Next action: In this pull request, add the codec hook and the Xiaomi flag derivation, prove Dreame and `c102gl` lists stay put, move `b108gl` and `d109gl` onto the derived flags, and update `/add-device` so a Xiaomi model starts from the Xiaomi base and a Dreame model stays on the catalog row.
