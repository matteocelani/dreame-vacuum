# 0002 — How should Xiaomi S20+ and X20 Max be structured in this integration?

- Status: accepted
- Date: 2026-10-26
- Supersedes: none
- Superseded by: none

## Brief

**Question.** How should support for `xiaomi.vacuum.b108gl` (Xiaomi Robot Vacuum S20+) and `xiaomi.vacuum.d109gl` (Xiaomi Robot Vacuum X20 Max) be structured, reusing the mapping and state conversion from commit `48ee651`, without renaming the Home Assistant domain?

**Why now.** Council 0001 says a second family is a sibling package created in the pull request that adds a concrete device, and that a domain rename is a separate council. These two models are that device. Upstream rejected them because they are not Dreame hardware. Until this structure is accepted, the port can still land as model-string branches inside the Dreame core, which is the shape `48ee651` used and the shape this repository forbids.

**Constraints.**

- Installed users. Domain stays `dreame_vacuum`. No config-entry key, entity `unique_id`, device identifier, or service schema changes. The model string is not stored on the config entry today; it arrives from the device at connect. Four Mijia Dreame models already in the current catalog (`c102cn`, `c102gl`, `d103cn`, `d110ch`) are reported as `xiaomi.vacuum.*` and already set `capability.mijia`. A branch on the prefix `xiaomi.vacuum.` or on `capability.mijia` changes those installed robots.
- Home Assistant floor. `hacs.json` stays `2024.2.0`. No new runtime dependency. `pycryptodome` is already in the manifest.
- HACS. One integration, package directory `custom_components/dreame_vacuum`. The new package lives inside that package. Tests stay outside it.
- Secrets. The local miIO token stays in memory on the transport. It must not be logged, put on a repr, or committed. No real device id, map, or token in fixtures. Cloud TLS is unchanged.
- Imports. Family packages must not import each other. Parent imports are forbidden, so `xiaomi` cannot import `dreame` and `dreame` cannot import `xiaomi`. The shell can import both. `48ee651` also copied the then-current `c102gl` capability row (`[1, 1, 18, 1]`, key `OFULk9To37qRdXY3`). The current blob is a newer catalog (763 models). Index 18 is a different capability now. The key string is still present, at a different index.
- Prior fixes to keep. `59f1551` removed `STATUS` from the Xiaomi property map so it cannot overwrite `STATE`. `ad756ee` converts values when raw properties arrive, not only on the optimistic update path.

**Unknowns.**

- Whether cloud `set_properties` still discards writes on these two models, which is why `48ee651` added a local UDP property transport. No device is on this network to recheck.
- Whether the copied `c102gl` capability flags match the hardware. The owner shipped that row; this council does not invent a different flag list.

**Options.**

1. Sibling package `xiaomi`, plus a generic codec the shell injects into the existing Dreame device. The package owns the two model codes, the MIoT overrides (no `STATUS`), the state and task conversion, the simple cleaning-mode flag, the docked-activity correction, and the local property transport. The Dreame device calls a resolver with the reported model and applies the result. It does not contain those model strings. `DEVICE_INFO` on the current blob gains the two rows with the owner's brand, flag, capability list, and key string, retargeted to current indexes. The global miIO timeout stays 2 seconds. Revert removes the package, the resolver argument, and the two rows. No storage rewrite.
2. Port `48ee651` inline into `dreame/types.py`, `device.py`, `protocol.py`, and `map.py`, including branches on `xiaomi.vacuum.` and `capability.mijia`, and the timeout change from 2 seconds to 5. Revert is a commit revert. Installed Mijia Dreame robots take the new branches because they already match those conditions.
3. A second device class that does not use `DreameVacuumDevice`, selected by the shell. Revert does not touch storage. Entities, services, and the map path are built for the Dreame device. A parallel class does not drive them without a second shell.
4. Do nothing. The two models stay out of the current catalog and the flow keeps rejecting them as unsupported.

## Positions

### Architect

- Option: 1
- Owns: `custom_components/dreame_vacuum/xiaomi/` owns the Xiaomi MIoT identity. The Dreame package owns only the codec application (merge overrides, call convert on the way in and out). The shell owns the resolver injection. Neither family imports the other. No shared package: the codec is a value the shell passes, not a module both families import.
- Because: Option 2 is a second family living as conditions inside Dreame, and those conditions also match Mijia Dreame models. Option 3 is a second implementation of the whole device with one caller, which I reject. The codec is the boundary parent imports force. It is not a plugin registry. Hard-coding `dreame_vacuum` inside the new package is rejected; imports stay package-relative.
- Cost: Dreame entities still render Xiaomi values, so a bad map looks like a wrong state. Property names are strings shared with `DreameVacuumProperty`, and the type checker cannot see that link.
- Would change my mind if: the two models used the Dreame siid/piid table and the Dreame value domain, so a catalog row was enough.

### Pragmatist

- Option: 1
- User impact: none for an already-configured Dreame, MOVA, Mijia, or TROUVER vacuum. A user who adds S20+ or X20 Max gets one config entry on `dreame_vacuum`, the same as any other model the catalog accepts.
- Because: The user-visible outcome is that these two model ids are accepted and their state conversion runs. That does not need a storage migration or a second device class. Option 2 is smaller as a diff and wrong as a behavior change: `c102gl` and the other three Mijia models already use `xiaomi.vacuum.` and `capability.mijia`. The local transport stays, because without it the owner's tested property writes do not stick, and it is still this pull request. I am deferring the ten-family picture to the Architect and the token handling to Security.
- Cost: The Dreame device grows a resolver argument and a few codec calls. A later family that is not MIoT-shaped cannot reuse this codec and will need its own shell branch.
- Would change my mind if: `DreameVacuumDevice` cannot represent these models without a new config entry for a vacuum the user already added.

### Security

- Veto: no
- Option: 1
- Because: Option 1 adds no dependency, no cloud endpoint, and no TLS change. The local transport speaks the same LAN miIO datagrams `python-miio` already speaks, using `pycryptodome` already in the manifest, and only for property reads and writes. The token stays on the transport object. Repr and logs omit it. Fixtures use a token of repeated `0` bytes. Option 2's timeout change and its `xiaomi.vacuum.` branches are not a secret exposure, but they are not the proposal I support. I will veto an implementation that logs the token or the datagram body, disables TLS, or commits a capture from a real robot.
- Cost: The safer call is awkward: the Dreame protocol has to accept a transport it does not construct, so a failed local probe must fall back to the existing cloud path instead of raising through a shared exception type.
- Would change my mind if: the transport cannot be written without a new dependency or without putting the token in a log line.

### Home Assistant conventions

- Option: 1
- HA surface: coordinator (one optional constructor argument) and the catalog the config flow already reads. No new flow branch, service, or entity.
- Because: Domain, `unique_id`s, device identifiers, and `services.yaml` stay put. `iot_class` stays `cloud_polling`: local property access is the same optional LAN path this integration already has, not a cloud-free setup. The floor stays 2024.2.0. The flow still aborts a second entry for the same MAC. User-visible copy for the two models lives in the README, not in a new `strings.json` key, because no new flow error or entity name is introduced. hassfest and the HACS zip stay valid if `manifest.json` is untouched.
- Cost: The integration domain still says Dreame after a Xiaomi sibling exists. That is the 0001 decision, and this option does not reopen it.
- Would change my mind if: these models needed a second config entry, a new service field, or a helper that 2024.2.0 does not provide.

## Rebuttals

### Architect

No change. The Pragmatist is right that the codec calls are extra lines in the Dreame device. Those lines are the boundary, not a model branch, and they do not make option 2 acceptable.

### Pragmatist

No change. Option 1 is the smallest change that does not retune installed Mijia robots. I am not asking to drop the local transport.

### Security

No change. The veto line stands. Option 1 does not cross it.

### Home Assistant conventions

No change. A sibling under `dreame_vacuum` keeps one coordinator per config entry and does not raise the floor.

## Verdict

- Recommendation: Option 1. Add a `xiaomi` sibling package that owns the S20+ and X20 Max MIoT maps, the state and task conversion (with `STATUS` left unmapped and conversion applied to raw property values), and the local property transport. The shell passes a resolver into the Dreame device. The device applies a returned codec and does not name these models. Re-add the two rows to the current `DEVICE_INFO` blob using the owner's brand, catalog flag, capability list, and key string, at current indexes. Do not rename the domain. Do not change the timeout for other devices. Do not branch on `capability.mijia` or on the `xiaomi.vacuum.` prefix.
- Rejected: Option 2, because the inline branches match Mijia Dreame models that are already installed, and because a second family inside Dreame contradicts 0001. Option 3, because it duplicates the device the shell already drives. Option 4, because the two models stay unsupported.
- Dissent: none
- Security veto: none
- Kill criteria: An installed Mijia Dreame model (`xiaomi.vacuum.c102gl`, `c102cn`, `d103cn`, or `d110ch`) changes task status, cleaning mode, or property routing. Or a map request on `b108gl` is sent with the Dreame `REQUEST_MAP` action, which that model's spec uses as start-vacuum. Or the local transport logs a token or a datagram body. Any of those reconvenes the council.
- Next action: In this pull request, add the `xiaomi` package and the codec injection, re-encode `b108gl` and `d109gl` into the current `DEVICE_INFO` blob, and cover the mapping, the conversion, and catalog recognition with device-core tests.
