---
name: github-pr-images
description: >-
  Put screenshots and diagrams into GitHub PR or issue bodies without 404s.
  Use when attaching before/after images, CleanShots, or diagrams to pull
  requests or issues via gh CLI or agent automation.
---

# GitHub PR images

Agents often embed `raw.githubusercontent.com` links in PR bodies. On **private
repos** GitHub's image proxy fetches anonymously and the image 404s. This skill
is the fix: get a URL that renders in markdown, then put `![alt](url)` in the
body.

## Never

- Never use `https://raw.githubusercontent.com/...` for private-repo embeds
- Never commit PR-only screenshots into the product tree unless the user asks
- Never put long-lived auth tokens into a PR body to "make raw URLs work"
- Never use `gh gist create` for binary images (unsupported)

## Preference order

Try the first option that works. Stop when you have a URL that returns HTTP 200
without auth.

1. **Real GitHub attachments** (best: private stays private)

   If `gh image` (extension [drogers0/gh-image](https://github.com/drogers0/gh-image))
   or similar is installed:

   ```bash
   gh image path/to/shot.png --repo owner/repo
   # => ![shot](https://github.com/user-attachments/assets/…)
   ```

   Same URL shape as drag-and-drop in the web UI.

2. **Ephemeral public host** (fine for non-sensitive UI shots)

   Example (Litterbox, ~72h TTL):

   ```bash
   curl -sS -F "reqtype=fileupload" -F "time=72h" \
     -F "fileToUpload=@path/to/shot.png" \
     https://litterbox.catbox.moe/resources/internals/api.php
   # => https://litter.catbox.moe/….png
   ```

   Verify with `curl -sI` → 200 before editing the PR.

3. **Link to a file in the PR** (last resort)

   Commit under something like `.github/pr-assets/` only if the user wants it
   in-repo, and link the blob URL for logged-in viewers. Do not pretend this
   embeds for anonymous/Camo fetches on private repos.

## Wire into the PR

```bash
# create
gh pr create --title "…" --body "$(cat <<'EOF'
## Summary
…

## Before
![Before](URL_HERE)

## Test plan
- [ ] …
EOF
)"

# or update
gh pr edit <n> --body "…"
```

One image → one markdown line. Prefer a short `## Before` / `## After` section.

## Privacy

| Backend | Visibility |
| --- | --- |
| `user-attachments` via `gh image` | Inherits repo visibility |
| Litterbox / catbox / similar | Public to anyone with the URL |
| Committed `.github/pr-assets/` | Repo visibility; embed still broken on private via Camo |

Do not upload credentials, customer data, or internal dashboards to public hosts.

## Quick checklist

- [ ] Image file exists locally
- [ ] Upload path chosen from preference order
- [ ] URL returns 200 without cookies
- [ ] Body uses `![alt](url)`, not a raw private GitHub URL
- [ ] No product-tree PNG commit unless requested
