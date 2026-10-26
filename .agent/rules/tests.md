---
trigger: always_on
---

# Tests

Tests protect protocol behavior and Home Assistant lifecycle. They are not a coverage costume.

## Layout

- Tests live in a top-level `tests/` directory that mirrors the package path: a module `custom_components/<domain>/<family>/protocol.py` is tested by `tests/<family>/test_protocol.py`.
- Tests are not placed inside `custom_components/`. HACS would ship them.
- A test module does not import from another test module. Shared builders live in `tests/helpers.py` or `tests/<family>/helpers.py` and contain no assertions.
- Device-core tests must not import `homeassistant`. That constraint is what keeps the core honest.
- Tests that need Home Assistant are marked `ha` and use the custom-component pytest harness. They are not the default place to test a parser.

## What every change tests

- A new capability, property, action, or model record ships with a test that asserts the record and at least one decode or state transition that uses it.
- A bug fix ships with a regression test that fails on the parent commit and passes on the fix. If you cannot show that, the test is not a regression test; say so and write the assertion you can actually support.
- A config-entry migration ships with a test that feeds the previous data shape and checks the stored result, including "already migrated".
- A redaction change ships with a test that the masked keys are absent from the diagnostic payload.
- Do not add tests whose only assertion is that a constant equals itself, or that a module imports.

## Isolation

- No network, no DNS, no real MQTT broker, no clock dependence. Time is injected or frozen.
- The cloud client and the local device client are faked at the boundary the production code already has. Do not mock three internals deep into a parser; that test breaks when the parser is cleaned up and proves nothing.
- A fixture that builds a device uses fake credentials, per `.agent/rules/security.md`.

## Coverage

- There is no repository-wide coverage gate until the inherited tree is measured honestly. Do not set `--cov-fail-under` to a number the tree cannot meet, and do not exclude the inherited package from measurement to manufacture a percentage.
- A new device-core module added by the pull request is at or above 90% line coverage, checked with `pytest --cov=<that module> --cov-report=term-missing`. Lines that are logging-only or a typed re-raise may stay uncovered; an uncovered branch that changes device behavior may not.
- The shell has no percentage gate. It does have a presence gate: a new public function, a new flow branch, or a new service has a test. Review fails the pull request if that test is missing.
- `pytest.skip` requires a reason that is an optional extra the environment may lack. Skipping because the test is unfinished is a failure. Delete the test or finish it.

## Tooling contract

The pull request that installs the gate adds this pytest configuration next to the Ruff contract:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --strict-markers --strict-config"
markers = [
    "ha: tests that import homeassistant and need the custom-component harness",
]
asyncio_mode = "auto"
```

Run from the repository root:

```bash
pytest
```

A pull request that touches Python also runs the coverage command above for each new device-core module and records the result in the pull request body. A docs-only pull request does not pretend it ran pytest.
