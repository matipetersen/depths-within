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


def main():
    out = os.path.join(WEB, "dread.html")
    html = build()
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"{out}  {len(html) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
