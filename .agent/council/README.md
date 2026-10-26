# Council

A small, written deliberation for decisions that are expensive to undo. Four roles, two rounds, one record. No plugins, no extra model providers, no standing meetings.

The procedure an agent runs is [`.agent/commands/council.md`](../commands/council.md). This file is the contract that command follows. Role mandates live in [`roles/`](roles/).

## When to convene

Convene the council before work starts, when the change would do any of the following:

- Add a package inside the integration, or a new top-level directory in the repository.
- Introduce a second device family, or a shared abstraction meant for more than the family that exists.
- Rename the integration domain, or split or merge HACS components.
- Change config-entry data, entity `unique_id`s, device-registry identifiers, event payloads, or a service schema.
- Add a runtime dependency, or raise the minimum Home Assistant version in `hacs.json`.
- Change authentication, the cloud transport, TLS verification, or the diagnostics redaction list.
- Pick an architecture the rules do not already decide, or resolve a contradiction between two rule files.

## When not to

Do not convene the council for:

- A model row added through `/add-device`.
- An entity added through `/add-entity`.
- A bug fix that restores behavior the rules already describe.
- Formatting, tests, documentation, or a rule clarification that does not change the rule's meaning.
- A choice that a one-commit revert can undo without touching user data.

If you are unsure, look at the cost of being wrong. A wrong entity description is a follow-up commit. A wrong `unique_id` scheme orphans history in every installation. The second one is a council.

## Roles

| Role | File | Optimizes for |
| --- | --- | --- |
| Architect | `roles/architect.md` | Boundaries that still hold with many device families |
| Pragmatist | `roles/pragmatist.md` | The installed base and the smallest change that does not block that future |
| Security | `roles/security.md` | Credentials, floor plans, and the supply chain. Has a veto |
| Home Assistant conventions | `roles/ha-conventions.md` | What a config entry, a coordinator, and an entity must do to be a good citizen |

The chair is the agent running the command. The chair does not get a vote and does not add a fifth opinion in the verdict. The chair writes down what the four roles actually concluded.

## Rounds

1. **Brief.** One decision, the constraints, two or more options including "do nothing", and how hard each option is to reverse. Facts the brief does not have are written as unknowns, not filled in with guesses.
2. **Independent positions.** Each role answers from its file, in the order Architect, Pragmatist, Security, Home Assistant conventions. A position is written to completion before the next role is started, and earlier positions are not edited afterward. A role that agrees with another role still writes its own reason.
3. **Rebuttal.** One short reply per role. A role may switch its chosen option once, and must name who changed its mind. This is the only revision allowed.
4. **Verdict.** The chair applies the decision rule below and fills in the record template.

Keep each position short. If a role needs more than half a page, it is arguing two decisions.

## Decision rule

- **Security veto.** Security may veto a proposal that ships a secret, weakens TLS, logs credentials, expands diagnostics with household data, or adds an unreviewed dependency with a known compromise path. A veto blocks `accepted`. Either the proposal changes until Security withdraws the veto, or the status is `escalated` and the maintainer has to override it in writing. Silence is not a withdrawal.
- **Accepted.** Three or four roles support the same option, and Security has not vetoed it. The dissenting role's objection is copied into the verdict unchanged.
- **Split.** The roles are 2–2, or two incompatible options each have support and no veto resolves it. Status is `split`. The maintainer decides. The chair must not invent a hybrid both sides can "live with" unless a role actually proposed that hybrid in its position or its rebuttal.

## Decision records

Copy [`TEMPLATE.md`](TEMPLATE.md) to `records/NNNN-kebab-title.md`. `NNNN` is the next free number, starting at `0001`.

Records are append-only. A typo fix is fine. A changed verdict is a new record whose brief links the old one, and the old record's status becomes `superseded`. Deleting a record is forbidden.

The implementation pull request links the record and stays inside the next action the verdict named. An implementation that needs a wider change convenes the council again instead of stretching the old verdict.

## Status values

| Status | Meaning |
| --- | --- |
| `accepted` | The next action may be implemented |
| `split` | The maintainer has to choose. Do not implement yet |
| `escalated` | A Security veto is unresolved |
| `superseded` | A later record replaced this one |
