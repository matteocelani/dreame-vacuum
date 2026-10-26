---
trigger: always_on
---

# Typing

New modules are fully typed. A modified signature is fully typed, including parameters the patch did not otherwise touch on that function. The rest of an inherited file stays as it is until a change edits it.

## Required form

- The first statement of every module is `from __future__ import annotations`, after the module docstring.
- Python 3.12 forms only: `list[str]`, `dict[str, int]`, `str | None`. `Optional`, `List`, `Dict`, `Tuple`, and `Union` from `typing` are forbidden in new code.
- Every function and method annotates every parameter and the return type. `-> None` is written out. `__init__` may omit the return annotation.
- A value that may be missing is `T | None`, and the `None` case is handled at the boundary. Do not sentinel-check with `getattr` or a bare `except` to paper over a missing annotation.
- Module constants that must not be rebound are `Final`.

## `Any` is forbidden

- Do not import or annotate `Any`.
- Untrusted JSON, `python-miio` values, and cloud payloads are parsed at the edge of the device core into a dataclass, an enum, or a `TypedDict`. Callers past that function never see an untyped bag.
- `object` plus an explicit narrowing is the escape hatch when a library truly returns an unknown value. The narrowing lives in that function, not at every call site.
- `Mapping[str, object]` is acceptable as the input type of a parser. It is not acceptable as the type of device state, entity attributes, or coordinator data.
- `# type: ignore` is allowed only with a specific code (`# type: ignore[attr-defined]`) and a comment that names the upstream limitation and the condition that removes the ignore. A bare `# type: ignore` fails review.

## Domain types

- A closed set of wire codes is an `IntEnum` or a `StrEnum`. Call sites use members. A raw integer or a raw string compared to a wire code fails review.
- A structured value the program creates (a point, a room, a capability record, an entity description) is a frozen dataclass with `slots=True`, or a `TypedDict` when the value has to stay a dict at a serialization boundary. Pick one per concept and do not keep both.
- Entity-description fields are typed. `key: str = None` is a defect. Use `key: str` when the field is required and `key: str | None = None` only when absence is a real state.
- The shell's view of a device is a `Protocol` (or a small facade class) defined for the shell. Platform code type-hints that protocol, not a grab-bag of concrete enums, once the facade exists. Do not introduce the protocol in a drive-by; introduce it in the change that needs a second family, or in a dedicated pull request the council accepted.

## Casts and escapes

- `cast(...)` is allowed when the type checker cannot see an invariant the code has already enforced. The line above states that invariant in one sentence. A cast used to silence a checker without an invariant is a defect.
- `assert` is not a type-narrowing strategy in runtime code. Narrow with a conditional and raise a typed exception from the device core, or a `HomeAssistantError` from the shell.

## Generics

- Coordinator entities are parameterized with the coordinator type.
- Do not erase a generic to simplify a signature. If the type is awkward, the data model is wrong; fix the model or ask the council.
