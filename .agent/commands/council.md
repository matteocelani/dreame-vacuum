---
trigger: manual
---

# /council

**Triggers:** `/council`, "convene the council", "we need a decision on".

Runs the decision process in [`.agent/council/README.md`](../council/README.md). The product is a decision record. It is not the implementation.

## Preconditions

- The question matches a trigger in the council README. If it is a model row, an entity, a bug fix, or a docs edit, refuse this command and name the command that applies (`/add-device`, `/add-entity`, `/review`).
- The question is one decision. Two questions are two councils.
- No role file is edited as part of answering. A role change is its own pull request.

## Steps

1. Read `AGENTS.md`, `.agent/council/README.md`, and all four files in `.agent/council/roles/`.
2. Write the brief: the question, why it is in front of the council now, the constraints (installed users, minimum Home Assistant version, HACS packaging, secrets), at least two options including "do nothing", and how reversible each option is.
3. Write the four positions in the order Architect, Pragmatist, Security, Home Assistant conventions. Finish each position before starting the next. Do not revise an earlier position after reading a later one. Each position uses the format in the council README and stays inside that role's mandate.
4. Rebuttal round. Each role may write one short reply and may change its stated option once. A change cites the role that caused it. Security's veto, if raised, is not bargained away in this round. It is resolved only by changing the proposal so the veto condition is gone, or by escalating.
5. The chair writes the verdict: recommendation, what was rejected, dissent that is still standing, whether a Security veto is none / resolved / escalated, the kill criteria, and one next action small enough for a single pull request.
6. If the options split 2–2 and neither side has a veto to resolve, status is `split`. Do not average the positions into a third design nobody wrote.
7. Save the record from `.agent/council/TEMPLATE.md` to `.agent/council/records/NNNN-kebab-title.md`. `NNNN` is the next free four-digit id. Status is `accepted` or `split`. Commit the record by itself, via `/commit`, with scope `agents`.

## Done

- The record is in the tree, with a brief, four positions, rebuttals, and a verdict.
- No product code changed in that commit.
- The next action is one sentence a later pull request can follow, or an explicit "maintainer decides" when the status is `split`.

## NEVER

- Convene the council to bless a decision that was already implemented on the branch.
- Skip a role because the answer feels obvious. Obvious answers are short, not silent.
- Invent a fifth role, a guest persona, or a historical figure.
- Treat the verdict as permission to ignore a stop signal the verdict did not explicitly lift.
- Edit an accepted record to change its verdict. Supersede it with a new record.
