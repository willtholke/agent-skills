---
name: new-skill
description: >-
  Scaffold a new portable skill in willtholke/agent-skills. Use when the user
  invokes /new-skill or asks to add, create, or scaffold a skill in this repo.
disable-model-invocation: true
---

# New skill

Add one skill to this pack. Keep it portable and short.

## Never

- Never add framework tutorials or product house rules
- Never add skills that need private infra or product secrets
- Never ship a new binary when `gh`, `curl`, or an existing skill works
- Never let `SKILL.md` grow past ~100 lines (split detail into `reference.md`)
- Never skip the README Skills table row
- Never invent a skill name that is not kebab-case `[a-z0-9-]+`

## In / Out

| In | Out |
| --- | --- |
| Recurring agent failure modes | Framework tutorials |
| Decision trees + stock shell/`gh` | One-repo style guides |
| Transfers across companies | Private infra / product secrets |

If it would not paste into `AGENTS.md` at three jobs, stop. Keep it local.

## Steps

1. Confirm it belongs (In/Out above). If Out, say so and stop
2. Collect only what is missing: kebab `name`, failure it fixes, trigger (`/` or auto), Never list, numbered steps, stock commands
3. Create `skills/<name>/SKILL.md` from the template below
4. Add a row to the README Skills table (after `new-skill`)
5. Symlink for local try: `ln -s "$(pwd)/skills/<name>" ~/.cursor/skills/<name>`
6. Do not commit or open a PR unless the user asks

## Template

```markdown
---
name: <name>
description: >-
  <what it does>. Use when <trigger>.
disable-model-invocation: true
---

# <Title>

<One or two lines: failure mode + fix>

## Never

- Never …

## Steps

1. …
2. …

## Checklist

- [ ] …
```

Omit `disable-model-invocation` only when the skill should auto-load from ambient context.

## Checklist

- [ ] Passes In/Out
- [ ] `skills/<name>/SKILL.md` exists and is under ~100 lines
- [ ] README Skills table has a Trigger + Does row
- [ ] Related skills linked, not copied
- [ ] Local symlink optional; commit only on request
