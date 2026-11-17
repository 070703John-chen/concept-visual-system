# -*- coding: utf-8 -*-
"""build_long.py —— 南枝的连续背景长图（与发布包定稿同构）

对应原始脚本 `_nz_render.py`：
  11 页（排除"附原版封面"）→ 连续米色背景（三段渐变 + 斜向柔光 + 颗粒）
  → 每页上下 90px 羽化 → 页间距 20 → 长图 1200×17800 → 切回单页

用法：
    python scripts/build_long.py
    python scripts/build_long.py --no-check
"""
import hashlib
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cfg import CFG, OUT  # noqa: E402

W = CFG["canvas"]["width"]
GAP = 20
FEATHER = 90

# 定稿 11 页（顺序即页序）；12-附原版封面 只用于单页展示，不进长图
PAGES = [
    "01-封面.jpg", "02-香调分析.jpg", "03-材料.jpg", "04-信息.jpg", "05-香型卡.jpg",
    "06-两种光.jpg", "07-冷调002.jpg", "08-冰晶.jpg", "09-灵感溯源.jpg", "10-自述.jpg",
    "11-封底.jpg",
]

SRC_DIR = os.path.join(OUT, "final")   # build_final.py 的输出目录


def feather_mask(w, h, px=FEATHER):
    m = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(m)
    for i in range(px):
        v = int(255 * i / px)
        d.line([(0, i), (w, i)], fill=v)
        d.line([(0, h - 1 - i), (w, h - 1 - i)], fill=v)
    return m


def build_bg(total_h):
    """三段米色渐变 + 斜向柔光 + 细颗粒（与 _nz_render.py 完全一致）"""
    top = np.array([244, 238, 226], dtype=np.float32)
    mid = np.array([236, 228, 213], dtype=np.float32)
    bot = np.array([214, 200, 178], dtype=np.float32)
    half = total_h // 2
    g = np.zeros((total_h, 3), dtype=np.float32)
    g[:half] = (top[None, :] * (1 - np.linspace(0, 1, half)[:, None]) +
                mid[None, :] * np.linspace(0, 1, half)[:, None])
    g[half:] = (mid[None, :] * (1 - np.linspace(0, 1, total_h - half)[:, None]) +
                bot[None, :] * np.linspace(0, 1, total_h - half)[:, None])
    bg = np.repeat(g[:, None, :], W, axis=1)

    yy, xx = np.mgrid[0:total_h, 0:W].astype(np.float32)
    for k in range(0, total_h, 3200):
        cy = k + 1600
        band = np.exp(-(((yy * 0.9 + xx * 0.35) - cy * 1.05) ** 2) / (2 * (1400 ** 2))) * 10
        bg = bg + band[:, :, None]

    rng = np.random.default_rng(11)
    bg = bg + rng.normal(0, 2.2, (total_h, W, 1))
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGB")


def main():
    check = "--no-check" not in sys.argv
    expect_pages = CFG.get("pages")
    expect_long = CFG.get("expected_long")

    print("=" * 54)
    print(f"  {CFG.get('name', 'nanzhi')} · 连续背景长图")
    print("=" * 54)

    print(f"\n[1/3] 读页面（{SRC_DIR}）")
    pages = []
    for f in PAGES:
        p = os.path.join(SRC_DIR, f)
        if not os.path.exists(p):
            raise FileNotFoundError(f"缺页面：{p}（先跑 build_final.py）")
        im = Image.open(p).convert("RGB")
        if im.width != W:
            im = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)
        pages.append((f, im))
        print(f"  {f:<18} {im.size[1]}")
    print(f"  共 {len(pages)} 页")

    total_h = sum(im.height for _, im in pages) + GAP * (len(pages) - 1)
    print(f"\n[2/3] 生成连续背景 {W}×{total_h}")
    canvas = build_bg(total_h)

    print("\n[3/3] 羽化贴页 + 切回单页")
    y = 0
    bounds = []
    for f, im in pages:
        canvas.paste(im, (0, y), feather_mask(W, im.height))
        bounds.append((f, y, y + im.height))
        y += im.height + GAP

    long_path = os.path.join(OUT, "长图-11页.jpg")
    canvas.save(long_path, quality=93, optimize=True, subsampling=0)
    print(f"  长图 {canvas.width}×{canvas.height}  {os.path.getsize(long_path)/1024/1024:.2f} MB")

    web_w = 760
    web_h = int(canvas.height * web_w / W)
    while web_h >= 16000:
        web_w = int(web_w * 0.9)
        web_h = int(canvas.height * web_w / W)
    canvas.resize((web_w, web_h), Image.LANCZOS).save(
        os.path.join(OUT, "长图-网页版.jpg"), quality=90, optimize=True)
    print(f"  网页版 {web_w}×{web_h}")

    man = {"project": CFG.get("name"), "pages": len(bounds),
           "long": f"{canvas.width}x{canvas.height}", "gap": GAP, "feather": FEATHER,
           "excluded": ["12-附原版封面.jpg"], "files": []}
    for f, y0, y1 in bounds:
        p = os.path.join(OUT, f)
        canvas.crop((0, y0, W, y1)).save(p, quality=94, optimize=True, subsampling=0)
        man["files"].append({"page": f, "h": y1 - y0, "bytes": os.path.getsize(p),
                             "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    ok = True
    if check and expect_pages and len(bounds) != expect_pages:
        print(f"  [FAIL] 页数 {len(bounds)} ≠ 基准 {expect_pages}"); ok = False
    if check and expect_long and [canvas.width, canvas.height] != list(expect_long):
        print(f"  [FAIL] 长图 {canvas.width}×{canvas.height} ≠ 基准 {expect_long}"); ok = False
    if check and ok:
        print(f"  [PASS] {len(bounds)} 页 · 长图 {canvas.width}×{canvas.height} 与基准一致")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
