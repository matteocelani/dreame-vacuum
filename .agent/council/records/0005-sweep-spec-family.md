# 0005 — Where does a second Xiaomi spec-family profile live?

- Status: accepted
- Date: 2026-10-28
- Supersedes: none
- Superseded by: none

## Brief

**Question.** Where does a second MIoT spec-family profile live, so E10-class models share it and later sweep-layout models can declare only diffs, without changing the council 0004 Xiaomi base contract?

**Why now.** `xiaomi.vacuum.b112`, `b112gl`, and `b112bk` are one released spec family. Address overlap with the station profile (`d109gl`) is about 0.15. The same layout is what X20 (`c101eu`), S20 (`d106gl`), S12 (`b106eu`), and T12 (`b106bk`) publish. Copying the station profile onto them would send the wrong addresses. Copying one E10 file three times, and again for those later models, is the duplication this profile exists to avoid.

**Constraints.**

- Installed users. Domain stays `dreame_vacuum`. No config-entry key, entity `unique_id`, device identifier, or service schema changes. Council 0004 flag rules, the local miIO transport, and `resolve_family` returning `None` for every model that is not registered stay as they are.
- Home Assistant floor. `hacs.json` stays `2024.2.0`. No new runtime dependency. No new package and no new top-level directory.
- Secrets. Spec fixtures are public MIoT documents. No token, host, or device id.
- The 0004 base contract is the codec hook, the explicit maps, the fail-closed flags, and the Dreame catalog path when the codec is `None`. This record does not rewrite that contract. A model still selects a base by being present or absent in `resolve_family`.

**Unknowns.**

- No robot is on this network. The released specs name services and addresses. They do not prove which entities a live E10 should show.
- `b112bk` has a debug version 2. This record uses released version 1 only. Whether version 2 ever ships is unknown.
- `b112bk` publishes a different timezone range from `b112`. That property is omitted, so the difference does not fork the profile.

**Options.**

1. Keep one Xiaomi package and one `XiaomiModel` codec. Move the family-agnostic composers and the stored Dreame codes into `model.py`. Leave the station tables in `profile.py`. Add `sweep.py` for the sweep-service addresses, state map, value maps, and controls. A model file composes that profile and declares only its diffs. `resolve_family` still returns the codec. Flags still come from `apply_capabilities`. Revert is a commit revert and does not move storage.
2. Add a second device-family package for the sweep layout. Revert does not move storage. It is a new package the 0004 record refused, and both packages would still speak MIoT through the same codec.
3. Paste the E10 addresses into each model file and refactor a shared profile when `c101eu` arrives. Revert is a commit revert. The shared shape is already visible, so the split would be a later rewrite of the same tables.
4. Do nothing. E10, E12, and E10C stay unsupported, and the next sweep-layout model has nowhere to compose from.

## Positions

### Architect

- Option: 1
- Owns: `xiaomi/model.py` owns the codec, the stored Dreame codes, and the composers. `xiaomi/profile.py` owns the station spec family. `xiaomi/sweep.py` owns the sweep spec family. Model modules own diffs. Neither profile imports the other. The shell still sees one facade.
- Because: Option 2 is a second package with one codec and one transport. Option 3 hides a second profile inside copy-paste. The composers are already called by every station model; moving them is the split the second caller makes real. Hard-coding `dreame_vacuum` is not part of this option. Flag derivation stays on the codec, so a sweep model cannot turn a flag on by naming a station address it did not map.
- Cost: Station model files still import the composers from `profile.py`, which re-exports them. A reader can miss that the definitions moved.
- Would change my mind if: the sweep models used the station siid table and the station value domain, so another profile had no second caller.

### Pragmatist

- Option: 1
- User impact: none for an already-configured vacuum. Same config entry, same entities, same history. E10, E12, and E10C are not in a release.
- Because: The user-visible hole is three models on the wrong spec. A new package does not fix that, and a copied file would be deleted when `c101eu` lands. The codec hook already exists. I am deferring token handling to Security. The slice that lands now is the profile, these three models, and tests that the station lists stay put.
- Cost: `model.py` grows by the composers. A sweep value that the Dreame select cannot round-trip stays a Xiaomi control until a later row maps it.
- Would change my mind if: shipping the profile required a new config entry for a vacuum the user already added.

### Security

- Veto: no
- Option: 1
- Because: Option 1 adds no endpoint, no dependency, and no TLS change. Nothing new leaves the house. The token stays on the transport. Spec fixtures are the public released documents, with no token, host, or device id. I will veto an implementation that logs a token, a property body, or a datagram, or that sends an address the released spec does not list. Option 2 is not a secret exposure. It is not the proposal I support.
- Cost: The safer call is the same boundary as 0004. The sweep profile does not give the shell a second way to read the token.
- Would change my mind if: mapping the family required a property value in a log or a fixture captured from a robot.

### Home Assistant conventions

- Option: 1
- HA surface: new entities only for the new models, through the existing Xiaomi control descriptions and the existing vacuum entity. New English keys in `strings.json`. No service field.
- Because: Config-entry identity, `unique_id`s, device identifiers, `services.yaml`, and the platform list stay put. One coordinator per entry. `iot_class` stays `cloud_polling`. The floor stays `2024.2.0`. hassfest and the HACS zip have nothing new to judge beyond `strings.json` keys. The catalog row is the same copied row the other Xiaomi models use, replaced at load by the codec.
- Cost: The legacy DnD switch description has no property key, so the shell still creates that switch. Turning it on does not send a write, because the sweep spec's DND property is read-only and stays unmapped.
- Would change my mind if: the profile required a second config entry, a service field, or a helper that Home Assistant 2024.2.0 does not provide.

## Rebuttals

### Architect

No change. The Pragmatist is right that the hook already exists. That does not make option 3 smaller once `c101eu` copies the same tables.

### Pragmatist

No change. Option 1 is the smallest change that lets the next sweep model be a diff. I am not asking for a new package.

### Security

No change. The veto line stands. Option 1 does not cross it.

### Home Assistant conventions

No change. A device-core profile keeps a single coordinator and does not raise the floor.

## Verdict

- Recommendation: Option 1. The Xiaomi base stays the explicit maps, the local miIO transport, and fail-closed flags on `XiaomiModel`. `resolve_family` still selects that codec or returns `None`. Station tables stay in `profile.py`. The sweep family lives in `sweep.py`. Model files compose it and declare only diffs. Domain stays `dreame_vacuum`. Do not add a package, a model-string branch in the shell, a map, or a change to the 0004 flag rules.
- Rejected: Option 2, because a second package does not change the codec and 0004 already refused it. Option 3, because the shared sweep layout is already visible on five model codes. Option 4, because the three models stay unsupported.
- Dissent: none
- Security veto: none
- Kill criteria: A station model's property map, action map, or derived flag list changes. A sweep model sends an siid/piid or siid/aiid that its released spec does not list. `resolve_family` returns a codec for a model that is not registered. Domain, config-entry identity, `unique_id`s, device identifiers, or a service schema changes. Any of those reconvenes the council.
- Next action: In this pull request, add `sweep.py`, register `b112`, `b112gl`, and `b112bk` on the sweep profile from their latest released specs, and test that every spec item is mapped or omitted and that station capability lists stay put.
