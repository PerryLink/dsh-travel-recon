#!/usr/bin/env python3
"""Generate README image assets for dsh-travel-recon (docs/assets/).

Outputs (idempotent overwrite):
  dsh-travel-recon-flow-light.svg / dsh-travel-recon-flow-dark.svg
      Hero pipeline diagram. Two hand-written SVG files (vector — never
      rasterized to webp). Text inside is command-surface tokens only
      (travel.ingest, travel.match, travel.export, ...), so all five README
      languages share the same pair.
  dsh-travel-recon-quickstart-{light,dark}.webp
      The real quickstart capture (docs/assets/quickstart.png, produced by
      `node samples/quickstart/run.mjs`, hashes in screenshots.json) framed
      on GitHub's light and dark page backgrounds. Content is not redrawn.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow (pip install pillow)
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# --- palette: PerryLink family (accent) + GitHub page backgrounds ----------
FAMILY = "#4B67B4"   # family accent (badges use labelColor #2B3245)
GREEN = {"light": "#16a34a", "dark": "#3fb950"}
SKIN = {
    "light": dict(bg="#ffffff", box="#f6f8fa", border="#d0d7de",
                  text="#1f2328", sub="#57606a", track="#eaeef2"),
    "dark": dict(bg="#0d1117", box="#161b22", border="#30363d",
                 text="#f0f6fc", sub="#8b949e", track="#21262d"),
}

# --- CJK font probe: captions must never render as tofu boxes --------------
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",      # Microsoft YaHei
    r"C:\Windows\Fonts\simhei.ttf",    # SimHei
    r"C:\Windows\Fonts\Deng.ttf",      # DengXian
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    sys.exit("FATAL: no CJK font found (looked for msyh.ttc, simhei.ttf, "
             "Deng.ttf, Noto Sans CJK, PingFang). Refusing to render text "
             "that could come out as tofu boxes; install one of the probed "
             "fonts and re-run.")


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


# ---------------------------------------------------------------------------
# 1. Hero pipeline SVG (light + dark) — tokens only, language-neutral
# ---------------------------------------------------------------------------
FLOW_NODES = [
    ("trips/invoices/cards.csv", "3 source CSV"),
    ("travel.ingest", "dedupe + duplicate report"),
    ("travel.match", "±0.01 tolerance"),
    ("travel.export", "xlsx · Trips / Matches"),
]


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    w, h = 1200, 430
    nw, nh, gap = 220, 96, 60
    y0 = 150
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="dsh-travel-recon pipeline">',
        '<title>dsh-travel-recon pipeline</title>',
        f'<rect width="{w}" height="{h}" rx="18" fill="{s["bg"]}"/>',
        f'<text x="60" y="62" fill="{s["text"]}" font-family="ui-sans-serif,'
        f'system-ui,sans-serif" font-size="30" font-weight="700">dsh-travel-recon</text>',
        f'<text x="60" y="94" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="16">local CSV → reconcile → xlsx ledger · '
        f'travel.ingest → travel.match → travel.export</text>',
        f'<line x1="60" y1="116" x2="1140" y2="116" stroke="{s["border"]}"/>',
    ]
    for i, (label, sub) in enumerate(FLOW_NODES):
        x = 60 + i * (nw + gap)
        accent = FAMILY if i in (1, 2) else s["border"]
        parts.append(
            f'<rect x="{x}" y="{y0}" width="{nw}" height="{nh}" rx="14" '
            f'fill="{s["box"]}" stroke="{accent}" stroke-width="2"/>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 40}" fill="{s["text"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="14" font-weight="700">{label}</text>')
        parts.append(
            f'<text x="{x + nw // 2}" y="{y0 + 68}" fill="{s["sub"]}" '
            f'text-anchor="middle" font-family="ui-monospace,monospace" '
            f'font-size="12">{sub}</text>')
        if i < len(FLOW_NODES) - 1:
            ax = x + nw + 6
            ay = y0 + nh // 2
            parts.append(
                f'<path d="M{ax} {ay}h{gap - 12}" stroke="{s["sub"]}" '
                f'stroke-width="3"/>')
            parts.append(
                f'<path d="M{ax + gap - 14} {ay - 7}l10 7-10 7" fill="none" '
                f'stroke="{s["sub"]}" stroke-width="3" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
    # read-only check surface (R0) — a side surface, not a pipeline stage
    bx, bw, by, bh = 60, 1080, 285, 50
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="12" '
        f'fill="{s["box"]}" stroke="{s["border"]}" stroke-width="1.5"/>')
    parts.append(
        f'<text x="{bx + bw // 2}" y="{by + 31}" fill="{s["sub"]}" '
        f'text-anchor="middle" font-family="ui-monospace,monospace" '
        f'font-size="13">R0 read-only: travel.duplicate_check · '
        f'travel.policy_check · travel.reuse_check · '
        f'travel.daily_limit_check</text>')
    parts.append(
        f'<text x="60" y="368" fill="{s["sub"]}" font-family="ui-monospace,'
        f'monospace" font-size="13">storage domain · '
        f'$DSH_HOME/storages/dsh-travel-recon · exports/travel-ledger.xlsx '
        f'· original CSV untouched</text>')
    parts.append(
        f'<text x="60" y="398" fill="{GREEN[skin]}" font-family="ui-monospace,'
        f'monospace" font-size="13">no model call · no network · '
        f'no upload</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# 2. Quickstart capture, framed for light + dark pages (real screenshot)
# ---------------------------------------------------------------------------
CAPTION = "quickstart · synthetic sample · not customer data"


def quickstart(skin: str) -> None:
    s = SKIN[skin]
    src = Image.open(os.path.join(OUT, "quickstart.png")).convert("RGB")
    img_w = 1000
    img_h = round(src.height * img_w / src.width)
    shot = src.resize((img_w, img_h), Image.LANCZOS)
    pad, cap_h = 40, 74
    w, h = img_w + pad * 2, img_h + cap_h + pad
    img = Image.new("RGB", (w, h), s["bg"])
    d = ImageDraw.Draw(img)
    d.text((pad, 30), CAPTION, font=font(22), fill=s["sub"])
    x, y = pad, cap_h
    img.paste(shot, (x, y))
    d.rounded_rectangle([x - 1, y - 1, x + img_w, y + img_h], radius=12,
                        outline=s["border"], width=2)
    img.save(os.path.join(OUT, f"dsh-travel-recon-quickstart-{skin}.webp"),
             "WEBP", quality=90)


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        with open(os.path.join(OUT, f"dsh-travel-recon-flow-{skin}.svg"),
                  "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
        quickstart(skin)
    print("wrote 2 SVG + 2 WebP assets to docs/assets/")


if __name__ == "__main__":
    main()
