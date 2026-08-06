---
name: new-skill
description: >-
  Use when scaffolding, adding, or refining a skill in willtholke/agent-skills
  (/new-skill, "add a skill", "scaffold a skill", "update this skill"). Does:
  Need → Evals → Route → thin hub → spokes → wire → append gotchas. Not when
  writing human docs, one-repo house rules, or private-infra runbooks.
disable-model-invocation: true
---

# New skill

Scaffold or refine one skill in this pack. Skills are context for models, not
docs for humans.

- **Format:** [Agent Skills spec](https://agentskills.io/specification) +
  [best practices](https://agentskills.io/skill-creation/best-practices)
- **Process:** [Perplexity on Agent Skills](https://research.perplexity.ai/articles/designing-refining-and-maintaining-agent-skills-at-perplexity)

## Never

- Never add a skill the bare agent already gets right (every skill is a context tax)
- Never write a description that only summarizes the workflow; it is a routing trigger (what + when)
- Never one-shot via LLM with no domain context; extract from a real task, then inject opinion
- Never recapitulate git/`gh`/`curl` sequences the model already knows
- Never change a merged skill's description without positive + negative load cases
- Never dump conditional/heavy content into `SKILL.md`; use spokes
- Never default-disable ambient skills; omit `disable-model-invocation` when auto-load is intended
- Never add framework tutorials, one-repo house rules, or private-infra skills
- Never skip the README Skills table row
- Never use a name that is not kebab-case matching the folder

## In / Out

| In | Out |
| --- | --- |
| Agent gets it wrong or inconsistent without special context | Model already knows it |
| Durable know-how, taste, or enterprise workflow | Fast-changing remote APIs / MCP tool lists |
| Decision trees + stock tools + gotchas | Human README-style command walkthroughs |
| Transfers across companies | Product secrets / private infra |

Test each sentence: "Would the agent get this wrong without it?" If no, delete it.

## Steps

1. **Need** – Run a few hero queries without the skill. Only proceed if it fails or flops.
2. **Evals first** – List load cases before writing body:
   - Positive: real user phrasings that must load
   - Negative: near-miss intents that must not load
   - Neighbor: adjacent skills that must stay distinct
3. **Description (route)** – Hybrid **what + when**. Soft ≤50 words; hard ≤1024 chars (spec). Pattern: `Use when… Does… Not when…`. Prefer user frustration phrases ("screenshots 404", "babysit CI") over internals. See [optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions).
4. **Body** – Intent + constraints + **Never/gotchas**. Skip the obvious. **Freedom calibration:** prescribe fragile sequences; give freedom + why when approaches vary. Prefer "cherry-pick onto a clean branch; preserve intent" over command railroads.
5. **Hierarchy** – Hub `SKILL.md`: soft ~100 lines; hard <500 lines / ~5k tokens (spec). Spokes:
   - `scripts/` – deterministic code the agent should run, not reinvent
   - `references/` – heavy docs ("read X if …")
   - `assets/` – templates/schemas to copy
6. **Wire** – Folder name = frontmatter `name`. README Skills row (after `new-skill`). Optional: `ln -s "$(pwd)/skills/<name>" ~/.cursor/skills/<name>`. Validate: `skills-ref validate ./skills/<name>` when available.
7. **Outcome eval (optional)** – For non-trivial skills, run a few end-to-end tasks and grade output quality; see [evaluating skills](https://agentskills.io/skill-creation/evaluating-skills).
8. **Iterate** – Append gotchas when the agent fails. Tighten description only with new load cases. Do not commit/PR unless asked.

## Slash vs ambient

| Kind | Frontmatter | When |
| --- | --- | --- |
| Slash / explicit only | `disable-model-invocation: true` | User must invoke (`/ship`, `/new-skill`) |
| Ambient | omit the field | Agent may auto-load from description match |

Do **not** default every skill to disabled. Only slash skills that would be harmful or noisy if ambient.

## Template

```markdown
---
name: <name>
description: >-
  Use when <user intent / real phrases>. Does: <what>. Not when <near-miss>.
# disable-model-invocation: true   # only for slash-only skills
# compatibility: <env requirements if any>
---

# <Title>

<Failure mode the bare agent hits + the fix>

## Never

- Never …   # gotchas; highest-value lines; grow over time

## Steps

1. …        # intent + constraints; calibrate freedom vs prescription

## Load cases

- Positive: …
- Negative: …
- Neighbor: …
```

## Maintain

Skills are append-mostly. Prefer new gotchas over longer instructions.

| Signal | Action |
| --- | --- |
| Agent fails mid-skill | Add a gotcha |
| Off-target load | Tighten description + negative cases |
| Missed load | Add intent keywords + positive cases |
| Description change after merge | Require updated load cases first |

## Checklist

- [ ] Bare agent fails the hero queries without it
- [ ] Description is hybrid what+when (soft ≤50 words, hard ≤1024 chars)
- [ ] Positive, negative, and neighbor load cases written
- [ ] Body skips what the model knows; gotchas present; freedom calibrated
- [ ] Hub soft ~100 lines / hard <500; heavy content in spokes
- [ ] Slash vs ambient chosen deliberately (no blind disable)
- [ ] README row + folder name matches `name`
- [ ] Related skills linked, not copied
- [ ] Optional: `skills-ref validate` + outcome evals for non-trivial skills
