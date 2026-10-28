---
trigger: manual
---

# /upstream-sync

**Triggers:** `/upstream-sync`, "sync upstream", "port Tasshack".

Brings new commits from Tasshack/dreame-vacuum onto this fork, oldest first, with attribution. The fork keeps full Dreame, MOVA, Mijia, and TROUVER support and keeps its own Xiaomi work. Merging `upstream/master` is not this command.

## Preconditions

- The working tree is clean.
- No open pull request from a `sync/upstream-*` branch. Resume that pull request instead of starting another.
- Read `AGENTS.md`, this file, `.agent/council/records/0004-family-bases.md`, `.agent/rules/security.md`, `.agent/rules/tests.md`, and `.agent/commands/gate.md`.

## State

`.agent/upstream-sync.json` is the only record of the last upstream commit this fork has finished classifying. Read it at the start. Do not copy the SHA into this file. The keys are exactly these:

- `upstream_url` — `https://github.com/Tasshack/dreame-vacuum`
- `upstream_branch` — upstream's default branch
- `last_synced_sha` — the full upstream commit already classified
- `last_synced_date` — `YYYY-MM-DD`, the date this fork recorded that sync

The seeded SHA is the upstream tip merged by pull request #1 on 2026-10-26 (`Merge pull request #1 from Tasshack/master`). It is that merge's second parent. Later runs trust the file.

## Steps

1. Fetch. Add the `upstream` remote at `upstream_url` when it is missing. When it exists and points somewhere else, stop. Fetch `upstream_branch`, including tags. Do not fetch into `master`. Pin the tip with `git rev-parse upstream/<branch>` and use that pin for the rest of the run.

2. Range. `$LAST` is `last_synced_sha`. Stop when that commit is missing, or when it is not an ancestor of the pinned tip. List every commit after it, oldest first, and every tag and GitHub release whose commit is in that range:

```bash
git log --reverse --format='%H %s' "$LAST"..upstream/"$BRANCH"
```

Releases come from `gh release list` on `Tasshack/dreame-vacuum`, kept only when the tag commit is in the range. When the log is empty, stop. Do not create a branch, do not open a pull request, and do not edit the state file. Report `$LAST` and that upstream has nothing new.

3. Branch. Update `origin/master` and create `sync/upstream-YYYY-MM` from it, using the UTC month the sync starts. This command authorizes the `sync/` prefix. Never commit on `master`. Never force-push `master`.

4. Classify every commit in the range before editing a product file. The class is one of: bug fix, new Dreame model or mapping, feature, refactor, translations, CI/meta, not applicable. For each commit, write what it changes and which files in this fork the diff hits, including a file a cherry-pick would conflict on. A commit that fits none of the classes is `not applicable`. Do not invent a class. Record the collected count from `pytest --collect-only -q` before the first port.

5. Port oldest first. One upstream commit becomes one commit on the branch. Read the upstream path list before applying it. Cherry-pick with `git cherry-pick -x <sha>` only when the path list does not touch a path that is ours and the pick applies with no conflict. Any conflict aborts the pick. A hunk on a path that is ours is re-implemented by hand, or the commit is skipped. Do not pass `-X ours` or `-X theirs`, and do not take a whole file from either side.

   The message names the upstream change and ends with both of these lines. The name and email come from that upstream commit:

```
Upstream: <full sha>
Co-authored-by: <name> <email>
```

   Add them with `git commit --amend` only while the port commit is still unpushed. An agent port also adds the `/commit` agent trailer. That trailer does not replace the two lines above.

6. Conflict policy.

   Ours, and never replaced by the upstream file: the Xiaomi package, the shell adapter that exposes it, the family resolver, the family codec, agent docs, council records, this state file, CI workflows, the test suite, and the fork README's attribution, domain statement, and Xiaomi scope. An upstream edit to a shared shell or Dreame file is adapted so those pieces stay. The file is not checked out from upstream.

   Upstream Dreame behavior wins only inside upstream-owned Dreame code: the catalog, the Dreame device core, map decoding, Dreame cloud and local transport, and Dreame translations. It wins only after the Xiaomi base still behaves the same. Where both bases run the same function, the Xiaomi capability lists, derived flags, and entity contracts stay as the tests freeze them. When the Dreame fix and that Xiaomi result cannot both be kept, skip the commit or mark it `needs council`. Do not invent a blend.

   Never delete a fork feature, model, test, or assertion to get past a conflict. Leave the MIT license and its Tasshack copyright notice as they are.

   Do not port a commit that would change the Home Assistant domain, config-entry storage, an entity `unique_id`, a device identifier, or a service schema, or that would change what council 0004 protects. Status is `needs council`. Do not convene the council inside this command. A later commit that depends on one of these gets the same status, or `skipped`, and the reason names the blocking SHA.

   A commit that cannot be ported without a silent behavior change is `skipped`, with a reason a reviewer can check. Do not port a token, password, account id, cookie, real device id, or map dump that arrived in an upstream diff.

7. Gate after every ported commit. Consecutive commits that share one class and one upstream concern may share one gate after the last of them. A failed group is bisected, and the bad commit is fixed or reverted before the next concern starts. The gate is `python -m pytest`, then Ruff check and Ruff format check on the paths `.github/workflows/xiaomi-tests.yaml` already lints. Do not aim Ruff at the rest of the inherited tree, and do not drop a path from that list. When the port changed `manifest.json`, `hacs.json`, `strings.json`, `services.yaml`, or the platform list, hassfest on the pull request has to pass. Run hassfest locally only when the executable is already installed. Otherwise record `hassfest: CI only`. Do not install a checker to manufacture a local pass.

   On a red gate, fix that port or revert it before moving on. A reverted port stays in the report as `skipped`, with the failure named. Do not add a skip, a coverage exclusion, or a Ruff ignore to get green.

8. Regression, once, after the last port and before the state-file commit. The collected count is at least the count from step 4. The coverage rules in `.agent/rules/tests.md` still hold. Every Xiaomi model still resolves with the same entity counts: the expected capability lists and entity contracts under `tests/xiaomi/` are unchanged, and those tests pass. Editing an expected value so a port goes green is a failed regression. Revert that port.

9. State and pull request. Set `last_synced_sha` to the pin from step 1 and `last_synced_date` to the UTC date of this sync. Commit that on the same branch. Open one pull request titled `Upstream sync YYYY-MM`. The body tables every commit in the range: SHA, title, classification, status (`ported`, `adapted`, `skipped`, or `needs council`), and reason. A blank reason fails the step. Under the table, put the collected counts before and after, and the CI status of the Xiaomi workflow and of hassfest. `validate-hacs` fails on repository settings and is ignored. Say that in the body. Do not try to make that check green.

10. Merge. Put every `needs council` row in a blocker list at the top of the body, with the SHA and the rule it hit. A row missing from that list is unflagged, which is itself a blocker. Squash-merge is allowed only when the final head has a green Xiaomi workflow and a green hassfest run, the blocker list is empty, and no test was removed or weakened. The squash message keeps every `Upstream:` line and every upstream `Co-authored-by` trailer. This step is the only waiver of "the author does not merge", and it applies only to that squash. A `needs council` row leaves the blocker list only after `/council` has an accepted record that cites the SHA. Resume this branch, link that record, and either port the commit or mark it `skipped` with the link. Do not relabel it without the record. When any merge condition fails, leave the pull request open.

## Done

- Upstream had nothing after `last_synced_sha`, and the tree is unchanged. Or one pull request carries every port, the table, both test counts, and the new SHA.
- Every `needs council` commit is in the table and in the blocker list. The pull request stays open while that list is non-empty, or while the Xiaomi workflow or hassfest is not green.
- No path that is ours was replaced by the upstream file.

## NEVER

- `git merge upstream/master`, or rebase `master` onto upstream.
- Commit on `master`, or force-push `master`.
- Replace the Xiaomi package, the family resolver or codec, agent docs, councils, CI, or tests with the upstream copy.
- Delete or weaken a fork test, or drop a Xiaomi model, to finish a port.
- Port a domain, storage, `unique_id`, device-identifier, service-schema, or council 0004 change before an accepted council record cites that upstream SHA.
- Advance `last_synced_sha` on `master` except by merging this pull request.
- Drop a commit from the table, or relabel `needs council` as `skipped` without that council record.
- Report a gate, a test count, or a CI check that did not run.
