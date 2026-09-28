# cosecloud.com

Source for the Collaborative Science Environment website. Static HTML, no framework.

## Layout

```
src/            page content, one file per page (index, scispinner-max, founders)
src/_partials.py shared header, nav and footer
style.css       all styles; brand tokens at the top
assets/         logo, line drawings, UI screenshots
build.py        assembles src/ + partials into dist/
dist/           build output (deployed by Cloudflare Pages; not committed)
```

## Build

```
python3 build.py
```

Writes `dist/`. Preview locally with `python3 -m http.server -d dist 8000`.

Cloudflare Pages runs the same command on every push to `main` and serves `dist/`.

## Editing

- Page text lives in `src/<page>.body.html`. Edit there, not in `dist/`.
- Nav links and footer are in `src/_partials.py` (`NAV_ITEMS`, `footer()`).
- To add a page: create `src/<name>.body.html` and add an entry to `PAGES` in `build.py`.
- Brand colours come from `07_Sales_Marketing/Brand/Brand_Guide.md`: `#004053` deep teal, `#0F7F9F` primary blue.

## Assets

Line drawings are the CAD line art from the SciSpinner Max manuals, recoloured to brand teal with a transparent background. Screenshots are from the Technical Reference figure set.
