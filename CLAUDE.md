# worldmachines

> **Environment rules, keys & safety policies:** see [Code/CLAUDE.md](../CLAUDE.md) — read before starting work.

Collaborative project to develop psychohistorical models based on Venkatesh Rao's world machines theory. Initially a static website on Cloudflare Pages that aggregates links to articles submitted by collaborators via a Google Form.

## Stack

- Static HTML · CSS · JS
- Cloudflare Pages (hosting)
- Google Forms (article submission intake)
- No build step — deploy directly from repo

## Structure

```
index.html       # main site
style.css
js/
assets/
```

## Workflow Notes

- Git repo: yes. Branch: `main` for production, feature branches for larger changes.
- Deployed via Cloudflare Pages connected to GitHub repo.
- Article submissions collected via Google Form; initially curated manually into the site.

## Status

See [`status.md`](status.md).
