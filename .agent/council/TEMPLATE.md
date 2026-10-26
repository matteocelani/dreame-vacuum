# Decision record template

Copy this file to `records/NNNN-kebab-title.md`. Replace every angle-bracket placeholder. Delete this header. Do not leave a section out; write "none" when a section is empty.

```markdown
# NNNN — <question in one line>

- Status: accepted | split | escalated | superseded
- Date: YYYY-MM-DD
- Supersedes: none | NNNN
- Superseded by: none | NNNN

## Brief

**Question.** <one decision>

**Why now.** <what is blocked until this is decided>

**Constraints.** <installed users, Home Assistant floor, HACS, secrets>

**Unknowns.** <facts the brief does not have, or "none">

**Options.**

1. <option, including reversibility>
2. <option>
3. Do nothing. <what stays broken or blocked>

## Positions

### Architect

- Option:
- Owns:
- Because:
- Cost:
- Would change my mind if:

### Pragmatist

- Option:
- User impact:
- Because:
- Cost:
- Would change my mind if:

### Security

- Veto:
- Option:
- Because:
- Cost:
- Would change my mind if:

### Home Assistant conventions

- Option:
- HA surface:
- Because:
- Cost:
- Would change my mind if:

## Rebuttals

### Architect

<one short reply, or "no change">

### Pragmatist

<one short reply, or "no change">

### Security

<one short reply, or "no change">

### Home Assistant conventions

<one short reply, or "no change">

## Verdict

- Recommendation: <option, or "maintainer decides" when split or escalated>
- Rejected: <options and the reason they lost>
- Dissent: <objections still standing, unedited, or "none">
- Security veto: none | resolved | escalated
- Kill criteria: <what we would observe if this was the wrong call>
- Next action: <one pull-request-sized step, or "wait for the maintainer">
```
