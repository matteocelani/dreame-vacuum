---
trigger: manual
---

# /commit

**Triggers:** `/commit`, `@commit`, "make a commit", "save the changes".

## Preconditions

- `git branch --show-current` is not `master`. If it is, stop and create a branch first.
- The change matches one concern. Split unrelated edits before staging.

## Steps

### Step 0 — Read

Read `AGENTS.md` and `.agent/rules/python-quality.md`. On any iteration after a fix, read them again.

### Step 1 — See the diff

```bash
git status
git diff
git diff --staged
```

If there is nothing to commit, stop. Do not create an empty commit.

### Step 2 — Check the rules

Against staged and unstaged diffs, list `file:line — rule` for every violation of `.agent/rules/`. New lines only. A violation is fixed before the commit, and the loop returns to Step 0.

### Step 3 — Gate when the diff contains Python

Run `/gate` when any `.py` file, `manifest.json`, `hacs.json`, `services.yaml`, or `strings.json` changed. A docs-only diff records the waiver and continues. A gate failure returns to Step 0.

### Step 4 — Stage on purpose

Stage the files that belong to this concern. Do not `git add` a file you did not mean to change. Do not stage credentials, local databases, map dumps, or editor metadata.

### Step 5 — Write the message

- Title: `type(scope): subject`, imperative, English, 72 characters or fewer.
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`.
- Scopes: `vacuum`, `map`, `flow`, `entity`, `coordinator`, `protocol`, `cloud`, `tests`, `ci`, `docs`, `agents`.
- Body: why, not a file-by-file retelling. Ten lines is already long.
- An agent-made commit adds the tool's trailer as its own paragraph:

```
Co-Authored-By: Cursor <cursoragent@cursor.com>
```

Use the trailer that names the tool that actually wrote the commit.

### Step 6 — Commit and push

```bash
git commit -m "type(scope): subject" -m "body"
git push -u origin HEAD
```

Do not amend a commit that has been pushed. Do not force-push. If the remote rejects the push, stop and report the rejection.

### Step 7 — Report

```
✓ <hash> <title> → origin/<branch>
```

## NEVER

- Commit on `master`.
- Mix a rule-file change and a behavior change in one commit. The rule changes first.
- Commit a secret, a real map, or a generated archive (`*.zip`).
- Use a message in any language other than English.
- Bypass a hook with `--no-verify`.
