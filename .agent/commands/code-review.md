---
trigger: manual
---

# /review

**Triggers:** `/review`, `@review`, "review the code", "check before PR".

A review is a loop. The loop ends when a clean pass finds zero violations in lines this branch added or modified. Fixing a violation restarts the loop. "Minor", "pre-existing style", and "matches the file" are not verdicts on a new line.

## Preconditions

- The branch is not `master`.
- The diff under review is `git diff origin/master...HEAD` after `git fetch origin`. Uncommitted work is included via `git diff HEAD` as well, and it is reviewed, not ignored.

## Steps

### Step 0 — Read the rules

Every iteration, read `AGENTS.md` and every file in `.agent/rules/`. Do not review from memory.

### Step 1 — Take the diff

```bash
git fetch origin
git diff origin/master...HEAD
git diff HEAD
```

Ignore nothing inside `custom_components/` or `tests/`. Generated locale catalogs are in scope only for keys that do not exist in `strings.json`.

### Step 2 — Self-pass

Walk each rule file. For every new or modified line, record `file:line — rule file — violated sentence` or record nothing for that file. Be exhaustive. A violation not written down becomes a review comment later.

Inherited violations on unchanged lines are out of scope. A new line that copies an inherited violation is in scope.

### Step 3 — Branch

- Any violation: fix it, then return to Step 0. Do not announce a pass.
- No violations: continue.

### Step 4 — Gate

Run `/gate`. A failure is a violation. Fix it and return to Step 0. A documented docs-only waiver is not a failure.

### Step 5 — Second pass

Read the diff again without the notes from Step 2. Look only for violations the first pass has a reason to rationalize: a parent import, an `Any`, a model-string comparison, a `unique_id` built from a name, a secret in a fixture, a blocking call in a coroutine, a new dependency, a service field missing from `services.yaml` or `strings.json`.

This pass does not see the self-pass notes. If the tool you are running can start a fresh reader, do that and give it `AGENTS.md`, `.agent/rules/`, and the diff command. If it cannot, re-read the rules from the top before looking at the diff again.

A hit here is a violation. Fix it and return to Step 0.

### Step 6 — Pass

```
✓ /review PASS
  - <N> self-pass violations, fixed across <K> iterations
  - second pass: 0 remaining
  - gate: pass | not installed (docs only)
  → ready for /pr
```

## NEVER

- Skip Step 0 on a later iteration.
- Announce PASS in the same iteration that applied a fix.
- Treat a rule as optional because the inherited file breaks it.
- Use the second pass to confirm the first pass. It exists to refute the first pass.
- Auto-fix past a stop signal in `AGENTS.md` (license, new dependency, unique_id migration, security). Stop and ask.
- Expand the diff with a drive-by refactor so that the review looks cleaner.
