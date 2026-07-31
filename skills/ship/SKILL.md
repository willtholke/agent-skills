---
name: ship
description: >-
  Verify, open a PR, wait for green checks and a preview deploy, merge, then
  smoke-test production. Use only when the user explicitly invokes /ship or
  asks to release, push to production, or ship through the full PR workflow.
disable-model-invocation: true
---

# Ship

Take local work to a verified production release through GitHub. Never direct-deploy
to production (`vercel --prod`, manual promote, etc.) unless the user explicitly
overrides this workflow.

Normal path:

`feature branch → PR → green checks + preview → merge → production → smoke test`

Once every gate is green, merge without asking for a second confirmation.

## Never

- Never force-push, bypass branch protection, or weaken tests/lint/CI to land
- Never commit secrets, credentials, local caches, or unrelated dirty files
- Never add `Co-authored-by: Cursor`, `cursoragent@cursor.com`, or Made-with Cursor
- Never merge while required checks are pending, failing, or unexpectedly skipped
- Never auto-rollback production; stop, report, recommend, ask

## 1. Release context

From the repo root, establish:

- default branch, current branch, upstream, full diff vs default
- package manager (lockfile) and declared lint / typecheck / test / build scripts
- PR template if present
- deploy host (Vercel when linked; otherwise whatever CI/docs say)

If ambiguous untracked or unrelated changes exist, ask one focused question. Do not
discard them.

## 2. Local gates

Use the project's package manager and scripts. Do not invent checks the repo lacks.

Run all that exist, in order: install/lockfile → format → lint → typecheck → tests →
production build. Fix failures caused by this release and rerun. Stop on pre-existing
unrelated failures and report them.

## 3. Pull request

If on the default branch, create a focused feature branch first.

1. Granular commits in the repo's style
2. Push without force
3. Create or update the PR (template + summary + exact test plan)
4. Wait for GitHub checks and the preview deployment
5. Fix valid review findings; rerun affected checks after each push

For screenshots in the PR body, use the `github-pr-images` skill.

## 4. Verify preview

Confirm the preview matches the PR's current HEAD SHA.

- Deploy status READY (or host equivalent)
- Preview URL returns success
- Critical changed routes / primary interactions work
- No release-blocking runtime errors in deploy logs

Prefer the host's MCP or CLI when available; otherwise use GitHub check details.
Never print tokens or env values.

## 5. Merge and watch production

Immediately before merge, restate: PR link, branch, HEAD SHA, local gates, CI,
preview URL, smoke result, residual risk.

Then:

1. Merge with the repo's allowed strategy
2. Record the merge SHA
3. Watch production deploy until READY or ERROR; confirm source commit = merge SHA
4. Smoke-test homepage + changed critical routes
5. Scan recent production logs for release-blocking errors

## Final report

```text
Production: LIVE | FAILED
URL: <production-url>
Commit: <sha>
PR: <link>
Checks: <green summary or failure>
Preview/Deploy: READY | ERROR
Smoke test: PASS | FAIL
```

Lead with that block. Add only actionable warnings and next steps.
