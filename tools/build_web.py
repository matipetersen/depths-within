"""Build web/dread.html: the touch-screen game as one self-contained page.

    python tools/build_web.py            # writes web/dread.html

The page is a fragment (title, meta, style, markup, scripts) because the Artifact host wraps it in
its own document skeleton. `wrap_for_browser` makes the same skeleton for local browsers and tests.
The engine and the data are embedded verbatim: web/engine.js is what tests/test_web_parity.py checks.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")

SKELETON = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
body{{margin:0;font:14px system-ui,sans-serif}}[hidden]{{display:none!important}}</style></head>
<body>{fragment}</body></html>"""


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return fh.read()


def build() -> str:
    data = {
        "events": json.loads(read("data", "events.json"))["events"],
        "missions": json.loads(read("data", "missions.json"))["missions"],
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = read("web", "template.html")
    for key, value in (("/*__STYLE__*/", read("web", "style.css")), ("/*__ENGINE__*/", read("web", "engine.js")),
                       ("/*__DATA__*/", blob), ("/*__UI__*/", read("web", "ui.js"))):
        assert key in html, key
        html = html.replace(key, value, 1)
    return html


def wrap_for_browser(fragment: str) -> str:
    return SKELETON.format(fragment=fragment)


MANIFEST = {
    "name": "Depths Within", "short_name": "Depths Within",
    "description": "A submarine patrol that looks like a war and is something else. Touch, landscape.",
    "start_url": "./", "scope": "./", "display": "standalone", "orientation": "landscape",
    "background_color": "#0a1117", "theme_color": "#0a1117",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}

APP_HEAD = """<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">
<link rel="icon" type="image/svg+xml" href="icons/icon.svg">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#0a1117">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Depths Within">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="description" content="Depths Within: a submarine patrol, played on a touch screen held sideways.">"""

SERVICE_WORKER = """/* Keeps the game playable with no signal: the page and its icons are cached the first time. */
const CACHE = 'depths-within-%(version)s';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];
self.addEventListener('install', (e) => { e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request).then((res) => {
    if (res.ok && new URL(e.request.url).origin === location.origin) caches.open(CACHE).then((c) => c.put(e.request, res.clone()));
    return res;
  }).catch(() => caches.match('index.html'))));
});
"""

REGISTER = "<script>if ('serviceWorker' in navigator) window.addEventListener('load', function () { navigator.serviceWorker.register('sw.js').catch(function () {}); });</script>"

ROOT_REDIRECT = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Depths Within</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="0; url=docs/">
<link rel="canonical" href="docs/"><meta name="theme-color" content="#0a1117"></head>
<body style="margin:0;background:#0a1117;color:#dbe2d8;font:16px system-ui,sans-serif">
<p style="padding:24px"><a style="color:#d1a64e" href="docs/">Play Depths Within</a></p></body></html>
"""


def build_page(fragment: str) -> str:
    """The same game as a stand-alone page for GitHub Pages: head tags for the icon and the installable app."""
    marker = '<div id="app">'
    head, body = fragment.split(marker, 1)
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            + APP_HEAD + "\n" + head + "</head>\n<body style=\"margin:0\">\n" + marker + body.replace("</script>\n", "</script>\n", 1)
            + REGISTER + "\n</body></html>\n")


def write(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def main():
    out = os.path.join(WEB, "dread.html")
    html = build()
    write(out, html)
    print(f"{out}  {len(html) / 1024:.0f} KB")
    docs = os.path.join(ROOT, "docs")
    page = build_page(html)
    import hashlib
    version = hashlib.sha1(page.encode("utf-8")).hexdigest()[:10]
    write(os.path.join(docs, "index.html"), page)
    write(os.path.join(docs, "manifest.webmanifest"), json.dumps(MANIFEST, indent=2) + "\n")
    write(os.path.join(docs, "sw.js"), SERVICE_WORKER % {"version": version})
    write(os.path.join(docs, ".nojekyll"), "")
    write(os.path.join(ROOT, ".nojekyll"), "")
    write(os.path.join(ROOT, "index.html"), ROOT_REDIRECT)
    print(f"{os.path.join(docs, 'index.html')}  (GitHub Pages)")


if __name__ == "__main__":
    main()
