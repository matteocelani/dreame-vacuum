---
trigger: manual
---

# /pr

**Triggers:** `/pr`, `@pr`, "open a pull request", "open the PR".

## Preconditions

- `/commit` has been run. The working tree is clean.
- The branch is not `master`, and it is ahead of `origin/master`.
- A council record exists and is linked when `AGENTS.md` required one for this change.

## Steps

### Step 0 — Read

Read `AGENTS.md` and `.agent/commands/code-review.md`.

### Step 1 — Review

Run `/review` to a PASS. If it fixes anything, it will have committed or it will leave a dirty tree: commit via `/commit` before continuing. Do not open the pull request from a dirty tree.

### Step 2 — Rebase

```bash
git fetch origin
git rebase origin/master
```

On a conflict, stop and ask. Do not resolve a conflict in `custom_components/` by taking "ours" or "theirs" wholesale.

### Step 3 — Push

Push the branch. If the rebase rewrote commits, `git push --force-with-lease` is the only acceptable force. Never `--force` alone.

### Step 4 — Confirm CI scope

If the change touches `manifest.json`, `hacs.json`, `strings.json`, `services.yaml`, or the platform list, say in the body that hassfest and HACS validation are required and have not been waived. Do not merge before they are green. The author of the pull request does not merge it anyway.

### Step 5 — Title and body

Title: imperative, 72 characters or fewer, the same Conventional Commit shape as the commit when there is one commit. An umbrella title when there are several, still `type(scope): subject`.

Body, in English:

- **Summary.** What changed and why, in two or three sentences.
- **Changes.** The substantive points. Three to six bullets. Do not narrate the diff file by file.
- **Gate.** The `/gate` outcome, including coverage for any new device-core module, or the docs-only waiver.
- **Council.** A link to the decision record, when one exists. Omit the section otherwise.
- **Risk.** Only if there is a real one: migration, unique_id, dependency, cloud transport. Omit when there is nothing to say.

An agent-opened pull request ends with the tool attribution line, for example `Co-Authored-By: Cursor <cursoragent@cursor.com>`.

### Step 6 — Open

Target `master`.

```bash
gh pr create --base master --head "$(git branch --show-current)" \
  --title "..." --body "..."
```

If the repository's pull request tool is different from `gh`, use that tool, still with base `master`. Do not invent labels the repository does not have. Do not assign a random reviewer.

### Step 7 — Stop

Report the pull request URL. Do not merge. Do not start the next feature on this branch.

## NEVER

- Open a pull request that `/review` did not pass.
- Target anything other than `master`.
- Mix two concerns to "save a review".
- Force-push over a reviewer's commits.
- Edit the pull request into a different scope after review started. Open a new branch.
