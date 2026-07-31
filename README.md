# Agent Skills

Agent-first engineering skills for Cursor and other agents that speak [Agent Skills](https://agentskills.io).

No CLIs to install. No frameworks. Short `SKILL.md` packs that fix workflows agents keep getting wrong.

## Install

**skills.sh (recommended)**

```bash
npx skills add willtholke/agent-skills
```

**Cursor UI**

1. Customize → Rules → Add Rule → Remote Rule (GitHub)
2. Paste `https://github.com/willtholke/agent-skills`

**Manual**

```bash
git clone https://github.com/willtholke/agent-skills.git
mkdir -p ~/.cursor/skills
ln -s "$(pwd)/agent-skills/skills/github-pr-images" ~/.cursor/skills/github-pr-images
```

## Skills

| Skill | When to use |
| --- | --- |
| [github-pr-images](skills/github-pr-images/) | Screenshots or diagrams in GitHub PR / issue bodies |

## What belongs here

| In | Out |
| --- | --- |
| Recurring agent failure modes | Framework tutorials |
| Decision trees + stock shell / `gh` | Product-specific house rules |
| Skills that transfer across companies | Skills that need your private infra |

If you would paste it into `AGENTS.md` at three jobs, it belongs. If it is one repo's style guide, keep it local.

## Contributing

One skill = one folder under `skills/<name>/SKILL.md`. Keep the main file under ~100 lines. Prefer teaching agents to use existing tools over shipping new binaries.

## License

[MIT](LICENSE)
