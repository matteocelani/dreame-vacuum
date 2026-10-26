---
trigger: always_on
---

# Formatting and lint

Ruff is the only linter and the only formatter. Its formatter is Black-compatible: line length 88, double quotes, spaces, trailing commas where Black would put them. Do not add Black, isort, autopep8, or yapf beside it. Do not enable Ruff's preview format.

## The configuration contract

The first pull request that installs the gate adds a `pyproject.toml` with this configuration, unchanged. Weakening a selection, adding a global ignore, or raising the line length requires a council record. Per-file ignores are allowed only for inherited modules, each tied to an issue that removes the ignore, and never for a file the same pull request creates.

```toml
[tool.ruff]
target-version = "py312"
line-length = 88
src = ["custom_components", "tests"]

[tool.ruff.lint]
select = [
    "A",
    "ANN",
    "ARG",
    "ASYNC",
    "B",
    "BLE",
    "C4",
    "E",
    "F",
    "I",
    "N",
    "PIE",
    "PTH",
    "RET",
    "RUF",
    "SIM",
    "T20",
    "TID",
    "UP",
]
ignore = [
    "E501",
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["ANN", "ARG"]

[tool.ruff.lint.flake8-annotations]
mypy-init-return = true
suppress-dummy-args = true

[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "parents"

[tool.ruff.lint.flake8-tidy-imports.banned-api]
"typing.Any".msg = "Any is forbidden. Parse untyped data at the boundary into a real type."
"typing.Dict".msg = "Use dict[]."
"typing.List".msg = "Use list[]."
"typing.Optional".msg = "Use X | None."
"typing.Tuple".msg = "Use tuple[]."
"typing.Union".msg = "Use X | Y."

[tool.ruff.lint.isort]
combine-as-imports = true
force-sort-within-sections = true
section-order = [
    "future",
    "standard-library",
    "third-party",
    "homeassistant",
    "first-party",
    "local-folder",
]

[tool.ruff.lint.isort.sections]
homeassistant = ["homeassistant"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
docstring-code-format = false
```

`E501` is ignored because the formatter owns line length. A line the formatter cannot wrap (a long string that is not a URL, a path, or a translation key) is still broken by hand. Review treats a hand-wrapped violation as a failure.

## What lint means in review

- `F401`, `F841`, and `ARG` removals are dead-code removals, not style. Fix them. Do not prefix a used name with `_` to silence the checker.
- `T20` forbids `print`. Diagnostics go through the integration logger (`.agent/rules/errors.md`).
- `ASYNC` findings in shell code are correctness bugs. Do not ignore them.
- `TID` parent-import findings are architecture bugs. Do not ignore them.
- A `# noqa` needs a specific code and a one-line reason. A file-level noqa blanket fails review.

## Commands

From the repository root, once `pyproject.toml` exists:

```bash
ruff check custom_components tests
ruff format --check custom_components tests
```

`ruff format` without `--check` is allowed only to fix files the task already changed. Running it across the inherited tree is a dedicated pull request, not a side effect.
