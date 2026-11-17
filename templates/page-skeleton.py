# -*- coding: utf-8 -*-
"""page-skeleton.py —— 页面骨架（可跑，输出一张合规的空白版式页）

用途：新项目开工时先跑它，得到一张"边距/字号/栅格都对"的底页，
      再往上加内容。避免每页从零调坐标。

用法：
    python page-skeleton.py                # 输出 skeleton.png 到当前目录
    python page-skeleton.py -o out.jpg --dark
    python page-skeleton.py --title "雨后木质" --kicker "封面"

依赖：Pillow。字体默认找 Windows 的思源宋体，找不到会退回系统衬线体。
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("需要 Pillow：pip install pillow", file=sys.stderr)
    sys.exit(2)

W, H, M = 1200, 1600, 72          # 画布与安全边距（铁律：边距 72）
T1, T2, T3, T4 = 72, 26, 16, 12   # 四档字号（不许加第五档）

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_CANDIDATES = [
    os.path.join(_ROOT, "assets", "fonts", "NotoSerifSC-VF.ttf"),
    os.path.join(_ROOT, "assets", "fonts", "NotoSerifCJKsc-Regular.otf"),
    r"C:\Windows\Fonts\NotoSerifSC-VF.ttf",
    r"C:\Windows\Fonts\SourceHanSerifSC-Regular.otf",
    r"C:\Windows\Fonts\simsun.ttc",
    r"C:\Windows\Fonts\msyh.ttc",
]


FONT_PATH = None


def find_font(allow_fallback=False):
    """找到就用；找不到默认报错退出（静默降级会出一张字体全错的图，比报错更糟）"""
    global FONT_PATH
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            FONT_PATH = p
            return p
    if allow_fallback:
        print("[警告] 找不到中文字体，退回默认字体（中文会变方块）", file=sys.stderr)
        return None
    print("[错误] 找不到中文字体。查过这些路径：", file=sys.stderr)
    for p in FONT_CANDIDATES:
        print("   " + p, file=sys.stderr)
    print("\n处理：装一个（如 Noto Serif SC），或用 --allow-fallback 强行生成（中文会变方块）", file=sys.stderr)
    sys.exit(3)


def load_font(size, bold=False):
    if FONT_PATH is None:
        return ImageFont.load_default()
    try:
        f = ImageFont.truetype(FONT_PATH, size)
        if bold and hasattr(f, "set_variation_by_name"):
            try:
                f.set_variation_by_name("Bold")
            except Exception:
                pass
        return f
    except Exception:
        return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description="生成一张合规的空白页面骨架")
    ap.add_argument("-o", "--out", default="skeleton.png")
    ap.add_argument("--dark", action="store_true", help="暗底（默认亮底）")
    ap.add_argument("--title", default="标题", help="T1 标题示例文字")
    ap.add_argument("--kicker", default="KICKER", help="页眉右侧英文标签")
    ap.add_argument("--allow-fallback", action="store_true", help="找不到中文字体时用默认字体硬跑")
    args = ap.parse_args()

    find_font(args.allow_fallback)

    if args.dark:
        bg, ink, sub, gold, line = (14, 11, 8), (239, 227, 206), (138, 115, 88), (192, 138, 74), (74, 55, 34)
    else:
        bg, ink, sub, gold, line = (238, 230, 214), (34, 26, 18), (100, 82, 58), (152, 108, 58), (170, 144, 110)

    cv = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(cv)

    # 安全边距（虚线框，正式出图时删掉这段）
    for x in range(M, W - M, 12):
        d.line([(x, M), (x + 6, M)], fill=line, width=1)
        d.line([(x, H - M), (x + 6, H - M)], fill=line, width=1)
    for y in range(M, H - M, 12):
        d.line([(M, y), (M, y + 6)], fill=line, width=1)
        d.line([(W - M, y), (W - M, y + 6)], fill=line, width=1)

    # 页眉
    d.text((M, 46), "BRAND", font=load_font(16), fill=gold)
    tw = d.textlength(args.kicker, font=load_font(T4))
    d.text((W - M - tw, 50), args.kicker, font=load_font(T4), fill=sub)
    d.line([(M, 84), (W - M, 84)], fill=line, width=1)

    # 标题区
    d.text((M, 140), args.title, font=load_font(T1, bold=True), fill=ink)
    d.text((M, 240), "副标：一句依据（数字/对比/条件）", font=load_font(T2), fill=sub)
    d.line([(M, 300), (M + 470, 300)], fill=gold, width=2)

    # 正文示例（宽度 ≤ 480 的铁律）
    d.text((M, 340), "正文：部位 + 动词 + 结果 + 依据", font=load_font(T3), fill=ink)
    d.text((M, 368), "每行不超过 480 px，最多 3 行。", font=load_font(T3), fill=ink)
    d.text((M, 400), "注：依据行（做了什么、数据来源）", font=load_font(T4), fill=sub)

    # 内容占位框（1 主 + 2 副）
    box = (M, 470, W - M, 1100)
    d.rectangle(box, outline=line, width=1)
    d.text((box[0] + 12, box[1] + 10), "主内容区 1056 × 630", font=load_font(T4), fill=sub)

    y2 = 1120
    w2 = (W - 2 * M - 16) // 2
    for i in range(2):
        b = (M + i * (w2 + 16), y2, M + i * (w2 + 16) + w2, y2 + 300)
        d.rectangle(b, outline=line, width=1)
        d.text((b[0] + 10, b[1] + 8), f"副区 {i+1} · {w2} × 300", font=load_font(T4), fill=sub)

    # 页脚
    d.text((M, H - 56), "品牌 · 自命题方案", font=load_font(T4), fill=sub)
    pg = "01"
    d.text((W - M - d.textlength(pg, font=load_font(13)), H - 56), pg, font=load_font(13), fill=sub)

    cv.save(args.out)
    print(f"已生成 {args.out}  {W}×{H}  边距 {M}  字号 {T1}/{T2}/{T3}/{T4}")
    print("提示：正式出图时删掉边距虚线框那一段代码")


if __name__ == "__main__":
    main()
