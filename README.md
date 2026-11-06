# Mythra's Mansion

*An eclectic and deranged mistress took over the manor.*

Simple static website. HTML + CSS; no build tools, package manager, or JavaScript required.

## Site map

- `index.html` — foyer (landing page only)
- `library/index.html` — research
- `workshop/index.html` — code and experiments
- `archives/index.html` — academic and personal legacy
- `residents/index.html` — eight resident introductions (clinically diagnosed DID)
- `resources/index.html` — Resource Wing directory (DID, transgender information, mental-health support)
- `resources/did/index.html` — clinical literature and references
- `resources/transgender/index.html` — clinical guidance and research
- `resources/mental-health/index.html` — mental-health support services
- `residents/residents.css` — residents-specific styling
- `resources/resources.css` — resource-specific styling
- `writing/index.html` — writing (intentionally empty for now)
- `about/index.html` — proprietor
- `CSS/style.css` — shared styling for all pages
- `favicon.svg` — browser icon
- `CNAME` — GitHub Pages custom domain; **keep this**

## Preview locally

From the repository root:

```bash
python3 -m http.server 8000
```

Then visit http://localhost:8000/ . Navigate to any room by clicking a link.

## Deploy

`main` is the published branch; `legacy` preserves the original homepage. Create a review branch for future changes. GitHub Pages is expected to publish from `main`.

## Editing notes

- Every room is an ordinary directory with its own `index.html`.
- Each page includes the same navigation and links to `../CSS/style.css`.
- Links are **relative**, so the site works both locally and on GitHub Pages.
- Rooms are intentionally skeletons, not placeholders masquerading as completed work.
- Residents profiles were published by the author; respect their pronouns and descriptions. The Writing Room remains unfinished.
- The homepage introduces the place and provides doors. Project listings and descriptions live inside their rooms.
- Fonts load from Google Fonts with system fallbacks.

## Project inventory (2026-11-06)

The six-category inventory is distributed across the rooms:

- **Library:** Active Research (2); Old Research — Unavailable Codebases (2).
- **Workshop:** Active Projects (2).
- **Archives:** Legacy Projects (1); Course Projects (6); Proprietary Software for ASU (3).

**Total: 16 project entries.** Nine entries have GitHub repository references; some are private or access-restricted. Repository reference links do **not** imply a public code release. Restricted research and ASU course/capstone software are described without uploading their source. CSE340 student coursework with third-party distribution restrictions and the private DIDTest research experiment are deliberately excluded.

The source repository's `legacy` branch preserves the former homepage. Publish `mansion-renovation` to `main` only after explicitly deciding to replace the live site.

## Site validation
Run `python3 scripts/check_site.py` from the repository root to check HTML headings, local paths, anchor targets and duplicate IDs. The script has no external dependencies.
