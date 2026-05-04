# Status — worldmachines

## Active
- Testing end-to-end submission pipeline with collaborators

## Upcoming
- Style polish on index page
- Consider pagination or filtering as article count grows
- Decide whether to surface extracted full text on article detail pages
- Add www → worldmachines.org redirect if needed

## Done
- **2026-05-04** — Full pipeline live: form → Cloudflare Access gate → Pages Function → GitHub Actions ingest → Cloudflare Pages deploy
- **2026-05-04** — Handle registry: email→handle KV lookup, `/admin/handles` web UI (Access-protected, admin-only)
- **2026-05-04** — Cloudflare Access: `/submit` + `/api/submit` gated for approved collaborators; `/admin*` gated for admin only
- **2026-05-04** — Custom domain worldmachines.org live on Cloudflare Pages
- **2026-05-04** — GitHub org at github.com/worldmachines, repo worldmachines/worldmachines
- **2026-05-04** — Project initiated: folder, CLAUDE.md, status.md, git repo, dashboard registration
