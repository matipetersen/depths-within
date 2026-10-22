"""The game as a GitHub Pages site: an installable web app with its icon (docs/)."""
import glob
import http.server
import json
import os
import shutil
import socketserver
import struct
import sys
import threading

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
sys.path.insert(0, os.path.join(ROOT, "tools"))
from build_web import APP_HEAD, build, build_page  # noqa: E402


def _png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", head[16:24])


def test_the_published_page_is_the_current_build():
    with open(os.path.join(DOCS, "index.html"), encoding="utf-8") as fh:
        assert fh.read() == build_page(build()), "run: python tools/build_web.py"


def test_the_page_carries_the_icon_the_manifest_and_the_app_tags():
    html = open(os.path.join(DOCS, "index.html"), encoding="utf-8").read()
    for tag in ('rel="icon"', 'rel="apple-touch-icon"', 'rel="manifest"', 'name="theme-color"', "serviceWorker"):
        assert tag in html
    assert APP_HEAD in html and "<title>Depths Within</title>" in html and html.count('id="app"') == 1


def test_the_manifest_points_at_icons_that_exist_with_the_sizes_it_claims():
    m = json.load(open(os.path.join(DOCS, "manifest.webmanifest")))
    assert m["display"] == "standalone" and m["orientation"] == "landscape" and m["start_url"] == "./"
    assert {i["purpose"] for i in m["icons"]} == {"any", "maskable"}
    for icon in m["icons"]:
        w, h = _png_size(os.path.join(DOCS, icon["src"]))
        assert f"{w}x{h}" == icon["sizes"]
    assert _png_size(os.path.join(DOCS, "icons", "apple-touch-icon.png")) == (180, 180)
    assert _png_size(os.path.join(DOCS, "icons", "favicon-32.png")) == (32, 32)


def test_the_root_sends_visitors_to_the_game_and_jekyll_stays_out_of_the_way():
    root = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    assert 'url=docs/' in root and 'href="docs/"' in root
    assert os.path.exists(os.path.join(DOCS, ".nojekyll")) and os.path.exists(os.path.join(ROOT, ".nojekyll"))


def test_the_service_worker_caches_what_the_game_needs():
    sw = open(os.path.join(DOCS, "sw.js"), encoding="utf-8").read()
    for item in ("index.html", "manifest.webmanifest", "icons/icon-192.png", "caches.open"):
        assert item in sw


CHROME = next(iter(sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))), None) or shutil.which("chromium")


@pytest.mark.skipif(CHROME is None, reason="no Chromium available")
def test_served_over_http_the_game_loads_the_icon_the_manifest_and_starts():
    sync_api = pytest.importorskip("playwright.sync_api")

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=ROOT, **k)

        def log_message(self, *a):
            pass

    with socketserver.TCPServer(("127.0.0.1", 0), Quiet) as srv:
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            with sync_api.sync_playwright() as p:
                b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
                ctx = b.new_context(viewport={"width": 844, "height": 390}, has_touch=True, is_mobile=True)
                page = ctx.new_page()
                page.goto(f"http://127.0.0.1:{port}/docs/")
                page.wait_for_selector("[data-a=new]")
                page.wait_for_timeout(1200)
                assert page.title() == "Depths Within"
                for url in ("manifest.webmanifest", "icons/icon-192.png", "icons/apple-touch-icon.png", "icons/favicon-32.png", "sw.js"):
                    assert page.evaluate("(u) => fetch(u).then((r) => r.status)", url) == 200, url
                assert page.evaluate("fetch('manifest.webmanifest').then(r => r.json()).then(m => m.name)") == "Depths Within"
                assert page.evaluate("document.querySelector('link[rel=manifest]').href").endswith("/docs/manifest.webmanifest")
                page.locator("[data-a=new]").tap()
                page.wait_for_selector(".cols")
                # and the root address lands on the game
                pg = b.new_page()
                pg.goto(f"http://127.0.0.1:{port}/")
                pg.wait_for_selector("[data-a=new]", timeout=8000)
                assert pg.url.endswith("/docs/")
                b.close()
        finally:
            srv.shutdown()
