"""Builds the purple/black Y2K banner SVGs in assets/ (header, footer, divider).

The character renders are the Pokemon HOME 3D models, pulled from the PokeAPI
sprite mirror and embedded as base64 so each SVG is fully self-contained --
GitHub's image proxy blocks external references from inside an SVG, so linking
them out would leave a blank banner.

    pip install Pillow
    python scripts/build_banners.py

To use different characters, change the national dex numbers passed to embed()
in build_header() / build_footer() (92 Gastly, 93 Haunter, 94 Gengar).
"""
import base64
import io
import os
import random
import urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".sprite-cache")
OUT = os.path.join(os.path.dirname(HERE), "assets")

SPRITES = ("https://raw.githubusercontent.com/PokeAPI/sprites/master"
           "/sprites/pokemon/other/home/%d.png")

MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace"
SANS = "'Inter','Segoe UI',Helvetica,Arial,sans-serif"


def fetch(dex):
    """Download a render once, then reuse the cached copy."""
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    path = os.path.join(CACHE, "%d.png" % dex)
    if not os.path.exists(path):
        with urllib.request.urlopen(SPRITES % dex, timeout=60) as resp:
            data = resp.read()
        with open(path, "wb") as fh:
            fh.write(data)
    return path


def embed(dex, target_h):
    """Trim transparent padding, scale to target height, return (data_uri, w, h)."""
    im = Image.open(fetch(dex)).convert("RGBA")
    im = im.crop(im.getbbox())
    w = round(im.width * target_h / im.height)
    im = im.resize((w, target_h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return ("data:image/png;base64,"
            + base64.b64encode(buf.getvalue()).decode("ascii"), w, target_h)


# ---------------------------------------------------------------- shared defs

DEFS = """
    <linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0.00" stop-color="#FFFFFF"/>
      <stop offset="0.14" stop-color="#F3E8FF"/>
      <stop offset="0.30" stop-color="#C4A5FF"/>
      <stop offset="0.46" stop-color="#7C3AED"/>
      <stop offset="0.50" stop-color="#2E1065"/>
      <stop offset="0.54" stop-color="#4C1D95"/>
      <stop offset="0.66" stop-color="#D946EF"/>
      <stop offset="0.80" stop-color="#F0ABFC"/>
      <stop offset="0.90" stop-color="#FFFFFF"/>
      <stop offset="1.00" stop-color="#A855F7"/>
    </linearGradient>

    <linearGradient id="irid" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0.00" stop-color="#3B0764" stop-opacity="0"/>
      <stop offset="0.18" stop-color="#4F46E5" stop-opacity="0.8"/>
      <stop offset="0.38" stop-color="#A855F7" stop-opacity="0.95"/>
      <stop offset="0.54" stop-color="#D946EF" stop-opacity="1"/>
      <stop offset="0.72" stop-color="#7C3AED" stop-opacity="0.9"/>
      <stop offset="0.88" stop-color="#4F46E5" stop-opacity="0.6"/>
      <stop offset="1.00" stop-color="#3B0764" stop-opacity="0"/>
    </linearGradient>

    <linearGradient id="bevel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0.00" stop-color="#FFFFFF"/>
      <stop offset="0.30" stop-color="#D8B4FE"/>
      <stop offset="0.52" stop-color="#6D28D9"/>
      <stop offset="0.55" stop-color="#1E0736"/>
      <stop offset="0.80" stop-color="#7C3AED"/>
      <stop offset="1.00" stop-color="#E9D5FF"/>
    </linearGradient>

    <radialGradient id="bloomA" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0.00" stop-color="#C026D3" stop-opacity="0.55"/>
      <stop offset="0.35" stop-color="#7C3AED" stop-opacity="0.30"/>
      <stop offset="0.70" stop-color="#4C1D95" stop-opacity="0.11"/>
      <stop offset="1.00" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>

    <linearGradient id="flareH" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0"   stop-color="#F0ABFC" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0.85"/>
      <stop offset="1"   stop-color="#F0ABFC" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="flareV" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0"   stop-color="#F0ABFC" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0.7"/>
      <stop offset="1"   stop-color="#F0ABFC" stop-opacity="0"/>
    </linearGradient>

    <linearGradient id="gridFade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0"    stop-color="#000000" stop-opacity="0.95"/>
      <stop offset="0.45" stop-color="#000000" stop-opacity="0.45"/>
      <stop offset="1"    stop-color="#000000" stop-opacity="0"/>
    </linearGradient>

    <filter id="bloom" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="20" result="b"/>
      <feComponentTransfer in="b">
        <feFuncR type="linear" slope="1.75"/>
        <feFuncG type="linear" slope="0.45"/>
        <feFuncB type="linear" slope="2.30"/>
      </feComponentTransfer>
    </filter>

    <filter id="softglow" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="9"/>
    </filter>
    <filter id="midglow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="5"/>
    </filter>
    <filter id="tinyglow" x="-150%" y="-150%" width="400%" height="400%">
      <feGaussianBlur stdDeviation="2.4"/>
    </filter>

    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="1.4" fill="#000000" opacity="0.22"/>
    </pattern>

    <path id="spark" d="M 0 -11 C 1.7 -3.7, 3.7 -1.7, 11 0 C 3.7 1.7, 1.7 3.7, 0 11
                        C -1.7 3.7, -3.7 1.7, -11 0 C -3.7 -1.7, -1.7 -3.7, 0 -11 Z"/>
"""


def sparkle(x, y, scale, opacity, dur, begin, color="#FFFFFF"):
    return (
        '  <g transform="translate(%s,%s) scale(%s)" fill="%s">\n'
        '    <use href="#spark" filter="url(#tinyglow)"/>\n'
        '    <use href="#spark"/>\n'
        '    <animate attributeName="opacity" values="%s;%.2f;%s" dur="%ss"'
        ' begin="%ss" repeatCount="indefinite"/>\n'
        "  </g>\n"
    ) % (x, y, scale, color, opacity, opacity * 0.12, opacity, dur, begin)


def grid_floor(horizon_y, bottom_y, vp_x, width, rows=9, cols=13, opacity=0.8):
    """Perspective wireframe floor receding to a vanishing point.

    Drawn full strength, then knocked back toward the horizon by a black fade so
    the far end dissolves into the void instead of ending on a hard line.
    """
    out = ['  <g stroke="#A855F7" stroke-width="1.1" opacity="%s" '
           'filter="url(#tinyglow)">\n' % opacity]
    span = width * 1.9
    for i in range(-cols, cols + 1):
        x_bottom = vp_x + i * (span / (2.0 * cols))
        out.append('    <line x1="%s" y1="%s" x2="%.1f" y2="%s"/>\n'
                   % (vp_x, horizon_y, x_bottom, bottom_y))
    depth = bottom_y - horizon_y
    for k in range(1, rows + 1):
        y = horizon_y + depth * (float(k) / rows) ** 2.3
        out.append('    <line x1="0" y1="%.1f" x2="%s" y2="%.1f"/>\n' % (y, width, y))
    out.append("  </g>\n")
    out.append('  <rect x="0" y="%s" width="%s" height="%s" fill="url(#gridFade)"/>\n'
               % (horizon_y - 6, width, depth + 6))
    return "".join(out)


def corner_brackets(w, h, m=22, arm=34, color="#A855F7", opacity=0.5):
    d = [
        "M %s %s L %s %s L %s %s" % (m, m + arm, m, m, m + arm, m),
        "M %s %s L %s %s L %s %s" % (w - m - arm, m, w - m, m, w - m, m + arm),
        "M %s %s L %s %s L %s %s" % (m, h - m - arm, m, h - m, m + arm, h - m),
        "M %s %s L %s %s L %s %s" % (w - m - arm, h - m, w - m, h - m, w - m, h - m - arm),
    ]
    return ('  <g fill="none" stroke="%s" stroke-width="1.8" opacity="%s">\n'
            % (color, opacity)
            + "".join('    <path d="%s"/>\n' % p for p in d) + "  </g>\n")


def barcode(x, y, h=26, seed=7, color="#C4B5FD", opacity=0.55):
    rng = random.Random(seed)
    out = ['  <g fill="%s" opacity="%s">\n' % (color, opacity)]
    cx = x
    for _ in range(34):
        bw = rng.choice([1, 1, 1.5, 2, 3])
        out.append('    <rect x="%.1f" y="%s" width="%s" height="%s"/>\n' % (cx, y, bw, h))
        cx += bw + rng.choice([1.5, 2, 2.5])
    out.append("  </g>\n")
    return "".join(out), cx - x


def flare(cx, cy, rx, ry=None):
    ry = ry or rx * 0.55
    return (
        '  <g opacity="0.75" filter="url(#midglow)">\n'
        '    <rect x="%s" y="%s" width="%s" height="3" fill="url(#flareH)"/>\n'
        '    <rect x="%s" y="%s" width="3" height="%s" fill="url(#flareV)"/>\n'
        "  </g>\n"
    ) % (cx - rx, cy - 1.5, rx * 2, cx - 1.5, cy - ry, ry * 2)


def chrome_text(x, y, size, content, letter=-3, weight=900, skew=-7, family=SANS,
                stroke_w=1.1, glow=0.5):
    """Bevelled Y2K chrome type: dark extrude, aura, gradient face, bright rim."""
    common = ('font-family="%s" font-size="%s" font-weight="%s" letter-spacing="%s"'
              % (family, size, weight, letter))
    return (
        '  <g transform="translate(%s,%s) skewX(%s)">\n'
        '    <text x="0" y="0" %s fill="#A855F7" filter="url(#softglow)" opacity="%s">%s</text>\n'
        '    <text x="6" y="8" %s fill="#180528">%s</text>\n'
        '    <text x="3" y="4" %s fill="#3B0764">%s</text>\n'
        '    <text x="0" y="0" %s fill="url(#chrome)" stroke="#F5F3FF" stroke-width="%s"'
        ' paint-order="stroke fill">%s</text>\n'
        "  </g>\n"
    ) % (x, y, skew, common, glow, content, common, content, common, content,
         common, stroke_w, content)


# ---------------------------------------------------------------- header

def build_header():
    W, H = 1200, 360
    uri, gw, gh = embed(93, 320)          # Haunter
    cx, cy = 946, 156
    x, y = cx - gw / 2.0, cy - gh / 2.0

    bars, bw = barcode(1024, 272, h=24, color="#DDD0FF", opacity=0.7)

    sparks = "".join([
        sparkle(742, 58, 1.2, 0.95, 3.4, -0.2),
        sparkle(1148, 92, 0.8, 0.85, 4.1, -1.4),
        sparkle(700, 196, 0.45, 0.6, 3.7, -2.8),
        sparkle(1096, 250, 0.55, 0.65, 4.8, -0.9),
        sparkle(86, 268, 0.5, 0.5, 5.2, -1.7, "#F0ABFC"),
    ])

    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %(W)s %(H)s" width="%(W)s" height="%(H)s" role="img" aria-label="Joshua V - Software Engineering, United Kingdom">
  <defs>%(defs)s</defs>

  <rect width="%(W)s" height="%(H)s" fill="#000000"/>

  <!-- light pooling in the void -->
  <ellipse cx="%(cx)s" cy="%(cy)s" rx="300" ry="230" fill="url(#bloomA)"/>
  <ellipse cx="180" cy="330" rx="280" ry="110" fill="url(#bloomA)" opacity="0.35"/>

%(grid)s
  <!-- iridescent sweep -->
  <rect x="-40" y="150" width="1280" height="2.5" fill="url(#irid)"
        transform="rotate(-6 600 170)" filter="url(#softglow)" opacity="0.5"/>

  <!-- the subject -->
  <g>
    <animateTransform attributeName="transform" type="translate"
                      values="0 0; 0 -9; 0 0" dur="7s" repeatCount="indefinite"/>
    <image href="%(uri)s" x="%(x)s" y="%(y)s" width="%(gw)s" height="%(gh)s"
           filter="url(#bloom)" opacity="0.9"/>
    <image href="%(uri)s" x="%(x)s" y="%(y)s" width="%(gw)s" height="%(gh)s"/>
  </g>

%(flare)s%(sparks)s
%(word)s
  <text x="98" y="216" font-family="%(mono)s" font-size="15" fill="#E9D5FF" letter-spacing="7">SOFTWARE ENGINEERING</text>
  <text x="100" y="244" font-family="%(mono)s" font-size="12.5" fill="#9F7AEA" letter-spacing="2.6">BSc @ LEICESTER  ·  JAVA · PYTHON · REACT  ·  UNITED KINGDOM</text>

  <!-- product-label furniture -->
%(bars)s  <text x="1024" y="310" font-family="%(mono)s" font-size="9.5" fill="#9F8DC0" letter-spacing="3.2">GITHUB.COM/JOSHIEV</text>

%(brackets)s
  <rect width="%(W)s" height="%(H)s" fill="url(#scan)"/>
  <rect x="0" y="%(rule)s" width="%(W)s" height="4" fill="url(#irid)"/>
</svg>
""" % dict(W=W, H=H, defs=DEFS, uri=uri, x=round(x, 1), y=round(y, 1), gw=gw, gh=gh,
           cx=cx, cy=cy, mono=MONO, sparks=sparks, bars=bars, rule=H - 4,
           grid=grid_floor(238, H, 600, W),
           flare=flare(742, 58, 96),
           word=chrome_text(92, 178, 92, "JOSHUA V"),
           brackets=corner_brackets(W, H))


# ---------------------------------------------------------------- footer

def build_footer():
    W, H = 1200, 210
    uri, gw, gh = embed(92, 142)          # Gastly
    cx, cy = 206, 104
    x, y = cx - gw / 2.0, cy - gh / 2.0

    huri, hw, hh = embed(94, 150)          # Gengar
    hcx, hcy = 1004, 102
    hx, hy = hcx - hw / 2.0, hcy - hh / 2.0

    sparks = "".join([
        sparkle(352, 44, 0.7, 0.8, 3.6, -0.5),
        sparkle(92, 156, 0.5, 0.6, 4.4, -2.0),
        sparkle(866, 46, 0.6, 0.7, 3.2, -1.2),
        sparkle(1124, 158, 0.44, 0.5, 5.0, -2.6),
    ])

    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %(W)s %(H)s" width="%(W)s" height="%(H)s" role="img" aria-label="Thanks for stopping by - github.com/joshieV">
  <defs>%(defs)s</defs>

  <rect width="%(W)s" height="%(H)s" fill="#000000"/>
  <rect x="0" y="0" width="%(W)s" height="4" fill="url(#irid)"/>

  <ellipse cx="%(cx)s" cy="%(cy)s" rx="152" ry="114" fill="url(#bloomA)"/>
  <ellipse cx="%(hcx)s" cy="%(hcy)s" rx="152" ry="114" fill="url(#bloomA)"/>

%(grid)s
  <g>
    <animateTransform attributeName="transform" type="translate"
                      values="0 0; 0 -11; 0 0" dur="6.5s" repeatCount="indefinite"/>
    <image href="%(uri)s" x="%(x)s" y="%(y)s" width="%(gw)s" height="%(gh)s"
           filter="url(#bloom)" opacity="0.85"/>
    <image href="%(uri)s" x="%(x)s" y="%(y)s" width="%(gw)s" height="%(gh)s"/>
  </g>

  <g>
    <animateTransform attributeName="transform" type="translate"
                      values="0 0; 0 9; 0 0" dur="7.5s" begin="-2.5s" repeatCount="indefinite"/>
    <image href="%(huri)s" x="%(hx)s" y="%(hy)s" width="%(hw)s" height="%(hh)s"
           filter="url(#bloom)" opacity="0.85"/>
    <image href="%(huri)s" x="%(hx)s" y="%(hy)s" width="%(hw)s" height="%(hh)s"/>
  </g>

%(sparks)s
%(word)s
  <text x="600" y="140" text-anchor="middle" font-family="%(mono)s" font-size="12"
        fill="#A855F7" letter-spacing="5">GITHUB.COM/JOSHIEV</text>

  <rect width="%(W)s" height="%(H)s" fill="url(#scan)"/>
</svg>
""" % dict(W=W, H=H, defs=DEFS, uri=uri, x=round(x, 1), y=round(y, 1), gw=gw, gh=gh,
           cx=cx, cy=cy, huri=huri, hx=round(hx, 1), hy=round(hy, 1),
           hw=hw, hh=hh, hcx=hcx, hcy=hcy, mono=MONO, sparks=sparks,
           grid=grid_floor(150, H, 600, W, rows=6, cols=11, opacity=0.32),
           word=chrome_text(600, 106, 34, "thanks for stopping by", letter=0,
                            weight=800, skew=-5, stroke_w=0.6, glow=0.4)
                .replace('<text x="0" y="0"', '<text text-anchor="middle" x="0" y="0"')
                .replace('<text x="6" y="8"', '<text text-anchor="middle" x="6" y="8"')
                .replace('<text x="3" y="4"', '<text text-anchor="middle" x="3" y="4"'))


# ---------------------------------------------------------------- divider

def build_divider():
    W, H = 1200, 34
    sparks = "".join([
        sparkle(300, 17, 0.5, 0.85, 3.3, -0.4),
        sparkle(600, 17, 0.62, 0.9, 4.0, -1.6),
        sparkle(900, 17, 0.46, 0.75, 3.6, -2.4),
    ])
    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %(W)s %(H)s" width="%(W)s" height="%(H)s" role="img" aria-label="">
  <defs>%(defs)s</defs>
  <rect x="0" y="12" width="%(W)s" height="10" rx="5" fill="url(#irid)"
        filter="url(#tinyglow)" opacity="0.35"/>
  <rect x="0" y="13" width="%(W)s" height="8" rx="4" fill="url(#bevel)" opacity="0.9"/>
  <rect x="0" y="14" width="%(W)s" height="1.4" fill="#FFFFFF" opacity="0.55"/>
  <rect x="0" y="12" width="%(W)s" height="10" fill="url(#scan)" opacity="0.5"/>
%(sparks)s</svg>
""" % dict(W=W, H=H, defs=DEFS, sparks=sparks)


if __name__ == "__main__":
    for name, svg in [("header.svg", build_header()),
                      ("footer.svg", build_footer()),
                      ("divider.svg", build_divider())]:
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print("%-14s %7.1f KB" % (name, os.path.getsize(path) / 1024))
