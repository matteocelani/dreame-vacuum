---
trigger: always_on
---

# Security

This integration holds the keys to someone's home: cloud passwords, local tokens, floor plans, and the ability to drive a robot. Treat every change as if the pull request will be read by a stranger with a hostile config entry.

## Secrets never enter the repository

Forbidden in source, tests, fixtures, snapshots, commit messages, pull request text, issue templates, and log samples:

- passwords, tokens, auth keys, session cookies, refresh material;
- real account emails or account ids;
- real device ids, real MAC addresses, real LAN IPs;
- map dumps, obstacle photos, or Wi-Fi maps from a real home.

Fixtures use obvious fakes: a token of repeated `0` characters at the length the protocol requires, host `127.0.0.1`, and MAC `00:00:00:00:00:00`. A test that needs a realistic cryptographic vector uses a vector generated in the test from a fixed fake key, not a capture from hardware.

## Where credentials live

- Config entry data is the only store for a username, password, token, auth key, or equivalent. Options do not hold secrets.
- The coordinator passes credentials into the device core at construction. Entities do not read `entry.data` for secrets.
- Secrets are not copied onto entity state, entity attributes, device-registry fields, persistent notifications, or events.
- Do not print a config entry. `ConfigEntry.as_dict` and similar dumps include data.

## Diagnostics redaction

These keys are redacted (removed or replaced with a fixed mask) in any diagnostic payload, debug dump, or repair description: `username`, `password`, `token`, `auth_key`, `dvc_key`, `host`, `mac`, `did`, plus any header or cookie that carries a session. A new credential key is added to this list in the same change that introduces it. Map geometry is omitted from the default diagnostic payload; include it only behind an explicit, documented opt-in, and say so in the pull request.

## Transport

- TLS verification stays on. `verify=False`, a custom trust-all context, and disabling hostname checks are forbidden.
- Cloud endpoints are constants. Do not take the authentication host from user input without an allow-list the council has accepted.
- Local network control is preferred when the device supports it. Do not send a map or a credential to the cloud for a feature the user asked to run locally.
- A dependency that parses untrusted device bytes (map decoder, crypto, JavaScript runtime) is not upgraded casually. Version bumps of `pycryptodome`, `python-miio`, `mini-racer`, `numpy`, and `paho-mqtt` name the reason and the risk in the pull request.

## New dependencies

A new install-time requirement is a council decision. The record must cover maintenance status, the license, what it does to HACS install size, and whether the same job can be done with the standard library or a library Home Assistant already installs. Typosquats and packages pinned to a mutable URL fail regardless of the council.

## Logs and errors

Follow `.agent/rules/errors.md`. In addition: an exception message built from a request body or a response body is scrubbed first. `repr` of a protocol object that stores a token is a leak; `__repr__` on credential-bearing objects lists the fields it omits.
