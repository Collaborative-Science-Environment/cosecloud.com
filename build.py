#!/usr/bin/env python3
"""Assemble the COSE site: src/*.body.html + shared partials -> dist/.

Usage: python3 build.py   # writes dist/ (deployed by Cloudflare Pages)
"""
import shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from _partials import head, nav, footer  # noqa: E402

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

PAGES = {
    "index": dict(title="CoSE — SciSpinner Max two-axis clinostat",
                  description="Collaborative Science Environment builds the SciSpinner Max, a two-axis clinostat for simulated-microgravity research. Designed and built in Madison, Wisconsin.",
                  current="home"),
    "scispinner-max": dict(title="SciSpinner Max — specifications and software",
                           description="Two independent axes, 167 mm sample chamber, onboard camera, lighting and sensors, measured time-averaged gravity. Full specifications for the SciSpinner Max clinostat.",
                           current="product"),
    "founders": dict(title="About CoSE",
                     description="The people behind Collaborative Science Environment: a science educator, a plant scientist and an engineer in Madison, Wisconsin.",
                     current="founders"),
}

def page(name, meta, skeleton=True):
    body = (ROOT / "src" / f"{name}.body.html").read_text()
    inner = f"{head(meta['title'], meta['description'])}\n{nav(meta['current'])}\n{body}\n{footer()}"
    if not skeleton:
        return inner
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            f"{inner}\n</body>\n</html>\n").replace(f"{head(meta['title'], meta['description'])}\n", f"{head(meta['title'], meta['description'])}\n</head>\n<body>\n", 1)

def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copy(ROOT / "style.css", DIST / "style.css")
    shutil.copytree(ROOT / "assets", DIST / "assets", ignore=shutil.ignore_patterns("*.txt", "logo.svg", "mark.svg"))
    (DIST / "_headers").write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n")
    (DIST / "_redirects").write_text(
        "/shop/ / 301\n/shop / 301\n/researchers/ /scispinner-max 301\n/teachers/ /founders 301\n"
        "/students/ /founders 301\n/the-cose-team/ /founders 301\n/blog/ / 301\n/cart/ / 301\n"
        "/index.html / 301\n/scispinner-max.html /scispinner-max 301\n/founders.html /founders 301\n")
    for name, meta in PAGES.items():
        (DIST / f"{name}.html").write_text(page(name, meta))
    print("built", sorted(p.name for p in DIST.iterdir()))

if __name__ == "__main__":
    main()
