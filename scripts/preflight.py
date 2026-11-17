# -*- coding: utf-8 -*-
"""preflight.py —— 开工前自检（一条命令，缺什么直接说）

用法：
    python preflight.py                 # 检查当前目录能否作为输出目录
    python preflight.py --out-dir D:\\项目\\out
    python preflight.py --quiet         # 只报问题，不报通过项

检查项：Python 版本 / Pillow / numpy / 中文字体 / 输出目录可写 / 磁盘剩余
退出码：0 = 全部通过；1 = 有阻断项（必须修）；2 = 参数错误
"""
import argparse
import os
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

OK, WARN, FAIL = "[OK]  ", "[WARN]", "[FAIL]"

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\NotoSerifSC-VF.ttf",
    r"C:\Windows\Fonts\SourceHanSerifSC-Regular.otf",
    r"C:\Windows\Fonts\simsun.ttc",
    r"C:\Windows\Fonts\msyh.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc",
]


def check_python(problems):
    v = sys.version_info
    if v >= (3, 9):
        return f"{OK} Python {v.major}.{v.minor}.{v.micro}"
    problems.append("Python 版本过低，需要 3.9+")
    return f"{FAIL} Python {v.major}.{v.minor}（需要 3.9+）"


def check_libs(problems):
    out = []
    try:
        import PIL
        out.append(f"{OK} Pillow {PIL.__version__}")
    except Exception as e:
        problems.append(f"缺 Pillow（{type(e).__name__}）→ pip install pillow")
        out.append(f"{FAIL} Pillow 未安装")
    try:
        import numpy
        out.append(f"{OK} numpy {numpy.__version__}")
    except Exception as e:
        problems.append(f"缺 numpy（{type(e).__name__}）→ pip install numpy")
        out.append(f"{FAIL} numpy 未安装")
    return out


def check_fonts(problems):
    found = [p for p in FONT_CANDIDATES if os.path.exists(p)]
    if found:
        return [f"{OK} 字体：{os.path.basename(found[0])}"] + \
               [f"      备选：{os.path.basename(p)}" for p in found[1:4]]
    problems.append("找不到中文字体 → 页面会全部变成方块/默认字体")
    return [f"{FAIL} 找不到任何候选中文字体（共查了 {len(FONT_CANDIDATES)} 个路径）"]


def check_outdir(path, problems):
    try:
        os.makedirs(path, exist_ok=True)
        probe = os.path.join(path, ".preflight_probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
    except Exception as e:
        problems.append(f"输出目录不可写：{path}（{type(e).__name__}）")
        return [f"{FAIL} 输出目录不可写：{path}"]
    free_gb = shutil.disk_usage(path).free / (1024 ** 3)
    lines = [f"{OK} 输出目录可写：{path}"]
    if free_gb < 2:
        problems.append(f"磁盘剩余 {free_gb:.1f} GB，长图可能写到一半失败")
        lines.append(f"{WARN} 磁盘剩余 {free_gb:.1f} GB（长图建议 ≥ 2 GB）")
    else:
        lines.append(f"{OK} 磁盘剩余 {free_gb:.1f} GB")
    return lines


def main():
    ap = argparse.ArgumentParser(description="视觉系统开工前自检")
    ap.add_argument("--out-dir", default=os.getcwd(), help="输出目录（默认当前目录）")
    ap.add_argument("--quiet", action="store_true", help="只报问题")
    args = ap.parse_args()

    problems = []
    blocks = []
    blocks.append(("运行环境", [check_python(problems)]))
    blocks.append(("依赖库", check_libs(problems)))
    blocks.append(("中文字体", check_fonts(problems)))
    blocks.append(("输出与磁盘", check_outdir(args.out_dir, problems)))

    print("=" * 54)
    print("  视觉系统 · 开工前自检")
    print("=" * 54)
    for title, lines in blocks:
        shown = lines if not args.quiet else [l for l in lines if l.startswith(FAIL) or l.startswith(WARN)]
        if not shown:
            continue
        print(f"\n{title}")
        for l in shown:
            print("  " + l)

    print("\n" + "-" * 54)
    if problems:
        print(f"阻断 {len(problems)} 项，先修再开工：")
        for p in problems:
            print("  · " + p)
        return 1
    print("全部通过，可以开工。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
