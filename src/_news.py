"""News posts: Markdown files in posts/ -> /news/<slug>, /news/, /news/feed.xml and a home-page block.

A post is posts/YYYY-MM-DD-slug.md with a short header, then Markdown:

    title: Software 1.3.0 released
    date: 2026-09-25
    author: Jerry Miao          (optional; this is the default)
    summary: One or two sentences shown in lists and feeds.

    Body text...

Supported Markdown: # headings, paragraphs, **bold**, *italic*, `code`, [links](url),
![images](src), - bullet lists, 1. numbered lists, > quotes, --- rules. No dependencies.
"""
import html as _html
import re
from datetime import datetime, timezone
from pathlib import Path

SITE = "https://cosecloud.com"


def _inline(s):
    s = _html.escape(s, quote=False)
    s = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1" loading="lazy">', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"`([^`]+)`", r'<code>\1</code>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", s)
    s = s.replace(" -- ", " &ndash; ").replace("...", "&hellip;")
    return s


def md_to_html(text):
    out, para, lst, quote = [], [], None, []

    def flush_para():
        if para:
            out.append("<p>" + _inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_list():
        nonlocal lst
        if lst:
            tag, items = lst
            out.append(f"<{tag}>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + f"</{tag}>")
            lst = None

    def flush_quote():
        if quote:
            out.append("<blockquote><p>" + _inline(" ".join(quote)) + "</p></blockquote>")
            quote.clear()

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush_para(); flush_list(); flush_quote(); continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            flush_para(); flush_list(); flush_quote()
            level = min(len(m.group(1)) + 1, 4)      # '#' in a post becomes h2; the page title is the h1
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>"); continue
        m = re.match(r"^!video\s+(\S+)\s+(\S+)(?:\s+(.*))?$", line)   # !video <src.mp4> <poster.jpg> caption
        if m:
            flush_para(); flush_list(); flush_quote()
            cap = f"<figcaption>{_inline(m.group(3))}</figcaption>" if m.group(3) else ""
            out.append(f'<figure class="post-video"><video src="{m.group(1)}" poster="{m.group(2)}" controls muted loop playsinline preload="none"></video>{cap}</figure>'); continue
        if re.match(r"^(-{3,}|\*{3,})$", line):
            flush_para(); flush_list(); flush_quote(); out.append("<hr>"); continue
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            flush_para(); flush_quote()
            if not lst or lst[0] != "ul": flush_list(); lst = ("ul", [])
            lst[1].append(m.group(1)); continue
        m = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if m:
            flush_para(); flush_quote()
            if not lst or lst[0] != "ol": flush_list(); lst = ("ol", [])
            lst[1].append(m.group(1)); continue
        if line.startswith(">"):
            flush_para(); flush_list(); quote.append(line[1:].strip()); continue
        if lst and raw.startswith("  "):                # continuation of a list item
            lst[1][-1] += " " + line.strip(); continue
        flush_list(); flush_quote(); para.append(line.strip())
    flush_para(); flush_list(); flush_quote()
    return "\n".join(out)


def load_posts(root):
    posts = []
    for f in sorted((root / "posts").glob("*.md")):
        text = f.read_text()
        head, _, body = text.partition("\n\n")
        meta = {}
        for ln in head.splitlines():
            k, _, v = ln.partition(":")
            meta[k.strip().lower()] = v.strip()
        if "title" not in meta or "date" not in meta:
            raise SystemExit(f"{f.name}: needs 'title:' and 'date:' header lines")
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.stem)
        date = datetime.strptime(meta["date"], "%Y-%m-%d")
        posts.append(dict(slug=slug, title=meta["title"], date=date, summary=meta.get("summary", ""),
                          author=meta.get("author", "Jerry Miao"),
                          html=md_to_html(body.strip()), url=f"/news/{slug}"))
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def fmt_date(d):
    return d.strftime("%-d %B %Y")


def post_body(p):
    return f"""<main>
<article class="post">
  <div class="wrap">
    <p class="eyebrow"><a href="/news/">News</a> &middot; <time datetime="{p['date']:%Y-%m-%d}">{fmt_date(p['date'])}</time> &middot; {_html.escape(p['author'])}</p>
    <h1>{_html.escape(p['title'])}</h1>
    {f'<p class="lede">{_inline(p["summary"])}</p>' if p['summary'] else ''}
    <div class="post-body">
{p['html']}
    </div>
    <p class="post-foot"><a href="/news/">&larr; All news</a></p>
  </div>
</article>
</main>
"""


def list_items(posts, cls="post-list"):
    items = "".join(
        f'<li><time datetime="{p["date"]:%Y-%m-%d}">{fmt_date(p["date"])}</time>'
        f'<div><h3><a href="{p["url"]}">{_html.escape(p["title"])}</a></h3>'
        + (f'<p>{_inline(p["summary"])}</p>' if p["summary"] else "") + '</div></li>'
        for p in posts)
    return f'<ul class="{cls}">{items}</ul>'


def index_body(posts):
    return f"""<main>
<section class="hero" style="padding-bottom:1rem">
  <div class="wrap" style="grid-template-columns:minmax(0,1fr)">
    <div class="hero-copy" style="max-width:720px">
      <p class="eyebrow">News</p>
      <h1>COSE updates</h1>
      <p class="lede">Software releases, new instruments, deliveries and engineering updates from COSE. <a href="/news/feed.xml">RSS feed</a>.</p>
    </div>
  </div>
</section>
<section id="news-list" style="border-top:0;padding-top:1rem">
  <div class="wrap">
    {list_items(posts)}
  </div>
</section>
</main>
"""


def home_block(posts, n=3):
    if not posts:
        return ""
    return f"""<section id="news">
  <div class="wrap">
    <div class="grid-2">
      <div>
        <p class="eyebrow">News</p>
        <h2>Latest from COSE</h2>
        <p style="margin-top:1.25rem"><a class="more" href="/news/">All news &rarr;</a></p>
      </div>
      {list_items(posts[:n], "post-list compact")}
    </div>
  </div>
</section>
"""


def feed(posts):
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    items = "".join(f"""
  <item>
    <title>{_html.escape(p['title'])}</title>
    <link>{SITE}{p['url']}</link>
    <guid>{SITE}{p['url']}</guid>
    <pubDate>{p['date'].strftime('%a, %d %b %Y 12:00:00 +0000')}</pubDate>
    <description>{_html.escape(p['summary'] or p['title'])}</description>
  </item>""" for p in posts)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
  <title>COSE news</title>
  <link>{SITE}/news/</link>
  <description>Updates from Collaborative Science Environment: software releases, instruments and deliveries.</description>
  <lastBuildDate>{now}</lastBuildDate>{items}
</channel></rss>
"""
