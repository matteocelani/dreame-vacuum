---
trigger: manual
---

# /gate

**Triggers:** `/gate`, "run the tests", "lint", "is this mergeable".

The local quality gate. It does not replace hassfest or the HACS action. Those still have to be green on the pull request when the manifest, `hacs.json`, strings, services, or the platform list changed.

## Preconditions

- The working tree contains the change under test. Do not stash part of it to make the gate look green.
- Commands run from the repository root.

## Steps

1. Read `.agent/rules/formatting.md` and `.agent/rules/tests.md`.
2. If `pyproject.toml` is missing, stop. The gate is not installed. Record `gate: not installed` in the pull request body. A docs-only change may merge with that waiver. A change that adds or modifies Python may not: install the gate from the two rule files in this same change, or stack on the pull request that does, and then re-run `/gate`. Do not invent a one-off Ruff or pytest command line that diverges from the contract.
3. Run, and do not continue past the first failure without fixing it:

```bash
ruff check custom_components tests
ruff format --check custom_components tests
pytest
```

4. For each device-core module this change added, also run:

```bash
pytest --cov=<module> --cov-report=term-missing
```

The module is at or above 90% line coverage, with the exceptions in `.agent/rules/tests.md`.

5. If Ruff or pytest fails, fix the cause. Do not add a global ignore, a blanket `# noqa`, or a `pytest.skip`. Then run `/gate` again from step 3. A fix restarts the gate; a partial re-run is not a pass.
6. Write down the commands and the outcome (pass, or the first failure) for the pull request body.

## Done

- All three commands exited 0, and every new device-core module met the coverage bar. Or the change is docs-only and the body records `gate: not installed` or `gate: not run, docs only` honestly.
- No ignore, skip, or coverage exclusion was added to buy the green run.

## NEVER

- Format or autofix the inherited tree while gating an unrelated change. `ruff check --fix` and `ruff format` apply only to files this change already owns, and only to satisfy a diagnostic in those files.
- Report PASS when a command did not run.
- Lower `hacs.json`'s Home Assistant floor, or delete a test, to get a green run.
- Treat a green local gate as a waiver for hassfest or HACS validation.
