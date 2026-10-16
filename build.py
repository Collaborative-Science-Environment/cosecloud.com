#!/usr/bin/env python3
"""Assemble the COSE site: src/*.body.html + shared partials -> dist/.

Usage: python3 build.py   # writes dist/ (deployed by Cloudflare Pages)
"""
import shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from _partials import head, nav, footer, logo_svg  # noqa: E402
import _news  # noqa: E402

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
POSTS = _news.load_posts(ROOT)

PAGES = {
    "index": dict(title="CoSE — research instruments for gravitational biology",
                  description="Collaborative Science Environment designs and builds clinostats and time-lapse imaging instruments for gravitational biology. Madison, Wisconsin.",
                  current="home"),
    "scispinner-max": dict(title="SciSpinner Max — specifications and software",
                           description="Two independent axes, 167 mm sample chamber, onboard camera, lighting and sensors, measured time-averaged gravity. Full specifications for the SciSpinner Max clinostat.",
                           current="product"),
    "tools": dict(title="Tools — CoSE",
                  description="Browser-based tools for SciSpinner data: g-level analysis of motion-sensor logs, with more to come. Everything runs locally; nothing is uploaded.",
                  current="tools", out="tools/index.html"),
    "accessories": dict(title="Accessories and parts — CoSE",
                        description="Spare Control Modules, extended cables, sample inserts and replacement parts for the SciSpinner Max, with US list prices.",
                        current="accessories"),
    "founders": dict(title="About CoSE",
                     description="The people behind Collaborative Science Environment: a science educator, a plant scientist and an engineer in Madison, Wisconsin.",
                     current="founders"),
}

def page(name, meta, skeleton=True, body=None):
    if body is None:
        body = (ROOT / "src" / f"{name}.body.html").read_text()
    if "{MAP}" in body:
        body = body.replace("{MAP}", (ROOT / "src" / "_map.svg").read_text())
    if "{NEWS}" in body:
        body = body.replace("{NEWS}", _news.home_block(POSTS))
    inner = f"{head(meta['title'], meta['description'])}\n{nav(meta['current'])}\n{body}\n{footer()}"
    if not skeleton:
        return inner
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            f"{inner}\n</body>\n</html>\n").replace(f"{head(meta['title'], meta['description'])}\n", f"{head(meta['title'], meta['description'])}\n</head>\n<body>\n", 1)

TOOL_BAR = """<style>
.cose-bar{font:14px/1 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:10px 16px;border-bottom:1px solid #e2e5e8;background:#fff}
.cose-bar a{color:#4b5560;text-decoration:none}.cose-bar a:hover{color:#0F7F9F}
.cose-bar .brand svg{height:26px;width:auto;display:block}.cose-bar .brand .wm{fill:#004053}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .cose-bar{background:#14171a;border-color:#2c3238}:root:not([data-theme="light"]) .cose-bar a{color:#b8c0c8}:root:not([data-theme="light"]) .cose-bar .brand .wm{fill:#DCEBF0}}
@media print{.cose-bar{display:none}}
</style>
<div class="cose-bar"><a class="brand" href="/" aria-label="CoSE home">""" + logo_svg() + """</a><a href="/tools/">All tools &rarr;</a></div>
"""

def tool_page(html):
    """A tool page is a self-contained HTML file kept verbatim; add the favicon and the site bar."""
    html = html.replace("</head>", '<link rel="icon" href="/favicon.ico" sizes="48x48">\n<link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/icon-32.png">\n</head>', 1)
    return html.replace("<body>", "<body>\n" + TOOL_BAR, 1)

def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copy(ROOT / "style.css", DIST / "style.css")
    shutil.copy(ROOT / "favicon.ico", DIST / "favicon.ico")
    shutil.copytree(ROOT / "assets", DIST / "assets", ignore=shutil.ignore_patterns("*.txt", "logo.svg", "mark.svg"))
    if (ROOT / "downloads").exists():
        shutil.copytree(ROOT / "downloads", DIST / "downloads")
    (DIST / "_headers").write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n")
    (DIST / "_redirects").write_text(
        "/shop/ / 301\n/shop / 301\n/researchers/ /scispinner-max 301\n/teachers/ /founders 301\n"
        "/students/ /founders 301\n/the-cose-team/ /founders 301\n/blog/ / 301\n/cart/ / 301\n"
        "/index.html / 301\n/scispinner-max.html /scispinner-max 301\n/founders.html /founders 301\n"
        "/tools/g-level-analysis.html /tools/g-level-analysis 301\n/analysis /tools/g-level-analysis 301\n"
        "/blog / 301\n/news/index.html /news/ 301\n/feed /news/feed.xml 301\n"
        "/datasheet /downloads/SciSpinner_Max_Datasheet_2026-10.pdf 302\n")
    (DIST / "tools").mkdir()
    # News: posts/*.md -> /news/<slug>, /news/ and the RSS feed
    (DIST / "news").mkdir()
    for p in POSTS:
        meta = dict(title=f"{p['title']} — CoSE", description=p["summary"] or p["title"], current="news")
        (DIST / "news" / f"{p['slug']}.html").write_text(page("news", meta, body=_news.post_body(p)))
    (DIST / "news" / "index.html").write_text(page("news", dict(title="News — CoSE",
        description="Updates from Collaborative Science Environment: software releases, instruments and deliveries.",
        current="news"), body=_news.index_body(POSTS)))
    (DIST / "news" / "feed.xml").write_text(_news.feed(POSTS))
    for name, meta in PAGES.items():
        (DIST / meta.get("out", f"{name}.html")).write_text(page(name, meta))
    # Standalone tools: served as-is from tools/, with a thin site bar and favicon added at build time.
    tools_src = ROOT / "tools"
    if tools_src.exists():
        for f in sorted(tools_src.glob("*.html")):
            (DIST / "tools" / f.name).write_text(tool_page(f.read_text()))
    print("built", sorted(p.name for p in DIST.iterdir()))

if __name__ == "__main__":
    main()
