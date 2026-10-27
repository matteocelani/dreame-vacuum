# 0003 — How should the unfinished X20 Max integration be finished and shipped?

- Status: accepted
- Date: 2026-10-26
- Supersedes: none
- Superseded by: none

## Brief

**Question.** How do we finish and ship the X20 Max (`xiaomi.vacuum.d109gl`) and S20+ (`xiaomi.vacuum.b108gl`) integration, given that pull request #6 carries mappings from commit `48ee651` that were tested on real hardware in March 2026, but the restructured tree was not re-run on a robot, dropped defensive guards from that testing, copied capability flags from the old `c102gl` row, and has no map, room, or zone support?

**Why now.** Council 0002 accepted the sibling package and the codec injection, and that structure is already on this branch. It did not decide what to do with the guards `48ee651` had in the shared parsers, or whether an unverified map and a re-derived capability row belong in the same pull request. Until that shipping line is accepted, the branch can still grow a model-string check, a global timeout change, or an untested map parser under the claim that the March robot already proved them.

**Constraints.**

- Installed users. Domain stays `dreame_vacuum`. No config-entry key, entity `unique_id`, device identifier, or service schema changes. Council 0001 is not reopened. Council 0002 still holds: no branch on `xiaomi.vacuum.` or on `capability.mijia`, and the shared `DreameVacuumDeviceProtocol` miIO timeout stays 2 seconds (`super().__init__(ip, token, 0, 0, True, 2)` in `dreame/protocol.py`). The Xiaomi property path is `MiioPropertyTransport`, whose `_TIMEOUT_SECONDS` is already `5.0`. That is the local miIO timeout the March property writes used. Cloud HTTP timeouts (6, 10, and 15 seconds) are a different path and were not the March change.
- Home Assistant floor. `hacs.json` stays `2024.2.0`. No new runtime dependency.
- HACS. One integration. Tests stay outside the package. The guards land in the parsers that already run, not in a new package.
- Secrets. No token, datagram body, real device id, or map dump in source, tests, or logs. The local token stays on the transport object.
- What `48ee651` actually changed, and what this branch dropped. The shared parsers lost `isinstance(..., str)` before `json.loads` / `split` on `DND_TASK`, `SCHEDULE`, `STREAM_STATUS`, and `OFF_PEAK_CHARGING`. `SCHEDULE` for `d109gl` is siid 2 / piid 19 (`order-clean`), so a non-string value reaches `_schedule_changed` and `.split` raises. `_request_cleaning_history` still evaluates `total > 0` when `CLEANING_COUNT` is `None` or a numeric string. `cleaning_paused` is still `bool(value)`, so a non-empty string such as `"0"` is true. Two attribute sites still evaluate `value > 0`, which raises when the value is a string. `_handle_device_info` still calls `json.loads` on a non-string `prop`. The March `cleaning_paused` special case was gated on `"xiaomi.vacuum." in model`. Restoring that gate would violate 0002.

**Unknowns.**

- No robot is on this network. The restructured codec, catalog rows, and local transport have not been repeated on the X20 Max that passed the March HAOS 13.2 / HA 2026.3.4 checks (setup, state, errors, sensors, start/pause/return_to_base/locate, the dock cycle, and local-only property writes).
- The runtime type of `d109gl` `order-clean`. It is not a Dreame semicolon schedule. It may be an int, a dict, or sometimes a string. The guard has to tolerate all three.
- Whether any installed Dreame model reports `CLEANING_PAUSED` as a truthy integer other than 1. This decision does not change the integer or bool reading.
- Which copied `c102gl` capability flags are wrong on these two models. This council does not invent a replacement list.
- Why the map reports a missing map key. Segment, room, and zone commands are unmapped. No fixture from the robot exists, and none will be added here.

**Options.**

1. Restore the type guards in the parsers that already own those values, with no model-string branch. Keep `_TIMEOUT_SECONDS` at 5.0 on the Xiaomi property transport. Leave the shared Dreame miIO timeout at 2 seconds and leave cloud HTTP timeouts alone. Do not re-derive capability flags and do not add map, room, or zone support in this pull request. Ship the branch as a base the owner re-tests on hardware before merge. Revert is a commit revert. No storage rewrite. A later capability correction is `/add-device` once the owner has hardware evidence. A later map or room change is its own pull request and convenes a council only if it hits a trigger in the council README.
2. Option 1, and also raise `DreameVacuumDeviceProtocol` from 2 seconds to 5, matching the other half of the `48ee651` timeout edit. Revert is a commit revert and does not move storage. Every local Dreame robot waits longer when the LAN device does not answer. This contradicts the timeout sentence of 0002. Accepting it would supersede that sentence only.
3. Hold the pull request until the owner re-runs the restructured package on the X20 Max and until capability flags and map, room, and zone support are derived in this same change. Reversible, because nothing new lands. The non-string schedule crash stays in the tree the owner would be re-testing.
4. Do nothing. Merge the restructured code with the dropped guards, the copied flags, and no map. Revert is possible only before merge. A non-string `SCHEDULE`, `DND_TASK`, `STREAM_STATUS`, `OFF_PEAK_CHARGING`, device-info `prop`, or `value > 0` comparison can still raise during an update.

## Positions

### Architect

- Option: 1
- Owns: The Dreame parsers that already accept `SCHEDULE`, `DND_TASK`, `STREAM_STATUS`, `OFF_PEAK_CHARGING`, `CLEANING_COUNT`, `CLEANING_PAUSED`, attribute flags, and device-info `prop`. The Xiaomi package keeps the property transport and its 5.0 second timeout. No new package, no shared helper module, and no model string in `device.py`.
- Because: These guards are narrowing at an existing boundary, not a second family hiding inside Dreame. A timeout constant for this family already lives in `xiaomi/transport.py`. Writing 5 into `DreameVacuumDeviceProtocol` puts one family's timing in the other family and is the change 0002 refused. Capability flags are a catalog row. Map and rooms are a later `xiaomi` change with a real decode, not a stub and not a condition in a platform module. Hard-coding `dreame_vacuum` is not part of this option.
- Cost: Dreame entities still render Xiaomi values, so a bad flag still looks like a normal entity. The split between "guards now" and "map later" stays visible only if the later change does not grow inside `device.py`.
- Would change my mind if: the Xiaomi property transport were still the shared `DreameVacuumDeviceProtocol`, so the March 5 second timeout had nowhere else to live.

### Pragmatist

- Option: 1
- User impact: none for an already-configured vacuum whose properties are already strings, bools, or ints. A user on S20+ or X20 Max stops taking an update exception when `order-clean` is not a schedule string. Same config entry, same entities, same history.
- Because: The crash is the user-visible hole. The guard is a few conditions, and a revert does not touch storage. Option 2 makes every local Dreame failure 3 seconds slower, and the property path these models use is already 5.0 seconds. I am not re-deriving flags or drawing a map without a robot. I am deferring the ten-family picture to the Architect and the token handling to Security. The slice that lands now is the guards. Flags wait for `/add-device` with hardware evidence. Map and rooms wait for their own pull request.
- Cost: The copied `c102gl` flags stay, so a wrong switch can still appear until a later row. The map still does not load. The owner has to re-test before merge, which this option does not pretend to replace.
- Would change my mind if: an already-configured Dreame robot relies on `cleaning_paused` being true for a non-empty string, or on `value > 0` raising, which is not a behavior anyone can use.

### Security

- Veto: no
- Option: 1
- Because: Option 1 adds no endpoint, no dependency, and no TLS change. Nothing new leaves the house. The token stays on the transport, and the new tests must use a fake token and `127.0.0.1`, not a capture. A parser that raises on `order-clean` can surface the value in a traceback; skipping a non-string avoids that without logging it. I will veto an implementation that logs the token or a property body, disables TLS, or commits a map or device dump to "finish" rooms. Option 2 is not a secret exposure. It is not the proposal I support. Option 3's map work is where a floor plan would enter the tree, and I do not accept that work in this decision.
- Cost: The awkward part is small. Device-info and schedule parsing stay in the inherited modules, so the guard cannot grow a new redaction helper in this change. Diagnostics redaction is unchanged.
- Would change my mind if: the guards cannot be written without logging the raw property or without a new parser dependency.

### Home Assistant conventions

- Option: 1
- HA surface: none
- Because: Config-entry identity, `unique_id`s, device identifiers, `services.yaml`, and `strings.json` stay put. One coordinator per entry. `iot_class` stays `cloud_polling`. The floor stays 2024.2.0. No new flow error and no new entity, so no new translation key. The work is inside the device core. Option 2 lengthens the executor job for every local miIO call on every model, which these two models do not need for property reads and writes. hassfest and the HACS zip have nothing new to judge if the manifest, `hacs.json`, strings, services, and the platform list stay untouched.
- Cost: The integration still exposes entities for capability flags that were copied, and it still has no map entity that works on `d109gl`. That is an honesty problem in the README, which already says segments, zones, and map management are not mapped. This option does not add a broken map entity to hide that.
- Would change my mind if: the guards required a second config entry, a service field, or a helper that Home Assistant 2024.2.0 does not provide.

## Rebuttals

### Architect

No change. The Pragmatist is right that the guards are a small diff. That does not make option 2 a Xiaomi timeout. The 5.0 second constant already has an owner.

### Pragmatist

No change. Option 2 is the smaller character edit and the larger installed-base change. I am not asking for it.

### Security

No change. The veto line stands. Option 1 does not cross it.

### Home Assistant conventions

No change. A device-core guard keeps a single coordinator and does not raise the floor.

## Verdict

- Recommendation: Option 1. In this pull request, restore type guards so a non-string `SCHEDULE`, `DND_TASK`, `STREAM_STATUS`, `OFF_PEAK_CHARGING`, or device-info `prop` is skipped instead of parsed; so `CLEANING_COUNT` of `None` or a numeric string does not raise in `_request_cleaning_history`; so `cleaning_paused` treats a numeric string by `int(value) == 1` and leaves bool and int values on `bool(value)`; and so attribute flags do not compare a string to an int. Do not add a `xiaomi.vacuum.` branch. Do not change `DreameVacuumDeviceProtocol`'s 2 second timeout or the cloud HTTP timeouts. Keep the Xiaomi property transport at 5.0 seconds. Do not re-derive capability flags. Do not add map, room, or zone support. Domain stays `dreame_vacuum`. The owner re-tests this base on hardware before merge.
- Rejected: Option 2, because the March property writes already have a 5.0 second timeout on `MiioPropertyTransport`, and raising the shared miIO timeout retunes every local Dreame robot, which 0002 forbade. Option 3, because it blocks the crash fix on map and flag work this environment cannot derive, and because a copied row is not fixed by inventing another one. Option 4, because the non-string schedule path still raises. A model-string gate around `cleaning_paused` is rejected with option 2's spirit: 0002 forbids it, and applying `int(value) == 1` to every integer would change a Dreame robot that reports a truthy value other than 1.
- Dissent: none
- Security veto: none
- Kill criteria: `_schedule_changed` still raises on a non-string schedule. An installed Dreame robot changes task status, cleaning mode, or property routing. An installed Dreame robot loses a low-battery pause notification for integer 0 or 1, or gains one for the string `"0"`. The shared miIO timeout is observed at 5 seconds. The owner’s X20 Max retest fails setup, state, the dock cycle, or local property writes. A map, room, or zone command is presented as supported. Any of those reconvenes the council or, for a failed retest, blocks merge.
- Next action: In this pull request, restore those guards and cover a non-string schedule (and the other restored branches) with device-core tests, and correct the pull request risk note so it states both timeouts: Xiaomi property transport 5.0 seconds, shared Dreame miIO protocol 2 seconds.
