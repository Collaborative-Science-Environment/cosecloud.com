"""Shared header/footer for the COSE site. build.py inlines these into each page."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGO = (ROOT / "assets" / "logo-inline.txt").read_text()

def logo_svg(height_class=""):
    return (f'<svg class="{height_class}" viewBox="0 0 311.43 116.43" role="img" aria-label="CoSE">{LOGO}</svg>')

def head(title, description, current=""):
    return f"""<title>{title}</title>
<meta name="description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/icon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="/assets/icons/icon-192.png">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/icons/icon-180.png">
<meta name="theme-color" content="#004053">
<link rel="stylesheet" href="/style.css">
<style>.brand .wm{{fill:var(--teal)}}</style>"""

NAV_ITEMS = [
    ("/#products", "Instruments", "products"),
    ("/founders", "About", "founders"),
    ("/#contact", "Contact", "contact"),
]

def nav(current=""):
    items = ""
    for href, label, key in NAV_ITEMS:
        cur = ' aria-current="page"' if key == current else ""
        items += f'<li><a href="{href}"{cur}>{label}</a></li>'
    return f"""<header class="nav">
  <div class="wrap">
    <a class="brand" href="/" aria-label="CoSE home">{logo_svg()}</a>
    <button class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="nav-links">Menu</button>
    <ul class="nav-links" id="nav-links">
      {items}
      <li><a class="btn btn-primary" href="/#contact">Request a quote</a></li>
    </ul>
  </div>
</header>"""

def footer():
    return f"""<footer>
  <div class="wrap">
    <div>
      <a class="brand" href="/" aria-label="CoSE home">{logo_svg()}</a>
      <p style="margin-top:1rem;max-width:34ch">Collaborative Science Environment Inc.<br>A Wisconsin benefit corporation building research instruments for gravitational biology.</p>
    </div>
    <div>
      <h4>Instruments</h4>
      <ul>
        <li><a href="/scispinner-max">SciSpinner Max</a></li>
        <li><a href="/#products">SciSpinner Duo</a></li>
        <li><a href="/#products">FlashLapse</a></li>
        <li><a href="/scispinner-max#downloads">Datasheet &amp; manuals</a></li>
        <li><a href="/founders">About CoSE</a></li>
      </ul>
    </div>
    <div>
      <h4>Contact</h4>
      <ul>
        <li><span class="mono" style="user-select:all">info@cosecloud.com</span></li>
        <li>56 Corry Street<br>Madison, Wisconsin 53704<br>United States</li>
      </ul>
    </div>
    <div class="fine">
      <span>&copy; 2026 Collaborative Science Environment Inc. SciSpinner and CoSE are trademarks of Collaborative Science Environment Inc.</span>
      <span>Made in Madison, Wisconsin</span>
    </div>
  </div>
</footer>
<script>
(function(){{
  var t=document.getElementById('nav-toggle'),l=document.getElementById('nav-links');
  if(t&&l){{t.addEventListener('click',function(){{var o=l.classList.toggle('open');t.setAttribute('aria-expanded',o);}});}}
  var f=document.getElementById('rfq');
  if(f){{f.addEventListener('submit',function(e){{
    if(!f.dataset.endpoint){{e.preventDefault();
      var ok=document.getElementById('rfq-ok');f.hidden=true;ok.hidden=false;ok.focus();}}
  }});}}
}})();
</script>"""
