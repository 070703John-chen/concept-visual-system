# -*- coding: utf-8 -*-
"""统一调色：把一批产品图拉到同一个"棚拍光"

用法：
    python grade.py <输入目录> [-o 输出目录] [--warm 1.06,1.01,0.90] [--cool 0.93,0.98,1.10]

默认参数来自实践：
    黑位 0.03 / 高光 0.97 / 左上主光 / 暗角 22% / 锐化 48%
"""
import os
import sys
import argparse
import numpy as np
from PIL import Image, ImageFilter


def grade(im, warm=(1.06, 1.01, 0.90), cool=(0.93, 0.98, 1.10),
          light_strength=1.0, vignette=0.22, sharpen=48):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    h, w, _ = a.shape

    # 1) 统一反差：黑位 0.03，高光 0.97
    a = np.clip((a - 0.03) / (0.97 - 0.03), 0, 1)
    a = a ** 0.96

    # 2) 冷暖分离：高光加暖，暗部加冷
    lum = a.mean(axis=2, keepdims=True)
    t = np.clip((lum - 0.35) / 0.45, 0, 1)
    a = a * (np.array(cool) * (1 - t) + np.array(warm) * t)

    # 3) 模拟左上主光
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    gx = (xx / w - 0.28)
    gy = (yy / h - 0.22)
    light = 1.0 - 0.16 * np.clip(np.sqrt(gx * gx + gy * gy) * 1.25, 0, 1) ** 1.4
    a = a * light[:, :, None] ** light_strength

    # 4) 统一暗角
    dx = (xx - w / 2) / (w / 2)
    dy = (yy - h / 2) / (h / 2)
    r = np.sqrt(dx * dx * 0.8 + dy * dy)
    a = a * (1.0 - vignette * np.clip(r - 0.55, 0, 1.4) ** 1.5)[:, :, None]

    # 5) 锐化 + 细噪点
    img = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    img = img.filter(ImageFilter.UnsharpMask(radius=1.4, percent=sharpen, threshold=2))
    b = np.asarray(img).astype(np.float32)
    rng = np.random.default_rng(3)
    b = b + rng.normal(0, 1.4, (h, w, 1))
    return Image.fromarray(np.clip(b, 0, 255).astype(np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--warm", default="1.06,1.01,0.90")
    ap.add_argument("--cool", default="0.93,0.98,1.10")
    args = ap.parse_args()

    out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.src)), "graded")
    os.makedirs(out, exist_ok=True)
    warm = tuple(float(x) for x in args.warm.split(","))
    cool = tuple(float(x) for x in args.cool.split(","))

    n = 0
    for f in sorted(os.listdir(args.src)):
        if not f.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        p = os.path.join(args.src, f)
        try:
            im = Image.open(p).convert("RGB")
        except Exception as e:
            print("skip", f, type(e).__name__)
            continue
        grade(im, warm, cool).save(os.path.join(out, f), quality=94, optimize=True)
        n += 1
    print(f"graded {n} → {out}")


if __name__ == "__main__":
    main()
