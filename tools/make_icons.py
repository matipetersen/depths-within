"""Draw the web app's icons (periscope over a sonar scope) with Pillow.

    python tools/make_icons.py     # writes docs/icons/*.png and web/icon.svg
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "icons")
HULL, PANEL, SEA, BRASS, PAPER = (10, 17, 23), (16, 26, 33), (120, 184, 160), (209, 166, 78), (219, 226, 216)

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<rect width="512" height="512" rx="96" fill="#0a1117"/>
<g fill="none" stroke="#78b8a0" stroke-width="6" opacity=".55"><circle cx="256" cy="276" r="190"/><circle cx="256" cy="276" r="132"/><circle cx="256" cy="276" r="74"/></g>
<path d="M256 276 L256 86" stroke="#78b8a0" stroke-width="5" opacity=".7"/>
<circle cx="338" cy="214" r="9" fill="#78b8a0"/>
<g fill="#dbe2d8"><path d="M96 352 q0-26 40-26 h244 q40 0 40 26 q0 26-40 26 h-244 q-40 0-40-26z"/><rect x="226" y="282" width="62" height="48" rx="10"/></g>
<g fill="none" stroke="#d1a64e" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"><path d="M268 286 V132 H334"/></g>
<rect x="326" y="118" width="30" height="28" rx="6" fill="#d1a64e"/>
<path d="M60 392 q50 22 100 0 t100 0 t100 0 t92 0" fill="none" stroke="#78b8a0" stroke-width="7" stroke-linecap="round" opacity=".8"/>
</svg>
"""


def draw(size: int, maskable: bool = False) -> Image.Image:
    k = 4                                                     # supersample, then shrink
    n = size * k
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = n / 512
    pad = 0.12 * 512 if maskable else 0                      # a maskable icon keeps its drawing in the middle 80 %
    sc = (512 - 2 * pad) / 512
    X = lambda v: (pad + v * sc) * s
    d.rounded_rectangle([0, 0, n, n], radius=0 if maskable else 96 * s, fill=HULL + (255,))
    for r, a in ((190, 140), (132, 140), (74, 140)):
        d.ellipse([X(256 - r), X(276 - r), X(256 + r), X(276 + r)], outline=SEA + (a,), width=max(1, int(6 * s * sc)))
    d.line([X(256), X(276), X(256), X(86)], fill=SEA + (180,), width=max(1, int(5 * s * sc)))
    d.ellipse([X(329), X(205), X(347), X(223)], fill=SEA + (255,))
    d.rounded_rectangle([X(96), X(326), X(420), X(378)], radius=26 * s * sc, fill=PAPER + (255,))
    d.rounded_rectangle([X(226), X(282), X(288), X(330)], radius=10 * s * sc, fill=PAPER + (255,))
    w = int(16 * s * sc)
    d.line([X(268), X(290), X(268), X(132), X(334), X(132)], fill=BRASS + (255,), width=w, joint="curve")
    d.rounded_rectangle([X(326), X(118), X(356), X(146)], radius=6 * s * sc, fill=BRASS + (255,))
    for x0 in (60, 160, 260, 352):
        d.arc([X(x0), X(380), X(x0 + 100), X(404)], 0, 180, fill=SEA + (210,), width=max(1, int(7 * s * sc)))
    return img.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, size, maskable in (("icon-192.png", 192, False), ("icon-512.png", 512, False), ("maskable-512.png", 512, True),
                                 ("apple-touch-icon.png", 180, False), ("favicon-32.png", 32, False)):
        draw(size, maskable).save(os.path.join(OUT, name))
        print(name)
    with open(os.path.join(ROOT, "web", "icon.svg"), "w", encoding="utf-8") as fh:
        fh.write(SVG)
    with open(os.path.join(ROOT, "docs", "icons", "icon.svg"), "w", encoding="utf-8") as fh:
        fh.write(SVG)


if __name__ == "__main__":
    main()
