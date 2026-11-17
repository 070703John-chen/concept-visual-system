# -*- coding: utf-8 -*-
"""连续背景长图合成器

输入：一批「透明 PNG 页面」（RGBA，画布 1200×1600，背景透明）
输出：连续背景长图 + 切回的单页 jpg + 网页版

用法：
    python compose_long.py <页面目录> [--width 1200] [--gap 20] [--web 760]

页面命名建议：01-xxx.png / 02-xxx.png …（按文件名排序）
不透明 jpg 也能放，会走"边缘羽化 60px"分支。
"""
import os
import sys
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def feather(im, px=60):
    """给不透明图加边缘羽化，让它融进连续背景"""
    w, h = im.size
    m = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(m)
    for i in range(px):
        v = int(255 * i / px)
        d.line([(0, i), (w, i)], fill=v)
        d.line([(0, h - 1 - i), (w, h - 1 - i)], fill=v)
    im = im.convert("RGBA")
    im.putalpha(m)
    return im


def build_background(w, total_h, bands=None, seed=5):
    """纵向渐变 + 柔光带 + 侧向明暗 + 细噪点"""
    y = np.linspace(0, 1, total_h)
    base = np.stack([
        20 + 12 * np.sin(y * np.pi * 1.2),
        15 + 9 * np.sin(y * np.pi * 1.2 + 0.2),
        11 + 6 * np.sin(y * np.pi * 1.2 + 0.4),
    ], axis=1)
    a = base[:, None, :].repeat(w, axis=1)

    bands = bands or [(0.05, 0.05, 1.0, (58, 33, 17)),
                      (0.32, 0.06, 0.75, (46, 25, 12)),
                      (0.60, 0.06, 0.80, (50, 28, 13)),
                      (0.82, 0.05, 0.75, (46, 26, 12))]
    yy = np.arange(total_h)[:, None]
    for cf, sp, st, col in bands:
        g = np.exp(-((yy - total_h * cf) ** 2) / (2 * (total_h * sp) ** 2))
        a = a + g[:, :, None] * np.array(col) * st

    x = np.linspace(0, 1, w)[None, :, None]
    a = a * (0.82 + 0.24 * np.exp(-((x - 0.5) ** 2) / (2 * 0.30 ** 2)))

    rng = np.random.default_rng(seed)
    a = a + rng.normal(0, 1.8, (total_h, w, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--width", type=int, default=1200)
    ap.add_argument("--gap", type=int, default=20)
    ap.add_argument("--web", type=int, default=760, help="网页版宽度（高度需 <16384）")
    args = ap.parse_args()

    out = args.out or args.src
    W = args.width
    files = sorted([f for f in os.listdir(args.src)
                    if f.lower().endswith((".png", ".jpg", ".jpeg"))])
    if not files:
        print("没有图片")
        return

    pages = []
    for f in files:
        im = Image.open(os.path.join(args.src, f)).convert("RGBA")
        if im.width != W:
            im = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)
        if f.lower().endswith(".png"):
            bb = im.getbbox()
            if bb:
                im = im.crop((0, bb[1], W, bb[3]))
        else:
            im = feather(im)
        pages.append((f, im))
        print(f, im.height)

    total_h = sum(im.height for _, im in pages) + args.gap * (len(pages) - 1)
    bg = build_background(W, total_h)
    print("背景", bg.size)

    canvas = bg.copy()
    y = 0
    bounds = []
    for f, im in pages:
        canvas.paste(im, (0, y), im)
        bounds.append((f, y, y + im.height))
        y += im.height + args.gap

    long_path = os.path.join(out, "长图.jpg")
    canvas.save(long_path, quality=92, optimize=True, subsampling=0)
    print("长图", canvas.size, round(os.path.getsize(long_path) / 1024 / 1024, 1), "MB")

    # 切回单页
    for f, y0, y1 in bounds:
        name = os.path.splitext(f)[0] + ".jpg"
        canvas.crop((0, y0, W, y1)).save(os.path.join(out, name),
                                         quality=94, optimize=True, subsampling=0)

    # 网页版（确保高度 < 16384）
    web_w = args.web
    web_h = int(canvas.height * web_w / W)
    while web_h >= 16000:
        web_w = int(web_w * 0.9)
        web_h = int(canvas.height * web_w / W)
    canvas.resize((web_w, web_h), Image.LANCZOS).save(
        os.path.join(out, "长图-网页版.jpg"), quality=90, optimize=True)
    print("网页版", web_w, "×", web_h)


if __name__ == "__main__":
    main()
