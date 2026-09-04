#!/usr/bin/env python3
"""Regenerates assets/stats.svg from live GitHub data.

Third-party README stat-card services kept going down (github-readme-stats
returns 503, the activity-graph host now returns 402), and none of them can be
themed to match the banners, so the panel is rendered here instead. Standard
library only, so the workflow needs no pip install.

Usage:  GITHUB_TOKEN=... python scripts/build_stats.py
"""
import json
import os
import sys
import urllib.error
import urllib.request

USER = "joshieV"
API = "https://api.github.com"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "assets", "stats.svg")

MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,monospace"
SANS = "'Inter','Segoe UI',Helvetica,Arial,sans-serif"

W, H = 1200, 330

# Bar colours, cycled per language row.
SWATCH = ["#D946EF", "#A855F7", "#7C3AED", "#8B5CF6", "#6366F1", "#C026D3"]


def api(path, accept="application/vnd.github+json"):
    req = urllib.request.Request(API + path, headers={
        "Accept": accept,
        "User-Agent": USER + "-profile-stats",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def collect():
    user = api("/users/" + USER)
    repos = [r for r in api("/users/%s/repos?per_page=100" % USER) if not r["fork"]]

    langs = {}
    for repo in repos:
        for name, size in api("/repos/%s/languages" % repo["full_name"]).items():
            langs[name] = langs.get(name, 0) + size

    # The commit search API is the only public count of authored commits; it is
    # rate-limited harder than the rest, so a failure must not fail the build.
    try:
        commits = api("/search/commits?q=author:%s&per_page=1" % USER)["total_count"]
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError):
        commits = None

    return {
        "repos": len(repos),
        "stars": sum(r["stargazers_count"] for r in repos),
        "followers": user["followers"],
        "commits": commits,
        "langs": sorted(langs.items(), key=lambda kv: -kv[1]),
    }


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def readout(x, y, label, value):
    return (
        '  <text x="%s" y="%s" font-family="%s" font-size="11" fill="#9F7AEA"'
        ' letter-spacing="3.4">%s</text>\n'
        '  <text x="%s" y="%s" font-family="%s" font-size="46" font-weight="900"'
        ' fill="url(#num)" stroke="#F5F3FF" stroke-width="0.7"'
        ' paint-order="stroke fill" letter-spacing="-1">%s</text>\n'
    ) % (x, y, MONO, esc(label), x, y + 44, SANS, esc(value))


def lang_rows(langs, x, y, bar_w=330, step=30):
    total = sum(v for _, v in langs) or 1
    out = []
    for i, (name, size) in enumerate(langs[:6]):
        pct = 100.0 * size / total
        ry = y + i * step
        colour = SWATCH[i % len(SWATCH)]
        out.append(
            '  <text x="%s" y="%s" text-anchor="end" font-family="%s" font-size="12"'
            ' fill="#C4B5FD" letter-spacing="1.4">%s</text>\n'
            '  <rect x="%s" y="%s" width="%s" height="11" rx="5.5" fill="#1E0736"/>\n'
            '  <rect x="%s" y="%s" width="%.1f" height="11" rx="5.5" fill="%s"/>\n'
            '  <rect x="%s" y="%s" width="%.1f" height="3" rx="1.5" fill="#FFFFFF"'
            ' opacity="0.45"/>\n'
            '  <text x="%s" y="%s" font-family="%s" font-size="11.5" fill="#9F8DC0">%.1f%%</text>\n'
            % (x, ry + 10, MONO, esc(name),
               x + 14, ry, bar_w,
               x + 14, ry, max(bar_w * pct / 100.0, 6), colour,
               x + 16, ry + 2, max(bar_w * pct / 100.0 - 4, 4),
               x + 14 + bar_w + 12, ry + 10, MONO, pct)
        )
    return "".join(out)


def grid_floor(horizon_y, bottom_y, vp_x, width, rows=7, cols=11):
    out = ['  <g stroke="#A855F7" stroke-width="1" opacity="0.7" filter="url(#tiny)">\n']
    span = width * 1.9
    for i in range(-cols, cols + 1):
        out.append('    <line x1="%s" y1="%s" x2="%.1f" y2="%s"/>\n'
                   % (vp_x, horizon_y, vp_x + i * (span / (2.0 * cols)), bottom_y))
    depth = bottom_y - horizon_y
    for k in range(1, rows + 1):
        yy = horizon_y + depth * (float(k) / rows) ** 2.3
        out.append('    <line x1="0" y1="%.1f" x2="%s" y2="%.1f"/>\n' % (yy, width, yy))
    out.append('  </g>\n'
               '  <rect x="0" y="%s" width="%s" height="%s" fill="url(#fade)"/>\n'
               % (horizon_y - 6, width, depth + 6))
    return "".join(out)


def brackets(m=20, arm=30):
    d = ["M %s %s L %s %s L %s %s" % (m, m + arm, m, m, m + arm, m),
         "M %s %s L %s %s L %s %s" % (W - m - arm, m, W - m, m, W - m, m + arm),
         "M %s %s L %s %s L %s %s" % (m, H - m - arm, m, H - m, m + arm, H - m),
         "M %s %s L %s %s L %s %s" % (W - m - arm, H - m, W - m, H - m, W - m, H - m - arm)]
    return ('  <g fill="none" stroke="#A855F7" stroke-width="1.6" opacity="0.45">\n'
            + "".join('    <path d="%s"/>\n' % p for p in d) + "  </g>\n")


def render(s):
    commits = "{:,}".format(s["commits"]) if s["commits"] is not None else "—"
    stats = (readout(96, 120, "PUBLIC REPOS", s["repos"])
             + readout(300, 120, "COMMITS", commits)
             + readout(96, 226, "STARS EARNED", s["stars"])
             + readout(300, 226, "FOLLOWERS", s["followers"]))

    return """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %(W)s %(H)s" width="%(W)s" height="%(H)s" role="img" aria-label="GitHub statistics for %(user)s">
  <defs>
    <linearGradient id="num" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0.00" stop-color="#FFFFFF"/>
      <stop offset="0.34" stop-color="#E9D5FF"/>
      <stop offset="0.52" stop-color="#7C3AED"/>
      <stop offset="0.56" stop-color="#3B0764"/>
      <stop offset="0.78" stop-color="#D946EF"/>
      <stop offset="1.00" stop-color="#F5D0FE"/>
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
    <radialGradient id="pool" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0.00" stop-color="#C026D3" stop-opacity="0.30"/>
      <stop offset="0.55" stop-color="#7C3AED" stop-opacity="0.13"/>
      <stop offset="1.00" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0"    stop-color="#000000" stop-opacity="0.95"/>
      <stop offset="0.45" stop-color="#000000" stop-opacity="0.45"/>
      <stop offset="1"    stop-color="#000000" stop-opacity="0"/>
    </linearGradient>
    <filter id="tiny" x="-150%%" y="-150%%" width="400%%" height="400%%">
      <feGaussianBlur stdDeviation="2.2"/>
    </filter>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="1.4" fill="#000000" opacity="0.22"/>
    </pattern>
  </defs>

  <rect width="%(W)s" height="%(H)s" fill="#000000"/>
  <ellipse cx="260" cy="180" rx="330" ry="190" fill="url(#pool)"/>
  <ellipse cx="900" cy="170" rx="330" ry="190" fill="url(#pool)"/>

%(grid)s
  <text x="96" y="66" font-family="%(mono)s" font-size="11.5" fill="#B9A6DC" letter-spacing="4.5">OVERVIEW</text>
  <rect x="96" y="76" width="132" height="1.4" fill="#A855F7" opacity="0.7"/>

%(stats)s
  <text x="712" y="66" font-family="%(mono)s" font-size="11.5" fill="#B9A6DC" letter-spacing="4.5">LANGUAGES</text>
  <rect x="712" y="76" width="132" height="1.4" fill="#A855F7" opacity="0.7"/>
%(langs)s
%(brackets)s
  <rect width="%(W)s" height="%(H)s" fill="url(#scan)"/>
  <rect x="0" y="%(rule)s" width="%(W)s" height="4" fill="url(#irid)"/>
</svg>
""" % dict(W=W, H=H, user=USER, mono=MONO, stats=stats, rule=H - 4,
           grid=grid_floor(212, H, 600, W),
           langs=lang_rows(s["langs"], 780, 96),
           brackets=brackets())


def main():
    stats = collect()
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(render(stats))
    print("wrote %s  (repos=%s commits=%s stars=%s followers=%s)"
          % (OUT, stats["repos"], stats["commits"], stats["stars"], stats["followers"]))


if __name__ == "__main__":
    sys.exit(main())
