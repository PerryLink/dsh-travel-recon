#!/usr/bin/env python3
"""Generate the dsh-travel-recon README visuals (docs/assets/).

What the code actually does (src/core/travel.ts, src/plugin/tools.ts,
samples/quickstart/expected/result.json):

  three CSVs (trips / invoices / cards)  ->  travel.ingest parses them into
  integer cents under one key, trip_id; a repeated trip id is kept and
  reported (E_TRAVEL_TRIP_DUPLICATE), extra rows are counted in `skipped`.
  travel.match then takes exactly one invoice and one card per trip (1:1) and
  computes two signed gaps in cents:

      D1 = invoice - order        D2 = card - invoice

  both must satisfy |gap| <= 1 cent; otherwise the trip is one of three
  reasons: amount_mismatch / card_missing / invoice_missing. travel.export
  writes the Trips + Matches sheets through safeExportPath. Four further
  tools are read-only (duplicate_check, policy_check, reuse_check,
  daily_limit_check) and only return lists.

Outputs (idempotent overwrite):

  dsh-travel-recon-hero-{zh,en}-{light,dark}.webp
      1440x576 banner: left column (kicker, title, two value lines, sub,
      meta, footer) and a right-side reconciliation ticket that shows the two
      gaps of TRIP-1003 and the verdicts of all four sample trips.
  dsh-travel-recon-flow-v5-{light,dark}.svg
      1100x660 structure diagram: a per-trip reconciliation matrix (trip_id
      key, three documents, the two gap columns) that dispatches into the four
      match states, plus the R1 write / R0 read rails.
  dsh-travel-recon-quickstart-{light,dark}.webp
      The real quickstart capture (docs/assets/quickstart.png) framed on the
      light and dark page backgrounds. Content is not redrawn.

Every label is taken from the code, the READMEs or the gold result file; the
numbers are the synthetic quickstart sample (4 trips / 5 invoices / 3 cards,
matched 2, exceptions 2, duplicate 1, policy 1, daily over 1). No invented
features: there is no approval, no payment, no network, no model call.

Run:  python scripts/gen-readme-assets.py
"""

from __future__ import annotations

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

# Rendered at 2x and downsampled: crisp corners, soft shadows.
SS = 2
HERO_W, HERO_H = 1440, 576
FLOW_W, FLOW_H = 1100, 660

# --- fonts: Microsoft YaHei (CJK + Latin) and Consolas (machine tokens) -----
FONT_PATHS = {
    "sans": [
        r"C:\Windows\Fonts\msyh.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/PingFang.ttc",
    ],
    "sans-bold": [
        r"C:\Windows\Fonts\msyhbd.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ],
    "mono": [
        r"C:\Windows\Fonts\consola.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ],
    "mono-bold": [
        r"C:\Windows\Fonts\consolab.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    ],
}
FONTS: dict[str, str] = {}
for _name, _paths in FONT_PATHS.items():
    FONTS[_name] = next((p for p in _paths if os.path.exists(p)), "")
    if not FONTS[_name]:
        sys.exit(
            "FATAL: no usable font for %s (probed %s). Refusing to render "
            "Chinese as tofu boxes; install one of the probed fonts."
            % (_name, ", ".join(_paths))
        )

_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def fnt(kind: str, size: float, scale: int = 1) -> ImageFont.FreeTypeFont:
    key = (kind, max(1, int(round(size * scale))))
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(FONTS[kind], key[1])
    return _FONT_CACHE[key]


_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def tw(text: str, kind: str, size: float) -> float:
    """Text width in 1x layout pixels."""
    return _MEASURE.textlength(text, font=fnt(kind, size))


# --- palette: family #4B67B4 (dark #8496f5) on the light/dark canvases -----
PAL = {
    "light": dict(
        bg1="#f9f6fd",
        bg2="#e4eaf8",
        panel="#ffffff",
        panel_border="#e3ddf0",
        card="#f8f5fe",
        card_border="#e8e1f6",
        row="#f4f0fc",
        text="#171820",
        sub="#535a6d",
        muted="#8a8fa2",
        accent="#4B67B4",
        accent_soft="#ece7f9",
        ok="#177a55",
        ok_soft="#e4f4ec",
        bad="#b0332b",
        bad_soft="#fbeae8",
        warn="#9a6200",
        warn_soft="#fdf2e0",
        dot="#cdc5e4",
        shadow=(38, 30, 78, 44),
        glow="#8f7bd6",
        glow_alpha=17,
    ),
    "dark": dict(
        bg1="#131a2a",
        bg2="#0c1016",
        panel="#161e2f",
        panel_border="#2a3450",
        card="#1a2234",
        card_border="#2b3653",
        row="#1c2539",
        text="#eef1fb",
        sub="#a7b1c9",
        muted="#7a849d",
        accent="#8496f5",
        accent_soft="#232c49",
        ok="#63d29a",
        ok_soft="#0f2c25",
        bad="#ff9a94",
        bad_soft="#2a1a1d",
        warn="#f0b95b",
        warn_soft="#2a2316",
        dot="#39415c",
        shadow=(0, 0, 0, 96),
        glow="#4B67B4",
        glow_alpha=30,
    ),
}
SANS_FAMILY = "'Microsoft YaHei', 'Segoe UI', system-ui, sans-serif"
MONO_FAMILY = "Consolas, 'Courier New', monospace"


# --- Pillow helpers --------------------------------------------------------
class Art:
    def __init__(self, img: Image.Image):
        self.img = img
        self.d = ImageDraw.Draw(img)

    def rect(self, box, radius, fill=None, outline=None, width=1.4):
        self.d.rounded_rectangle(
            [v * SS for v in box],
            radius=radius * SS,
            fill=fill,
            outline=outline,
            width=max(1, int(round(width * SS))),
        )

    def text(self, xy, s, kind, size, fill, anchor="ls"):
        self.d.text(
            (xy[0] * SS, xy[1] * SS),
            s,
            font=fnt(kind, size, SS),
            fill=fill,
            anchor=anchor,
        )

    def line(self, p1, p2, fill, width=1.2):
        self.d.line(
            [p1[0] * SS, p1[1] * SS, p2[0] * SS, p2[1] * SS],
            fill=fill,
            width=max(1, int(round(width * SS))),
        )

    def dashed(self, x1, y1, x2, y2, fill, width=1.2, dash=6, gap=5):
        length = math.hypot(x2 - x1, y2 - y1)
        if length <= 0:
            return
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        pos = 0.0
        while pos < length:
            end = min(pos + dash, length)
            self.line(
                (x1 + ux * pos, y1 + uy * pos),
                (x1 + ux * end, y1 + uy * end),
                fill,
                width,
            )
            pos = end + gap

    def circle(self, center, r, fill=None, outline=None, width=1.4):
        self.d.ellipse(
            [
                (center[0] - r) * SS,
                (center[1] - r) * SS,
                (center[0] + r) * SS,
                (center[1] + r) * SS,
            ],
            fill=fill,
            outline=outline,
            width=max(1, int(round(width * SS))),
        )


def hx(color: str, alpha: int = 255):
    value = color.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha)


def shadow(img, box, radius, blur=15, dy=9, color=(38, 30, 78, 44)):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = [v * SS for v in box]
    d.rounded_rectangle(
        (x0, y0 + dy * SS, x1, y1 + dy * SS), radius=radius * SS, fill=color
    )
    layer = layer.filter(ImageFilter.GaussianBlur(blur * SS * 0.7))
    img.alpha_composite(layer)


def glow(img, center, radius, color, alpha):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy, r = center[0] * SS, center[1] * SS, radius * SS
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=hx(color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.55))
    img.alpha_composite(layer)


def gradient(size, c1, c2):
    w, h = size
    vertical = Image.linear_gradient("L").resize((w, h))
    horizontal = Image.linear_gradient("L").rotate(90, expand=True).resize((w, h))
    mask = Image.blend(vertical, horizontal, 0.42)
    return Image.composite(
        Image.new("RGB", (w, h), c2), Image.new("RGB", (w, h), c1), mask
    )


def dot_field(img, color, alpha, step=26, radius=1.3):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(step // 2, img.size[1], step * SS):
        for x in range(step // 2, img.size[0], step * SS):
            r = radius * SS
            d.ellipse((x - r, y - r, x + r, y + r), fill=hx(color, alpha))
    img.alpha_composite(layer)


def fit_size(lines, kind, maxw, start, floor, step=1):
    size = start
    while size >= floor:
        if all(tw(line, kind, size) <= maxw for line in lines):
            return size
        size -= step
    raise SystemExit("FATAL: cannot fit text: %r" % (lines,))


def has_cjk(text: str) -> bool:
    for ch in text:
        code = ord(ch)
        if (0x2E80 <= code <= 0x9FFF or 0x3000 <= code <= 0x303F
                or 0xF900 <= code <= 0xFAFF or 0xFE30 <= code <= 0xFE4F
                or 0xFF00 <= code <= 0xFFEF):
            return True
    return False


def pick_kind(text: str, prefer_mono: bool = True) -> str:
    """Consolas has no CJK glyphs; mixed strings must use the CJK face."""
    return "mono" if prefer_mono and not has_cjk(text) else "sans"


def require(cond, message):
    if not cond:
        raise SystemExit("FATAL: layout check failed: " + message)


def chip(art, x, y, text, fg, bg, border=None, size=13, mono=True, height=26,
         padx=11):
    kind = "mono" if mono else "sans"
    w = tw(text, kind, size) + padx * 2
    art.rect((x, y, x + w, y + height), height / 2, fill=bg, outline=border,
             width=1.2)
    art.text((x + padx, y + height / 2 + 1), text, kind, size, fg, anchor="lm")
    return w


# --- hero copy (numbers come from samples/quickstart/expected/result.json) --
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness · 差旅对账插件",
        title="dsh-travel-recon",
        lines=["行程 × 发票 × 卡流水，逐趟对到分",
               "对不上的、重复的、超标的，全列清"],
        sub="三份 CSV 进，两表 xlsx 出 · 不联网 · 不调模型",
        meta="travel.ingest · travel.match · travel.export · v0.1.1",
        foot="社区插件 · 与 DeepSeek 无关 · 仅公开 / 合成样例",
        panel_head="对账卡 · 逐趟",
        panel_meta="合成样例 · 4 趟 · 单位 元",
        trip="TRIP-1003",
        route="PEK → CAN",
        stamp="2026-04-01 · EMP-01",
        stubs=[("订单 trips", "2 450.00"),
               ("发票 invoices", "2 400.00"),
               ("卡流水 cards", "2 400.00")],
        gaps=[("Δ1 发票 − 订单", "-50.00", -5000, False, "超差 1 分"),
              ("Δ2 卡流水 − 发票", "0.00", 0, True, "在带内")],
        state="amount_mismatch",
        detail="Δ1 超出 ±0.01 容差 · Δ2 命中",
        ids="INV-2003 · CARD-3003",
        note="1:1 只取首条 · 多余发票由 duplicate_check 另列",
        trio=[("TRIP-1001", "matched", "Δ1 0.00 · Δ2 0.00", "ok"),
              ("TRIP-1002", "matched", "发票 ×2 · INV-2004 另列", "ok"),
              ("TRIP-1004", "card_missing", "Δ2 -320.00 · 无卡流水", "bad")],
        tally="matched 2 · exceptions 2 · duplicate 1 · policy 1 · daily over 1",
        footer=("exports/travel-ledger.xlsx · Trips / Matches · ",
                "原 CSV 只读"),
    ),
    "en": dict(
        kicker="DeepSeek Harness · travel reconciliation plugin",
        title="dsh-travel-recon",
        lines=["Trip, invoice, card — matched per trip",
               "Gaps, double claims, over-limit days, listed"],
        sub="Three CSVs in, one two-sheet xlsx out · offline",
        meta="travel.ingest · travel.match · travel.export · v0.1.1",
        foot="Community plugin · not affiliated with DeepSeek",
        panel_head="Reconciliation card",
        panel_meta="synthetic · 4 trips · CNY",
        trip="TRIP-1003",
        route="PEK → CAN",
        stamp="2026-04-01 · EMP-01",
        stubs=[("order trips", "2,450.00"),
               ("invoice", "2,400.00"),
               ("card", "2,400.00")],
        gaps=[("Δ1 invoice − order", "-50.00", -5000, False, "over 1 cent"),
              ("Δ2 card − invoice", "0.00", 0, True, "in band")],
        state="amount_mismatch",
        detail="Δ1 exceeds the ±0.01 band · Δ2 passes",
        ids="INV-2003 · CARD-3003",
        note="1:1 first match · extras listed by duplicate_check",
        trio=[("TRIP-1001", "matched", "Δ1 0.00 · Δ2 0.00", "ok"),
              ("TRIP-1002", "matched", "2 invoices · INV-2004", "ok"),
              ("TRIP-1004", "card_missing", "Δ2 -320.00 · no card", "bad")],
        tally="matched 2 · exceptions 2 · duplicate 1 · policy 1 · daily over 1",
        footer=("exports/travel-ledger.xlsx · Trips / Matches · ",
                "source CSV read-only"),
    ),
}


def draw_gauge(art, cx, y, value_cents, passed, P, half=64.0):
    """Tolerance rail: a ±1-cent band at the centre, a marker for the gap."""
    ink = P["ok"] if passed else P["bad"]
    art.rect((cx - half, y - 3, cx + half, y + 3), 3, fill=P["card_border"])
    band = 15
    art.rect((cx - band / 2, y - 5, cx + band / 2, y + 5), 5,
             fill=P["ok_soft"], outline=P["ok"] + "66", width=1.1)
    for sign in (-1, 1):
        edge = cx + sign * band / 2
        art.line((edge, y - 8), (edge, y + 8), P["ok"] + "99", 1.2)
    if passed:
        mx = cx + (value_cents / 100.0) * (band / 2)
    else:
        mx = cx + (-1 if value_cents < 0 else 1) * (half - 8)
    art.circle((mx, y), 5.0, fill=ink)
    art.circle((mx, y), 5.0, outline=P["panel"], width=1.8)


def draw_hero(lang: str, skin: str) -> Image.Image:
    P = PAL[skin]
    T = HERO[lang]
    img = gradient((HERO_W * SS, HERO_H * SS), P["bg1"], P["bg2"]).convert("RGBA")
    dot_field(img, P["dot"], 26 if skin == "light" else 34)
    glow(img, (150, 120), 340, P["glow"], P["glow_alpha"])
    glow(img, (1220, 470), 300, P["glow"], P["glow_alpha"])
    art = Art(img)

    # ---------------- left column: kicker / title / values / meta ----------
    x0, left_max = 48, 700
    kicker_size = 18
    kw = tw(T["kicker"], "sans", kicker_size) + 40
    require(kw <= left_max, "hero kicker wider than the left column")
    art.rect((x0, 50, x0 + kw, 90), 20, fill=P["accent_soft"],
             outline=P["accent"] + "55", width=1.2)
    art.text((x0 + 20, 78), T["kicker"], "sans", kicker_size, P["accent"])

    title_size = 80
    require(tw(T["title"], "sans-bold", title_size) <= left_max,
            "hero title wider than the left column")
    art.text((x0, 226), T["title"], "sans-bold", title_size, P["text"])

    value_size = fit_size(T["lines"], "sans-bold", 668, 34, 28)
    for index, line in enumerate(T["lines"]):
        art.text((x0, 306 + index * 46), line, "sans-bold", value_size,
                 P["text"])

    sub_size = fit_size([T["sub"]], "sans", left_max, 25, 25)
    art.text((x0, 406), T["sub"], "sans", sub_size, P["sub"])

    meta_size = fit_size([T["meta"]], "sans", left_max, 20, 17)
    art.text((x0, 450), T["meta"], "sans", meta_size, P["muted"])

    art.line((x0, 482), (x0 + 236, 482), P["panel_border"], 1.4)
    foot_size = fit_size([T["foot"]], "sans", left_max, 20, 17)
    art.text((x0, 516), T["foot"], "sans", foot_size, P["muted"])

    # ---------------- right panel: one reconciliation ticket ----------------
    px, py, pw, ph = 748, 34, 656, 508
    shadow(img, (px, py, px + pw, py + ph), 22, 16, 9, P["shadow"])
    art.rect((px, py, px + pw, py + ph), 22, fill=P["panel"],
             outline=P["panel_border"], width=1.3)

    ix = px + 24
    ixr = px + pw - 24
    art.text((ix, 78), T["panel_head"], "sans-bold", 22, P["text"])
    art.text((ixr, 78), T["panel_meta"], "sans", 13.5, P["muted"], anchor="rs")
    art.line((ix, 100), (ixr, 100), P["panel_border"], 1.2)

    # ticket
    tx, ty, twd, tht = px + 22, 112, pw - 44, 292
    require(tx + twd <= px + pw - 20, "hero ticket wider than its panel")
    art.rect((tx, ty, tx + twd, ty + tht), 18, fill=P["card"],
             outline=P["card_border"], width=1.3)
    for cx in (tx, tx + twd):
        art.circle((cx, ty + 146), 9, fill=P["panel"])
        art.circle((cx, ty + 146), 9, outline=P["card_border"], width=1.2)

    art.text((tx + 24, ty + 36), T["trip"], "mono-bold", 23, P["text"])
    art.text((tx + 24, ty + 60), T["stamp"], "mono", 13.5, P["muted"])
    art.text((tx + twd - 24, ty + 34), T["route"], "mono", 14.5, P["sub"],
             anchor="rs")
    art.dashed(tx + 20, ty + 74, tx + twd - 20, ty + 74, P["card_border"],
               1.2, 5, 5)

    # three document stubs, separated like a ticket
    stub_w, sep = 172, 28
    centers = [tx + 24 + stub_w / 2, tx + 24 + stub_w + sep + stub_w / 2,
               tx + 24 + 2 * (stub_w + sep) + stub_w / 2]
    for index, (label, amount) in enumerate(T["stubs"]):
        cx = centers[index]
        art.text((cx, ty + 98), label, "sans", 13.5, P["muted"], anchor="ms")
        art.text((cx, ty + 138), amount, "mono-bold", 25, P["text"],
                 anchor="ms")
        if index < 2:
            sx = tx + 24 + (stub_w + sep) * (index + 1) - sep / 2
            art.dashed(sx, ty + 84, sx, ty + 148, P["card_border"], 1.2, 4, 4)

    # the two gaps: each one is a signed delta against the ±0.01 band
    cell_w, gap_x = 280, tx + 24
    for index, (label, value, cents, passed, verdict) in enumerate(T["gaps"]):
        cx0 = gap_x + index * (cell_w + 12)
        cx1 = cx0 + cell_w
        ink = P["ok"] if passed else P["bad"]
        bg = P["ok_soft"] if passed else P["bad_soft"]
        art.rect((cx0, ty + 154, cx1, ty + 226), 14, fill=bg,
                 outline=ink + "33", width=1.2)
        art.text((cx0 + 14, ty + 177), label, "sans", 13, P["sub"])
        art.text((cx1 - 14, ty + 177), "±0.01 容差" if lang == "zh"
                 else "±0.01 tol.", "sans", 11.5, P["muted"], anchor="rs")
        art.text((cx0 + 14, ty + 205), value, "mono-bold", 21, ink)
        vw = tw(value, "mono-bold", 21)
        art.text((cx0 + 24 + vw, ty + 205), verdict, "sans", 12.5, ink)
        draw_gauge(art, cx0 + cell_w / 2, ty + 219, cents, passed, P,
                   half=64)

    # state row
    sx = tx + 24
    sy = ty + 238
    cw = chip(art, sx, sy, T["state"], P["bad"], P["panel"],
              P["bad"] + "66", 13, True, 26)
    art.text((sx + cw + 10, sy + 18), T["detail"], "sans", 13, P["sub"])
    art.text((tx + twd - 24, sy + 18), T["ids"], "mono", 13, P["muted"],
             anchor="rs")
    art.text((sx, sy + 42), T["note"], "sans", 12, P["muted"])

    # verdict strip: the other three sample trips
    trio_y, chip_w, gap = 416, 200, 6
    for index, (tid, state, detail, tone) in enumerate(T["trio"]):
        cx0 = tx + index * (chip_w + gap)
        cx1 = cx0 + chip_w
        ink = P["ok"] if tone == "ok" else P["bad"]
        bg = P["ok_soft"] if tone == "ok" else P["bad_soft"]
        art.rect((cx0, trio_y, cx1, trio_y + 38), 12, fill=bg,
                 outline=ink + "44", width=1.1)
        art.circle((cx0 + 15, trio_y + 14), 3.4, fill=ink)
        art.text((cx0 + 27, trio_y + 19), tid, "mono-bold", 13, P["text"])
        art.text((cx1 - 12, trio_y + 19), state, "mono", 11.5, ink,
                 anchor="rs")
        art.text((cx0 + 15, trio_y + 33), detail, pick_kind(detail), 11.5,
                 P["muted"])
        require(tw(detail, pick_kind(detail), 11.5) <= chip_w - 27,
                "hero verdict detail overflows: " + detail)
        require(cx1 <= px + pw - 20, "hero verdict chip overflows the panel")

    art.text((ix, 480), T["tally"], "mono", 13, P["sub"])
    require(tw(T["tally"], "mono", 13) <= ixr - ix, "hero tally too wide")
    art.line((ix, 498), (ixr, 498), P["panel_border"], 1.2)
    mono_foot, sans_foot = T["footer"]
    art.text((ix, 522), mono_foot, "mono", 13, P["muted"])
    fx = ix + tw(mono_foot, "mono", 13)
    art.text((fx, 522), sans_foot, "sans", 13, P["muted"])
    require(fx + tw(sans_foot, "sans", 13) <= ixr,
            "hero footer too wide")

    return img.resize((HERO_W, HERO_H), Image.LANCZOS).convert("RGB")


# --- flow SVG: 1100x660, matrix + dispatch --------------------------------
FLOW_TEXT = {
    "title": "dsh-travel-recon",
    "subtitle": "三份 CSV 逐趟对账：一个 trip_id、两段分差、四态分派",
    "pill": "v0.1.1 · 不联网 · 不调模型",
    "sec1": "① 逐趟对账矩阵 · travel.ingest 按 trip_id 对齐三份 CSV（4 / 5 / 3 行）",
    "sec1_note": "两段分差各以 ±0.01 元（1 分）为界",
    "sec2": "② 状态分派 · 每趟只取 1 张发票 + 1 笔卡流水（1:1）",
    "sec2_note": "状态由 travel.match 写入 Matches 表",
    "cols": [
        ("trip_id", "键 key"),
        ("订单 trips", "trips.csv · 4 行"),
        ("Δ1", "订单→发票"),
        ("发票 invoices", "invoices.csv · 5 行"),
        ("Δ2", "发票→卡流水"),
        ("卡流水 cards", "cards.csv · 3 行"),
        ("状态 state", "4 态 · travel.match"),
    ],
    "rows": [
        ("TRIP-1001", "PEK→SHA", "EMP-01 · 04-01", "1 280.00", 0,
         "1 280.00", "INV-2001", False, 0, "1 280.00", "CARD-3001",
         ("matched", "ok"), "两段分差均 0.00"),
        ("TRIP-1002", "SZX→HGH", "EMP-02 · 04-02", "860.00", 0,
         "860.00", "INV-2002", True, 0, "860.00", "CARD-3002",
         ("matched", "ok"), "发票另有 1 条（×2）"),
        ("TRIP-1003", "PEK→CAN", "EMP-01 · 04-01", "2 450.00", -5000,
         "2 400.00", "INV-2003", False, 0, "2 400.00", "CARD-3003",
         ("amount_mismatch", "bad"), "Δ1 超差 -5 000 分"),
        ("TRIP-1004", "CTU→XIY", "EMP-03 · 04-03", "320.00", 0,
         "320.00", "INV-2005", False, -32000, None, None,
         ("card_missing", "bad"), "Δ2 无卡流水 -32 000 分"),
    ],
    "bins": [
        ("matched", "ok", "2 趟", "TRIP-1001 · TRIP-1002",
         "→ Matches 表 · state=matched"),
        ("amount_mismatch", "bad", "1 趟", "TRIP-1003 · Δ1 -50.00",
         "→ 例外清单 · 附两段分差"),
        ("card_missing", "bad", "1 趟", "TRIP-1004 · Δ2 -320.00",
         "→ 例外清单 · 补卡流水"),
        ("invoice_missing", "muted", "0 趟", "本次样例未出现",
         "→ 缺发票时落这里"),
    ],
    "r1_head": "R1 · 本地写 3 个工具",
    "r1_tools": "travel.ingest → travel.match → travel.export",
    "r1_path": "storages/dsh-travel-recon/exports/travel-ledger.xlsx",
    "r1_counts": "Trips 5 行 · Matches 5 行 · 原 CSV 只读",
    "r1_note": "safeExportPath：越界 / 非法路径直接失败",
    "r0_head": "R0 · 只读 4 个工具（只列清单，不改单、不审批）",
    "r0_tools": "duplicate_check · policy_check · reuse_check · daily_limit",
    "r0_dup": "duplicate 1 张（TRIP-1002 发票 ×2，保留不合并）· reuse 0",
    "r0_policy": "policy 1：TRIP-1003 2 450.00 > 上限 2 000.00",
    "r0_daily": "daily 1 天：EMP-01 04-01 合计 3 730.00（超 730.00）",
    "foot": "原 CSV 只读 · 导出前经 safeExportPath 校验 · 不联网 · 不调模型 · 不上传",
    "alt": (
        "dsh-travel-recon 结构：三份 CSV（行程 4 行、发票 5 行、卡流水 3 行）"
        "由 travel.ingest 按 trip_id 对齐成逐趟对账矩阵，每趟并列订单 / 发票 / "
        "卡流水三列，中间是两段带符号分差 Δ1 = 发票 − 订单、Δ2 = 卡流水 − "
        "发票，两段都以 ±0.01 元（1 分）为界；矩阵结果按四态分派——matched 2 "
        "趟进 Matches 表，amount_mismatch（TRIP-1003，Δ1 -50.00）与 "
        "card_missing（TRIP-1004，Δ2 -320.00）进例外清单，invoice_missing 为 "
        "0；R1 本地写轨的 ingest → match → export 写 "
        "storages/dsh-travel-recon/exports/travel-ledger.xlsx（Trips / "
        "Matches），R0 只读轨的 duplicate / policy / reuse / daily_limit 只返回"
        "清单；原 CSV 只读，不联网、不调模型。"
    ),
}


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def money(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    value = abs(cents)
    whole = "%d" % (value // 100)
    groups = []
    while len(whole) > 3:
        groups.insert(0, whole[-3:])
        whole = whole[:-3]
    groups.insert(0, whole)
    return "%s%s.%02d" % (sign, ",".join(groups), value % 100)


class Svg:
    def __init__(self, palette):
        self.P = palette
        self.parts: list[str] = []
        self.problems: list[str] = []

    def add(self, raw: str):
        self.parts.append(raw)

    def width(self, text, kind, size):
        return tw(text, "mono" if kind == "mono" else "sans", size)

    def text(self, x, y, text, size, fill, kind="sans", anchor="start",
             weight="400", limit=None, label=""):
        w = self.width(text, kind, size)
        if limit is not None:
            if anchor == "start" and x + w > limit + 0.6:
                self.problems.append(
                    "%s: %r ends %.1f > %.1f" % (label, text, x + w, limit))
            if anchor == "end" and x - w < limit - 0.6:
                self.problems.append(
                    "%s: %r starts %.1f < %.1f" % (label, text, x - w, limit))
        family = MONO_FAMILY if kind == "mono" else SANS_FAMILY
        self.add(
            '<text x="%.1f" y="%.1f" fill="%s" font-family="%s" '
            'font-size="%.2f" font-weight="%s" text-anchor="%s">%s</text>'
            % (x, y, fill, family, size, weight,
               {"start": "start", "end": "end", "middle": "middle"}[anchor],
               esc(text))
        )

    def rect(self, x, y, w, h, radius=10, fill="none", stroke=None,
             width=1.4, dash=None, opacity=None):
        bits = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                'rx="%.1f" fill="%s"' % (x, y, w, h, radius, fill)]
        if stroke:
            bits.append(' stroke="%s" stroke-width="%.2f"' % (stroke, width))
        if opacity is not None:
            bits.append(' opacity="%.2f"' % opacity)
        if dash:
            bits.append(' stroke-dasharray="%s"' % dash)
        self.add("".join(bits) + "/>")

    def line(self, x1, y1, x2, y2, stroke, width=1.2, dash=None,
             opacity=None, cap="round"):
        bits = ['<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                'stroke="%s" stroke-width="%.2f" stroke-linecap="%s"'
                % (x1, y1, x2, y2, stroke, width, cap)]
        if dash:
            bits.append(' stroke-dasharray="%s"' % dash)
        if opacity is not None:
            bits.append(' opacity="%.2f"' % opacity)
        self.add("".join(bits) + "/>")

    def circle(self, cx, cy, r, fill="none", stroke=None, width=1.2):
        bits = ['<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"'
                % (cx, cy, r, fill)]
        if stroke:
            bits.append(' stroke="%s" stroke-width="%.2f"' % (stroke, width))
        self.add("".join(bits) + "/>")

    def path(self, d, stroke, width=1.6, fill="none", cap="round"):
        self.add('<path d="%s" fill="%s" stroke="%s" stroke-width="%.2f" '
                 'stroke-linecap="%s" stroke-linejoin="round"/>'
                 % (d, fill, stroke, width, cap))

    def chip(self, x, y, text, fg, bg, border, size=13, height=24, padx=10,
             mono=True, weight="700"):
        kind = "mono" if mono else "sans"
        w = self.width(text, kind, size) + padx * 2
        self.rect(x, y, w, height, height / 2, fill=bg, stroke=border,
                  width=1.1)
        self.add(
            '<text x="%.1f" y="%.1f" fill="%s" font-family="%s" '
            'font-size="%.2f" font-weight="%s" text-anchor="middle">%s</text>'
            % (x + w / 2, y + height / 2 + size * 0.36, fg,
               MONO_FAMILY if mono else SANS_FAMILY, size, weight, esc(text))
        )
        return w

    def svg(self):
        return "\n".join(self.parts) + "\n"


def flow_svg(skin: str) -> str:
    P = PAL[skin]
    T = FLOW_TEXT
    s = Svg(P)
    accent, text, sub, muted = P["accent"], P["text"], P["sub"], P["muted"]
    border, card_bg, panel, row_bg = P["panel_border"], P["card"], P["panel"], P["row"]

    def tone(name):
        if name == "ok":
            return P["ok"], P["ok_soft"], P["ok"] + "66"
        if name == "bad":
            return P["bad"], P["bad_soft"], P["bad"] + "66"
        return sub, row_bg, border

    s.add('<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="660" '
          'viewBox="0 0 1100 660" role="img" aria-label="%s">' % esc(T["alt"]))
    s.add("<title>%s</title>" % esc(
        "dsh-travel-recon: per-trip reconciliation matrix with two gap "
        "columns, four-state dispatch, R1 write / R0 read rails"))
    s.add('<rect width="1100" height="660" fill="%s"/>' % panel)

    # ---- header
    s.text(40, 60, T["title"], 30, text, "sans", weight="700")
    s.text(40, 88, T["subtitle"], 15, sub)
    pill_w = s.width(T["pill"], "sans", 12.5) + 30
    s.rect(1060 - pill_w, 40, pill_w, 28, 14, fill=P["accent_soft"],
           stroke=accent + "55", width=1.1)
    s.add('<text x="%.1f" y="58.5" fill="%s" font-family="%s" font-size="12.5" '
          'font-weight="400" text-anchor="middle">%s</text>'
          % (1060 - pill_w / 2, accent, SANS_FAMILY, esc(T["pill"])))
    s.line(40, 102, 1060, 102, border, 1.2)

    # ---- section 1 label
    s.text(40, 128, T["sec1"], 16.5, text, "sans", weight="700", limit=860,
           label="sec1")
    s.text(1060, 128, T["sec1_note"], 12, muted, "sans", anchor="end",
           limit=730, label="sec1_note")

    # ---- matrix geometry
    cols = [40, 176, 318, 428, 570, 680, 822, 1060]
    top, header_h, row_h, gap = 142, 44, 52, 4
    zebra_top = top + header_h
    s.rect(40, top, 1020, header_h, 10, fill=row_bg)
    for index, (head, note) in enumerate(T["cols"]):
        cx0, cx1 = cols[index], cols[index + 1]
        if index in (0, 1, 3, 5, 6):
            s.text(cx0 + 12, top + 22, head, 13.5, text, "sans", weight="700",
                   limit=cx1 - 12, label="col head %d" % index)
        else:
            s.text(cx0 + 12, top + 22, head, 16, accent, "sans", weight="700",
                   limit=cx1 - 10, label="col head %d" % index)
        s.text(cx0 + 12, top + 38, note, 12, muted, "sans",
               limit=cx1 - 12, label="col note %d" % index)

    # zebra rows + gap-column tint
    for index, _ in enumerate(T["rows"]):
        ry = zebra_top + index * (row_h + gap)
        if index % 2 == 0:
            s.rect(40, ry, 1020, row_h, 9, fill=card_bg)
    for cx0, cx1 in ((318, 428), (570, 680)):
        s.rect(cx0, zebra_top, cx1 - cx0, len(T["rows"]) * (row_h + gap) - gap,
               0, fill=P["accent_soft"], opacity=0.42)
    for edge in (176, 318, 428, 570, 680, 822):
        s.line(edge, top, edge, 410, border, 1.0, dash="3 5", opacity=0.75)
    s.line(40, 410, 1060, 410, border, 1.2)

    # ---- matrix rows
    for index, entry in enumerate(T["rows"]):
        (tid, route, stamp, order, d1, inv, inv_id, dup, d2, card_amt, card_id,
         state, reason) = entry
        ry = zebra_top + index * (row_h + gap)
        s.text(52, ry + 21, tid, 15, text, "mono", weight="700",
               limit=176 - 12, label="trip id")
        s.text(52, ry + 38, route, 12, muted, "mono", limit=176 - 12,
               label="route")
        s.text(318 - 12, ry + 22, order, 14.5, text, "mono", anchor="end",
               limit=176 + 12, label="order amount")
        s.text(318 - 12, ry + 38, stamp, 12, muted, "mono", anchor="end",
               limit=176 + 12, label="employee/date")
        # gap 1
        s.text(373, ry + 21, money(d1), 13.5,
               P["ok"] if abs(d1) <= 1 else P["bad"], "mono", anchor="middle")
        draw_svg_gauge(s, 373, ry + 34, d1, P)
        s.text(570 - 12, ry + 22, inv, 14.5, text, "mono", anchor="end",
               limit=436, label="invoice amount")
        s.text(570 - 12, ry + 38, inv_id, 12, muted, "mono", anchor="end",
               limit=436, label="invoice id")
        if dup:
            s.rect(436, ry + 6, 26, 17, 8.5, fill=P["warn_soft"],
                   stroke=P["warn"] + "77", width=1.0)
            s.add('<text x="%.1f" y="%.1f" fill="%s" font-family="%s" '
                  'font-size="11" font-weight="700" text-anchor="middle">'
                  '×2</text>' % (449, ry + 18.5, P["warn"], MONO_FAMILY))
        # gap 2
        s.text(625, ry + 21, money(d2), 13.5,
               P["ok"] if abs(d2) <= 1 else P["bad"], "mono", anchor="middle")
        draw_svg_gauge(s, 625, ry + 34, d2, P)
        if card_amt is None:
            s.text(822 - 12, ry + 22, "—", 14.5, muted, "mono", anchor="end")
            s.text(822 - 12, ry + 38, "无卡流水", 12, muted, "sans",
                   anchor="end", limit=680 + 12, label="card missing note")
        else:
            s.text(822 - 12, ry + 22, card_amt, 14.5, text, "mono", anchor="end",
                   limit=680 + 12, label="card amount")
            s.text(822 - 12, ry + 38, card_id, 12, muted, "mono", anchor="end",
                   limit=680 + 12, label="card id")
        fg, bg, stroke = tone(state[1])
        s.chip(832, ry + 8, state[0], fg, bg, stroke, 13, 24, 10)
        s.text(832, ry + 45, reason, 12, muted, "sans", limit=1060 - 12,
               label="state reason")

    # ---- dispatch
    s.text(40, 428, T["sec2"], 14.5, text, "sans", weight="700", limit=760,
           label="sec2")
    s.text(1060, 428, T["sec2_note"], 12, muted, "sans", anchor="end",
           limit=520, label="sec2_note")

    bin_y, bin_h, bin_w = 440, 82, 252
    centers = [40 + index * (bin_w + 4) + bin_w / 2 for index in range(4)]
    s.line(550, 410, 550, 434, border, 1.4)
    s.line(centers[0], 434, centers[-1], 434, border, 1.4)
    for cx in centers:
        s.line(cx, 434, cx, bin_y, border, 1.4)
        s.circle(cx, 434, 2.6, fill=border)
    s.circle(550, 434, 2.6, fill=border)

    for index, (name, tname, count, sample, dest) in enumerate(T["bins"]):
        bx = 40 + index * (bin_w + 4)
        fg, bg, stroke = tone(tname)
        s.rect(bx, bin_y, bin_w, bin_h, 14, fill=card_bg, stroke=border,
               width=1.1)
        s.rect(bx, bin_y, bin_w, 3, 1.5, fill=fg, opacity=0.85)
        s.chip(bx + 12, bin_y + 9, name, fg, bg, stroke, 13, 24, 10)
        s.text(bx + bin_w - 12, bin_y + 26, count, 14, text, "sans",
               anchor="end", weight="700")
        s.text(bx + 12, bin_y + 47, sample, 12, muted, "mono",
               limit=bx + bin_w - 12, label="bin sample %d" % index)
        s.text(bx + 12, bin_y + 66, dest, 12, sub, "sans",
               limit=bx + bin_w - 12, label="bin dest %d" % index)

    # ---- rails
    rail_y, rail_h = 528, 100
    rows = (
        (T["r1_head"], T["r1_tools"], T["r1_path"], T["r1_counts"],
         T["r1_note"]),
        (T["r0_head"], T["r0_tools"], T["r0_dup"], T["r0_policy"],
         T["r0_daily"]),
    )
    for index, (head, tools, line2, line3, line4) in enumerate(rows):
        bx = 40 if index == 0 else 532
        bw = 484 if index == 0 else 528
        s.rect(bx, rail_y, bw, rail_h, 16, fill=card_bg, stroke=border, width=1.1)
        s.rect(bx, rail_y, 3, rail_h, 1.5, fill=P["accent"], opacity=0.9)
        s.text(bx + 18, rail_y + 21, head, 14, text, "sans", weight="700",
               limit=bx + bw - 14, label="rail head %d" % index)
        s.text(bx + 18, rail_y + 40, tools, 12, accent, "mono",
               limit=bx + bw - 14, label="rail tools %d" % index)
        s.text(bx + 18, rail_y + 57, line2, 12, sub, "sans",
               limit=bx + bw - 14, label="rail line2 %d" % index)
        s.text(bx + 18, rail_y + 73, line3, 12, sub, "sans",
               limit=bx + bw - 14, label="rail line3 %d" % index)
        s.text(bx + 18, rail_y + 89, line4, 12, muted, "sans",
               limit=bx + bw - 14, label="rail line4 %d" % index)

    s.text(40, 648, T["foot"], 12, muted, "sans", limit=1060,
           label="footer")
    s.add("</svg>")
    if s.problems:
        raise SystemExit("FATAL: SVG layout problems:\n  "
                         + "\n  ".join(s.problems))
    return s.svg()


def draw_svg_gauge(s: Svg, cx, y, cents, P, half=32.0):
    """A 5-tick tolerance ruler: band in the middle, marker clamped at edges."""
    passed = abs(cents) <= 1
    ink = P["ok"] if passed else P["bad"]
    s.line(cx - half, y, cx + half, y, P["panel_border"], 1.2)
    s.rect(cx - 6, y - 4, 12, 8, 2, fill=P["ok_soft"], stroke=P["ok"] + "66",
           width=0.9)
    for offset in (-half, -half / 2, 0, half / 2, half):
        s.line(cx + offset, y - 2.8, cx + offset, y + 2.8,
               P["muted"], 0.9)
    if passed:
        mx = cx + (cents / 100.0) * 6
    else:
        mx = cx + (-1 if cents < 0 else 1) * (half - 4)
    s.circle(mx, y, 3.4, fill=ink)
    return passed


# ---------------------------------------------------------------------------
# quickstart capture, framed on the GitHub page backgrounds (kept neutral so
# the frame disappears into the page; content is the real run, not redrawn)
# ---------------------------------------------------------------------------
FRAME = {
    "light": dict(bg="#ffffff", border="#d0d7de", sub="#57606a"),
    "dark": dict(bg="#0d1117", border="#30363d", sub="#8b949e"),
}


def quickstart(skin: str) -> None:
    F = FRAME[skin]
    src = Image.open(os.path.join(OUT, "quickstart.png")).convert("RGB")
    img_w = 1000
    img_h = round(src.height * img_w / src.width)
    shot = src.resize((img_w, img_h), Image.LANCZOS)
    pad, cap_h = 40, 74
    w, h = img_w + pad * 2, img_h + cap_h + pad
    img = Image.new("RGB", (w, h), F["bg"])
    d = ImageDraw.Draw(img)
    d.text((pad, 30), "quickstart · synthetic sample · not customer data",
           font=fnt("sans", 22), fill=F["sub"])
    x, y = pad, cap_h
    img.paste(shot, (x, y))
    d.rounded_rectangle([x - 1, y - 1, x + img_w, y + img_h], radius=12,
                        outline=F["border"], width=2)
    img.save(os.path.join(OUT, "dsh-travel-recon-quickstart-%s.webp" % skin),
             "WEBP", quality=90)


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    written = []
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            image = draw_hero(lang, skin)
            path = os.path.join(
                OUT, "dsh-travel-recon-hero-%s-%s.webp" % (lang, skin))
            image.save(path, "WEBP", quality=90, method=6)
            written.append((os.path.basename(path), os.path.getsize(path)))
    for skin in ("light", "dark"):
        path = os.path.join(OUT, "dsh-travel-recon-flow-v5-%s.svg" % skin)
        content = flow_svg(skin)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        written.append((os.path.basename(path), os.path.getsize(path)))
    for skin in ("light", "dark"):
        quickstart(skin)
        name = "dsh-travel-recon-quickstart-%s.webp" % skin
        written.append((name, os.path.getsize(os.path.join(OUT, name))))
    for name, size in written:
        print("wrote %-46s %7d bytes" % (name, size))


if __name__ == "__main__":
    main()
