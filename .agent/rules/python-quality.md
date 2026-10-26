---
trigger: always_on
---

# Python quality

New and modified lines must satisfy every item. "The file already does this" is not an exception.

## Dead code

The following are review failures:

- A function, class, method, import, variable, or parameter with no caller. A parameter required by a Home Assistant or library signature is kept and named with a leading underscore when the body does not use it.
- Commented-out code, including a block "kept in case we need it".
- A feature flag, constant, or branch that no runtime path can reach.
- A module that nothing imports.
- A compatibility branch for a Home Assistant version older than `hacs.json`.
- An abstraction with one implementation and one caller. Inline it.
- A `# TODO`, `# FIXME`, or `# XXX` that does not name an issue (`# TODO(#123): ...`). The issue has to exist before the comment is committed.
- A stub body: `...`, `pass` on a non-protocol method, `raise NotImplementedError` left for a later pull request, or a comment that says the logic will be filled in.

Generated translation catalogs and the license text are not dead code.

## Surgical edits

- Change only the lines the task requires.
- Do not reformat, reorder, or retype an untouched function in a file you happen to open.
- Do not rename a symbol the task did not ask to rename. Entity `unique_id`s, service names, config keys, and event names are not renames; they are migrations, and they need the council.
- Do not delete a comment you do not understand. If it is wrong, fix it in the same change that fixes the code it describes.
- Return complete code. Never substitute a placeholder comment for a block you did not want to write out.

## Control flow

- Guard clauses over nested `if` / `else`. A new function body nested more than three levels is split.
- No mutable default arguments (`def f(items=[])` or `def f(items={})`).
- No `global`. A module-level constant is assigned once.
- Comparison to a singleton uses `is` (`is None`, `is True` only when the value is genuinely the boolean singleton and not a truthiness check — prefer `if value:` / `if not value:` for ordinary flags).
- Do not catch `BaseException`, and do not use a bare `except:`.

## Comments

- English only.
- At most two lines.
- Explain why, not what. If the code already says what, delete the comment.
- Forbidden inside comments: bullet lists, numbered steps, decorative rulers, ASCII art, and section banners.
- A one-line module docstring is required on every new module and states what the module is for.

## Constants

- A literal that encodes a protocol value, a timeout, a retry count, a size limit, a status code, or a config-entry key is a named constant.
- Not constants: `0` and `1` used as trivial indexes or empty counts, and a format string that is the whole body of a one-line function.
- The constant lives next to its only user. It moves to the family or the shell constant module when a second module needs it.

## Functions

- A new function does one thing a reviewer can name in a short sentence.
- Side effects are visible in the name (`async_write_...`, `decode_...`) or are absent. A function named like a query must not mutate device state.
- Boolean expressions that mix protocol checks with Home Assistant registry edits are two functions, in the two layers those concerns belong to.
