# -*- coding: utf-8 -*-
"""run_all.py —— 一键复现（在 examples/watch 目录下运行）

    python scripts/run_all.py

顺序：逐个页面脚本 → 合成连续背景长图 → 切回单页 → 页数校验
"""
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import json
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from cfg import CFG, ASSETS, OUT  # noqa: E402

PY = sys.executable

# 生成顺序（后跑的会覆盖同名输出，这是原流水线的设计）
ORDER = [
    "build_rules.py",
    "build_fill.py",
    "build_layout.py",
    "build_kv2.py",
    "build_fix_4_11.py",
    "build_merge.py",
    "build_scenes2.py",
    "build_extra.py",
    "build_approach.py",
]

# 长图页序（与定稿一致；透明页优先）
# 只写页名，扩展名自动挑（透明 png 优先，没有就用 jpg 并羽化）
LONG_ORDER = [
    "00-approach", "01-cover", "02-manifesto", "03-keyvisual",
    "04-material", "05-anatomy", "06-night", "07-spec",
    "08-profile", "09-variants", "10-scenes", "11-detail",
    "12-colophon", "13-night", "14-typography", "15-mono",
]


def run_scripts():
    for s in ORDER:
        p = os.path.join(HERE, s)
        if not os.path.exists(p):
            print(f"  跳过（不存在）{s}")
            continue
        r = subprocess.run([PY, p], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=HERE)
        tail = (r.stdout or r.stderr or "").strip().splitlines()
        print(f"  {s:<22} {'OK' if r.returncode == 0 else 'FAIL'}  {tail[-1] if tail else ''}")
        if r.returncode != 0:
            print((r.stderr or "")[-500:])
            return False
    return True


def build_long():
    """页面 → 连续背景长图 → 切回单页"""
    W, H = CFG["canvas"]["width"], CFG["canvas"]["height"]
    M = CFG["canvas"]["margin"]
    GAP = 20

    files = []
    for base in LONG_ORDER:
        png, jpg = base + ".png", base + ".jpg"
        if os.path.exists(os.path.join(OUT, png)):
            files.append((png, True))
        elif os.path.exists(os.path.join(OUT, jpg)):
            files.append((jpg, False))
    if not files:
        print("  没有可合成的页面"); return None

    # 用透明层叠（透明页）；不透明页羽化
    def feather(im, px=80):
        w, h = im.size
        m = Image.new("L", (w, h), 255)
        d = ImageDraw.Draw(m)
        for i in range(px):
            val = int(255 * i / px)
            d.line([(0, i), (w, i)], fill=val)
            d.line([(0, h - 1 - i), (w, h - 1 - i)], fill=val)
        im = im.copy(); im.putalpha(m)
        return im

    pages = []
    for f, transparent in files:
        im = Image.open(os.path.join(OUT, f)).convert("RGBA")
        if transparent:
            bb = im.getbbox()
            if bb:
                im = im.crop((0, bb[1], W, bb[3]))
        else:
            im = feather(im)   # 不透明页：上下羽化融入背景
        pages.append((f, im))

    total_h = sum(im.height for _, im in pages) + GAP * (len(pages) - 1)

    # 连续背景：纵向渐变 + 柔光带 + 侧向明暗 + 细噪点
    top = np.array([20, 15, 11], dtype=np.float32)
    bottom = np.array([14, 11, 8], dtype=np.float32)
    t = np.linspace(0, 1, total_h)[:, None]
    g = (top[None,None,:] * (1 - t[:,:,None]) + bottom[None,None,:] * t[:,:,None])
    g = np.repeat(g, W, axis=1)
    yy, xx = np.mgrid[0:total_h, 0:W].astype(np.float32)
    for k in range(0, total_h, 2600):
        band = np.exp(-(((yy) - (k + 900))**2) / (2 * (900**2))) * 10
        g = g + band[:, :, None]
    v = 0.82 + 0.24 * np.exp(-((np.linspace(0, 1, W)[None,:,None] - 0.5)**2) / (2 * 0.30**2))
    g = g * v
    rng = np.random.default_rng(5)
    g = g + rng.normal(0, 1.6, (total_h, W, 1))
    canvas = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")

    y = 0
    bounds = []
    for f, im in pages:
        canvas.paste(im, (0, y), im)
        bounds.append((f, y, y + im.height))
        y += im.height + GAP

    long_path = os.path.join(OUT, "长图.jpg")
    canvas.convert("RGB").save(long_path, quality=92, optimize=True, subsampling=0)

    # 网页版（高度必须 < 16384）
    ww = 760
    hh = int(canvas.height * ww / W)
    while hh >= 16000:
        ww = int(ww * 0.9); hh = int(canvas.height * ww / W)
    canvas.convert("RGB").resize((ww, hh), Image.LANCZOS).save(
        os.path.join(OUT, "长图-网页版.jpg"), quality=90, optimize=True)

    # 切回单页（保证单页与长图同源）
    for f, y0, y1 in bounds:
        canvas.crop((0, y0, W, y1)).convert("RGB").save(
            os.path.join(OUT, f.replace(".png", ".jpg")), quality=94, optimize=True)

    return canvas.size


def main():
    print("=" * 54)
    print(f"  {CFG.get('name', 'example')}")
    print(f"  素材 {ASSETS}")
    print(f"  输出 {OUT}")
    print("=" * 54)
    print("\n[1/2] 逐页生成")
    if not run_scripts():
        print("\n生成失败，停止")
        return 1
    print("\n[2/2] 合成连续背景长图")
    size = build_long()
    if not size:
        return 1

    expect = CFG.get("pages")
    got = len(LONG_ORDER)
    print(f"\n长图 {size[0]}×{size[1]}")
    print(f"页数 {got}" + (f"（配置写的 {expect}）" if expect else ""))
    if expect and got != expect:
        print("页数不一致 —— 检查 config.json 的 pages 或 LONG_ORDER")
        return 1
    print("\n完成。产物在 out/ 目录")
    return 0


if __name__ == "__main__":
    sys.exit(main())
