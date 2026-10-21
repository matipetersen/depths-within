"""The touch game in a real browser: landscape viewports, taps, and nothing hidden on screen."""
import glob
import os
import re
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from build_web import build, wrap_for_browser  # noqa: E402

sync_api = pytest.importorskip("playwright.sync_api")
CHROME = next(iter(sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))), None) \
    or shutil.which("chromium") or shutil.which("google-chrome")
pytestmark = pytest.mark.skipif(CHROME is None, reason="no Chromium available")

LANDSCAPE = [(667, 375), (844, 390), (932, 430), (1024, 768), (1280, 800)]
HIDDEN = ("moral_debt", "orders_doubt", "war_over", "notice_at", "names_learned", "name_known", "candor",
          "mundane_cause", "uncanny_cause", "mundane_when", "peak_dread")
HIDDEN_FIELD = re.compile(r"\b(attention|owed|dread|fear|guilt|trust)\s*[:=]\s*[0-9.]+")


@pytest.fixture(scope="module")
def page_file(tmp_path_factory):
    path = tmp_path_factory.mktemp("web") / "page.html"
    path.write_text(wrap_for_browser(build()), encoding="utf-8")
    return str(path)


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        yield b
        b.close()


def open_page(browser, page_file, size=(844, 390), touch=True):
    ctx = browser.new_context(viewport={"width": size[0], "height": size[1]}, has_touch=touch, is_mobile=touch,
                              device_scale_factor=2)
    page = ctx.new_page()
    page.errors = []
    page.on("pageerror", lambda e: page.errors.append(str(e)))
    page.on("console", lambda m: page.errors.append(m.text) if m.type == "error" and "font" not in m.text.lower()
            and "net::" not in m.text else None)
    page.goto("file://" + page_file)
    return page


def begin(page):
    btn = page.locator("[data-a=new]")
    btn.tap() if page.evaluate("'ontouchstart' in window") else btn.click()
    page.wait_for_selector(".cols")


def to_decision(page, limit=60):
    for _ in range(limit):
        if page.locator(".sheet.decision").count():
            page.wait_for_timeout(400)               # past the stray-tap guard
            return
        page.locator("[data-a=news]").tap()
    raise AssertionError("no decision appeared")


def test_the_page_is_the_current_build():
    """web/dread.html is what gets published; it must not lag behind its sources."""
    with open(os.path.join(ROOT, "web", "dread.html"), encoding="utf-8") as fh:
        assert fh.read() == build(), "run: python tools/build_web.py"
    with open(os.path.join(ROOT, "web", "engine.js"), encoding="utf-8") as fh:
        assert fh.read().strip() in build()          # the engine that the parity test checks is the one shipped


def test_title_then_the_bridge_without_errors(browser, page_file):
    page = open_page(browser, page_file)
    assert "Depths Within" in page.inner_text(".sheet")
    begin(page)
    text = page.inner_text("#app").lower()          # the labels are set in small caps by CSS
    for part in ("ledger", "the men", "log", "orders", "wait 1h", "100%", "sink the battleship"):
        assert part in text, part
    assert page.errors == []


@pytest.mark.parametrize("size", LANDSCAPE)
def test_no_sideways_scroll_and_buttons_are_big_enough(browser, page_file, size):
    page = open_page(browser, page_file, size)
    begin(page)
    for stage in ("main", "orders", "decision"):
        if stage == "orders":
            page.locator("[data-a=orders]").tap()
        if stage == "decision":
            page.locator("[data-a=close]").tap()
            to_decision(page)
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), (size, stage)
        small = page.evaluate("""() => [...document.querySelectorAll('button')].filter(b => b.offsetParent && !b.disabled)
            .map(b => [b.textContent.trim().slice(0, 24), b.getBoundingClientRect().width, b.getBoundingClientRect().height])
            .filter(([t, w, h]) => w < 40 || h < 40)""")
        assert not small, (size, stage, small)


def test_a_decision_stops_the_clock_and_ignores_a_stray_tap(browser, page_file):
    page = open_page(browser, page_file)
    begin(page)
    for _ in range(60):
        if page.locator(".sheet.decision").count():
            break
        page.locator("[data-a=news]").tap()
    assert page.locator(".sheet.decision").count() == 1
    tick = page.evaluate("dreadDebug.state.game.w.tick_no")
    assert page.locator("[data-a=wait]").is_disabled() and page.locator("[data-a=news]").is_disabled()
    page.locator(".sheet.decision .opt").first.tap()              # within 350 ms of appearing: not an answer
    assert page.locator(".sheet.decision").count() == 1
    page.wait_for_timeout(450)
    page.locator(".sheet.decision .opt").first.tap()
    assert page.locator(".sheet.decision").count() == 0
    assert page.evaluate("dreadDebug.state.game.w.tick_no") == tick
    assert page.errors == []


def test_orders_and_picking_a_man(browser, page_file):
    page = open_page(browser, page_file)
    begin(page)
    page.locator("[data-a=orders]").tap()
    page.locator(".orders-grid .opt", has_text="Confine").tap()
    assert page.locator(".pick .opt").count() == 12
    page.locator(".pick .opt").nth(2).tap()
    assert "is confined" in page.inner_text(".notice")
    page.locator("[data-a='tabC:men']").tap()
    assert "CONFINED" in page.inner_text(".men").upper()
    page.locator("[data-a=orders]").tap()
    page.locator(".orders-grid .opt", has_text="Silence the sonar").tap()
    assert "SONAR OFF" in page.inner_text(".sonar").upper()


def test_nothing_hidden_is_ever_drawn(browser, page_file):
    page = open_page(browser, page_file)
    begin(page)
    seen = []
    for step in range(260):
        if page.evaluate("dreadDebug.state.game.over"):
            break
        if page.evaluate("!!dreadDebug.state.game.w.pending"):
            seen.append(page.inner_text("#app"))
            page.evaluate("(n) => dreadDebug.act('c:' + (n % dreadDebug.state.game.w.pending.choices.length))", step)
        else:
            page.evaluate("(a) => dreadDebug.act(a)", "w" if step % 3 else "t")
        if step % 10 == 0:
            seen.append(page.inner_text("#app"))
    seen.append(page.inner_text("#app"))
    text = "\n".join(seen).lower()
    for token in HIDDEN:
        assert token not in text, token
    assert not HIDDEN_FIELD.search(text)
    page.evaluate("() => { dreadDebug.state.tabC = 'men'; dreadDebug.render(); }")
    assert not re.search(r"\d", page.inner_text(".men"))        # not one number about the men
    assert "Hull" in "\n".join(seen) and "CAPTAIN" in "\n".join(seen)


def test_portrait_asks_for_landscape_and_landscape_does_not(browser, page_file):
    portrait = open_page(browser, page_file, (390, 844))
    assert portrait.locator(".rotate").is_visible()
    landscape = open_page(browser, page_file, (844, 390))
    assert not landscape.locator(".rotate").is_visible()


def test_a_closed_tab_does_not_lose_the_patrol(browser, page_file):
    page = open_page(browser, page_file)
    begin(page)
    for _ in range(6):
        if page.locator(".sheet.decision").count():
            page.wait_for_timeout(400)
            page.locator(".sheet.decision .opt").first.tap()
        page.locator("[data-a=news]").tap()
    before = page.evaluate("dreadDebug.state.game.w.log.join('\\n')")
    moves = page.evaluate("dreadDebug.state.game.inputs.length")
    assert moves > 3
    page.reload()
    assert "Continue" in page.inner_text(".sheet")
    page.locator("[data-a=continue]").tap()
    page.wait_for_selector(".cols")
    assert page.evaluate("dreadDebug.state.game.w.log.join('\\n')") == before
    assert page.evaluate("dreadDebug.state.game.inputs.length") == moves


def test_a_whole_patrol_ends_with_both_reports_and_starts_again(browser, page_file):
    page = open_page(browser, page_file)
    begin(page)
    page.evaluate("""() => { const d = dreadDebug; let n = 0;
      while (!d.state.game.over && n++ < 4000) { const g = d.state.game;
        if (g.w.pending) g.do('c:' + (n % g.w.pending.choices.length)); else g.do(n % 7 === 0 ? 't' : 'w'); }
      d.render(); }""")
    text = page.inner_text(".sheet")
    assert "The end" in text and "Report of proceedings" in text and "Captain's log" in text
    assert "stopped listening" in text
    assert page.locator("[data-a=wait]").is_disabled()
    page.locator("[data-a=new]").tap()
    page.wait_for_selector(".cols")
    assert page.evaluate("dreadDebug.state.game.w.tick_no") == 0 and page.errors == []


def test_keyboard_answers_decisions_and_waits(browser, page_file):
    page = open_page(browser, page_file, touch=False)
    begin(page)
    page.keyboard.press("Space")
    assert page.evaluate("dreadDebug.state.game.w.tick_no") == 1
    for _ in range(60):
        if page.locator(".sheet.decision").count():
            break
        page.keyboard.press("w")
    page.keyboard.press("1")
    assert page.locator(".sheet.decision").count() == 0


def test_replay_from_the_seed_gives_the_same_boat():
    """What makes save/continue safe: a game is its seed plus its inputs."""
    if shutil.which("node") is None:
        pytest.skip("node is not installed")
    script = """
const fs=require('fs'),path=require('path');const D=require(path.join(%r,'web','engine.js'));
D.setData({events:JSON.parse(fs.readFileSync(path.join(%r,'data','events.json'))).events,
  missions:JSON.parse(fs.readFileSync(path.join(%r,'data','missions.json'))).missions});
const g=new D.Game(4242);let n=0;
while(!g.over&&n++<600){ if(g.w.pending) g.do('c:'+(n%%g.w.pending.choices.length)); else g.do(n%%6?'w':'t'); }
const r=D.Game.restore(JSON.parse(JSON.stringify(g.serialize())));
console.log(JSON.stringify([g.w.log.join('|')===r.w.log.join('|'), g.ending===r.ending, g.over, g.inputs.length]));
""" % (ROOT, ROOT, ROOT)
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout
    same_log, same_end, over, moves = __import__("json").loads(out)
    assert same_log and same_end and over and moves > 20


def test_the_chart_and_the_instruments_show_where_the_boat_is_and_move_with_the_work(browser, page_file):
    page = open_page(browser, page_file)
    begin(page)
    assert page.locator("svg.chart .boat").count() == 1
    assert page.locator("svg.chart polyline.trk").count() == 1        # only the orders received are on the chart
    for label in ("Heading", "Speed", "Depth", "Grid", "Signature", "Next"):
        assert label.lower() in page.inner_text(".gauges").lower()
    before = page.get_attribute("svg.chart .boat", "transform")
    page.locator("button.step").tap()
    for _ in range(4):
        if page.locator(".sheet.decision").count():
            break
        page.locator("[data-a=wait]").tap()
    assert page.get_attribute("svg.chart .boat", "transform") != before
    assert page.inner_text(".gauges").count("°") == 1


def test_the_hull_tab_shows_each_compartment_and_where_the_damage_is(browser, page_file):
    page = open_page(browser, page_file)
    begin(page)
    page.locator("[data-a='tabL:hull']").tap()
    assert page.locator(".comp li").count() == 5 and page.locator("svg.hullsvg .cp.sound").count() == 5
    page.evaluate("() => { const w = dreadDebug.state.game.w; w.ship.hull -= 0.4; w.settle_damage(); dreadDebug.render(); }")
    assert page.locator("svg.hullsvg .cp.flooding, svg.hullsvg .cp.damaged").count() == 1
    assert "taking water" in page.inner_text(".comp")
    page.locator("[data-a='tabL:ledger']").tap()
    assert "Diesel" in page.inner_text(".led")


def test_the_tabs_are_big_enough_to_tap(browser, page_file):
    page = open_page(browser, page_file, (667, 375))
    begin(page)
    for tab in page.locator("button.tab").all():
        box = tab.bounding_box()
        assert box["height"] >= 40 and box["width"] >= 40
