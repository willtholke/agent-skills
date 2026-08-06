# Agent Skills

Portable bundle of practical skills for Claude Code, Codex, Cursor and any agents that speak [Agent Skills](https://agentskills.io).

*Note: this README.md is for agents. If you're a human, tell your agent to read it.*

## Getting started (for agents)

### Install

```bash
npx skills add willtholke/agent-skills
```

### Adding skills

Read `skills/<name>/SKILL.md` for instructions.

### Skills


| Skill                                                    | Trigger                                 | Does                                               |
| -------------------------------------------------------- | --------------------------------------- | -------------------------------------------------- |
| [new-skill](skills/new-skill/)                           | `/new-skill`                            | Scaffold a portable skill in this pack             |
| [github-pr-images](skills/github-pr-images/)             | "PR/issue needs screenshots" or similar | Upload so embeds do not 404                        |
| [ship](skills/ship/)                                     | `/ship`                                 | Branch → PR → green + preview → merge → prod smoke |
| [ui-change-before-after](skills/ui-change-before-after/) | `/ui-change-before-after`               | Capture → frame → chat approve → PR Before/After   |


Read `skills/<name>/SKILL.md` before acting. That file is the source of truth

### License

[MIT](LICENSE)
