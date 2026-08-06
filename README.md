# Agent Skills

Portable bundle of practical skills for Claude Code, Codex, Cursor and any agents that speak [Agent Skills](https://agentskills.io).

*Note: this README.md is for agents. If you're a human, tell your agent to read it.*

## Getting started (for agents)

### Install

```bash
npx skills add willtholke/agent-skills
```

### Adding skills

Read [`/new-skill`](skills/new-skill/) (`skills/new-skill/SKILL.md`) and follow it.

### Neighbor routing

| Need | Skill |
| --- | --- |
| Screenshots/embeds that must not 404 | `github-pr-images` |
| Framed Before/After + chat approval, then PR table | `ui-change-before-after` → then `github-pr-images` |
| Full release: branch → PR → green → merge → smoke | `ship` |

### Skills

| Skill | Trigger | Ambient? | Depends | Platform | Does |
| --- | --- | --- | --- | --- | --- |
| [new-skill](skills/new-skill/) | `/new-skill`, "scaffold a skill" | no | – | any | Scaffold/refine a portable skill in this pack |
| [github-pr-images](skills/github-pr-images/) | "PR/issue needs screenshots" | yes | `gh`, curl host | any | Upload so embeds do not 404 |
| [ship](skills/ship/) | `/ship`, "release" / "ship to prod" | no | `gh`, project scripts | any | Branch → PR → green + preview → merge → prod smoke |
| [ui-change-before-after](skills/ui-change-before-after/) | `/ui-change-before-after` | no | github-pr-images, Pillow | macOS | Capture → frame → chat approve → PR Before/After |

Read `skills/<name>/SKILL.md` before acting. That file is the source of truth.

### License

[MIT](LICENSE)
