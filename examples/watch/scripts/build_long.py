# -*- coding: utf-8 -*-
"""build_long.py —— 合成定稿级长图（与发布包里的定稿逐像素同构）

对应原始脚本 `_final5.py`：
  17 页 → 连续背景（纵向渐变 + 四道柔光带 + 侧向明暗 + 噪点 + 0.6px 模糊）
        → 页间距 20px → 长图 1200×25438 → 切回 17 张单页 → manifest（含 SHA-256）

与定稿的对应关系（页名映射）：
  00-cover   ← out/00-cover.png        （作品集封面，透明）
  01-hero    ← 01-cover.png
  02-feature ← 02-manifesto.png
  03-hero    ← 03-keyvisual.png
  04-grid    ← 04-material.png
  05-spec    ← 05-anatomy.png
  06-hero    ← 06-night.png
  07-spec    ← 07-spec.png
  08-feature ← 08-profile.png
  09-spec    ← 09-variants.png
  10-grid    ← 10-scenes.png
  11-feature ← assets/11-detail.jpg    （不透明照片页，上下各 60px 羽化）
  12-brand   ← 12-colophon.png
  13-hero    ← 13-night.png
  14-doc     ← 14-typography.png
  15-mono    ← 15-mono.png
  17-doc     ← 00-approach.png         （设计思路放最后）

用法：
    python scripts/build_long.py            # 合成 + 校验
    python scripts/build_long.py --no-check  # 跳过高度校验
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
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cfg import CFG, ASSETS, OUT  # noqa: E402

W = CFG["canvas"]["width"]
GAP = 20

# (输出页名, 源文件, 是否透明层)
# 模式：alpha = 透明层（按 bbox 裁边）；feather = 不透明页（上下 60px 羽化）；
#       opaque = 整幅铺满（不裁不羽化）—— 08/12 在定稿里是这种
ORDER = [
    ("00-cover",   "00-cover.png",        "alpha"),
    ("01-hero",    "01-cover.png",        "alpha"),
    ("02-feature", "02-manifesto.png",    "alpha"),
    ("03-hero",    "03-keyvisual.png",    "alpha"),
    ("04-grid",    "04-material.png",     "alpha"),
    ("05-spec",    "05-anatomy.png",      "alpha"),
    ("06-hero",    "06-night.png",        "alpha"),
    ("07-spec",    "07-spec.png",         "alpha"),
    ("08-feature", "08-profile.jpg",      "opaque"),
    ("09-spec",    "09-variants.png",     "alpha"),
    ("10-grid",    "10-scenes.png",       "alpha"),
    ("11-feature", "__ASSETS__/11-detail.jpg", "feather"),
    ("12-brand",   "12-colophon.jpg",     "opaque"),
    ("13-hero",    "13-night.png",        "alpha"),
    ("14-doc",     "14-typography.png",   "alpha"),
    ("15-mono",    "15-mono.png",         "alpha"),
    ("17-doc",     "00-approach.png",     "alpha"),
]


def resolve(src):
    if src.startswith("__ASSETS__/"):
        return os.path.join(ASSETS, src.split("/", 1)[1])
    return os.path.join(OUT, src)


def feather(im, px=60):
    """不透明页：上下各 px 像素线性羽化，融入连续背景"""
    m = Image.new("L", (W, im.height), 255)
    md = ImageDraw.Draw(m)
    for i in range(px):
        v = int(255 * i / px)
        md.line([(0, i), (W, i)], fill=v)
        md.line([(0, im.height - 1 - i), (W, im.height - 1 - i)], fill=v)
    im = im.copy()
    im.putalpha(m)
    return im


def load_pages():
    contents = []
    for name, src, mode in ORDER:
        p = resolve(src)
        if not os.path.exists(p):
            raise FileNotFoundError(f"缺源文件：{p}（页 {name}）")
        im = Image.open(p).convert("RGBA")
        if mode == "alpha":
            bb = im.getbbox()
            if bb:
                im = im.crop((0, bb[1], W, bb[3]))
        elif mode == "feather":
            im = feather(im)
        # opaque：保持整幅，不裁不羽化
        contents.append((name, im))
        print(f"  {name:<11} 高 {im.height}")
    return contents


def build_bg(total_h):
    """与 _final5.py 完全一致的背景算法"""
    y = np.linspace(0, 1, total_h)
    base = np.stack([20 + 12 * np.sin(y * np.pi * 1.2),
                     15 + 9 * np.sin(y * np.pi * 1.2 + 0.2),
                     11 + 6 * np.sin(y * np.pi * 1.2 + 0.4)], axis=1)
    a = base[:, None, :].repeat(W, axis=1)

    def band(cf, sp, st, col):
        yy = np.arange(total_h)[:, None]
        g = np.exp(-((yy - total_h * cf) ** 2) / (2 * (total_h * sp) ** 2))
        return g[:, :, None] * np.array(col) * st

    for cf, sp, st, col in [(0.05, 0.05, 1.00, (58, 33, 17)),
                            (0.32, 0.06, 0.75, (46, 25, 12)),
                            (0.60, 0.06, 0.80, (50, 28, 13)),
                            (0.82, 0.05, 0.75, (46, 26, 12))]:
        a = a + band(cf, sp, st, col)

    x = np.linspace(0, 1, W)[None, :, None]
    a = a * (0.82 + 0.24 * np.exp(-((x - 0.5) ** 2) / (2 * 0.30 ** 2)))
    rng = np.random.default_rng(5)
    a = a + rng.normal(0, 1.8, (total_h, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(0.6))


def main():
    check = "--no-check" not in sys.argv
    expect_pages = CFG.get("pages")
    expect_long = CFG.get("expected_long")   # [w, h]

    print("=" * 54)
    print(f"  {CFG.get('name', 'example')} · 合成定稿级长图")
    print("=" * 54)
    print("\n[1/4] 取页面并裁透明边")
    contents = load_pages()

    print("\n[2/4] 生成连续背景")
    total_h = sum(im.height for _, im in contents) + GAP * (len(contents) - 1)
    bg = build_bg(total_h)

    print("\n[3/4] 逐页贴上并切片")
    out = bg.copy()
    yy = 0
    bounds = []
    for name, im in contents:
        out.paste(im, (0, yy), im)
        bounds.append((name, yy, yy + im.height))
        yy += im.height + GAP

    long_path = os.path.join(OUT, "长图-17页.jpg")
    out.save(long_path, quality=92, optimize=True, subsampling=0)
    print(f"  长图 {out.width}×{out.height}  {os.path.getsize(long_path)/1024/1024:.2f} MB")

    web = out.resize((760, int(out.height * 760 / W)), Image.LANCZOS)
    web.save(os.path.join(OUT, "长图-网页版.jpg"), quality=90, optimize=True)

    print("\n[4/4] 切回单页 + manifest")
    man = {"project": CFG.get("name"), "pages": len(bounds),
           "long": f"{out.width}x{out.height}", "gap": GAP, "files": []}
    for name, y0, y1 in bounds:
        p = os.path.join(OUT, name + ".jpg")
        out.crop((0, y0, W, y1)).save(p, quality=94, optimize=True, subsampling=0)
        man["files"].append({"page": name, "file": name + ".jpg", "h": y1 - y0,
                             "bytes": os.path.getsize(p),
                             "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()})
    json.dump(man, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---- 校验 ----
    ok = True
    if check and expect_pages and len(bounds) != expect_pages:
        print(f"  [FAIL] 页数 {len(bounds)} ≠ 配置 {expect_pages}")
        ok = False
    if check and expect_long and list(expect_long) != [out.width, out.height]:
        print(f"  [FAIL] 长图 {out.width}×{out.height} ≠ 基准 {expect_long[0]}×{expect_long[1]}")
        ok = False
    if check and ok:
        print(f"  [PASS] {len(bounds)} 页 · 长图 {out.width}×{out.height} 与基准一致")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
