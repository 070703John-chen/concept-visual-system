# -*- coding: utf-8 -*-
"""bootstrap_fonts.py —— 字体引导：找得到就用，找不到按固定来源下载并校验

为什么需要它：
    页面脚本里写死 `C:\\Windows\\Fonts\\NotoSerifSC-VF.ttf` 是机器指纹，
    换一台没有思源宋体的机器，出来的字全是方块。

解析顺序（与 kit.py / page-skeleton.py 一致）：
    1. 环境变量 CVS_FONT 指定的路径
    2. <repo>/assets/fonts/ 下的 *.otf / *.ttf / *.ttc（按文件名优先级）
    3. 系统常见路径（Windows / macOS / Linux）
    4. 都没有 → 用本脚本下载到 assets/fonts/（--allow-download）

用法：
    python scripts/bootstrap_fonts.py                  # 只检查，报告找到了什么
    python scripts/bootstrap_fonts.py --allow-download  # 缺失时下载思源宋体
    python scripts/bootstrap_fonts.py --print-sha256    # 打印已装字体的 SHA-256（用于钉版本）

钉版本：
    下载默认校验 SIZE_MIN..SIZE_MAX 区间；拿到 SHA-256 后可写进
    assets/fonts/SHA256SUMS，之后下载会自动比对。
"""
import argparse
import hashlib
import os
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

# 思源宋体（Noto Serif CJK SC）官方仓库
FONT_URL = ("https://github.com/notofonts/noto-cjk/raw/main/Serif/OTF/"
            "SimplifiedChinese/NotoSerifCJKsc-Regular.otf")
FONT_NAME = "NotoSerifCJKsc-Regular.otf"
SIZE_MIN = 15 * 1024 * 1024      # 15 MB —— 明显偏小说明下到的是 HTML 错误页
SIZE_MAX = 40 * 1024 * 1024

PREFER = ["NotoSerifSC-VF.ttf", "NotoSerifCJKsc-Regular.otf", "SourceHanSerifSC-Regular.otf",
          "SourceHanSerifSC-Regular.ttf", "songti.ttc", "simsun.ttc", "msyh.ttc"]

SYSTEM_PATHS = [
    r"C:\Windows\Fonts\NotoSerifSC-VF.ttf",
    r"C:\Windows\Fonts\NotoSerifCJKsc-Regular.otf",
    r"C:\Windows\Fonts\SourceHanSerifSC-Regular.otf",
    r"C:\Windows\Fonts\simsun.ttc",
    r"C:\Windows\Fonts\msyh.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/Library/Fonts/Songti.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc",
]


def find_local():
    """返回 (path, 来源说明) 或 (None, None)"""
    env = os.environ.get("CVS_FONT")
    if env and os.path.exists(env):
        return env, "环境变量 CVS_FONT"

    if os.path.isdir(FONT_DIR):
        files = [f for f in os.listdir(FONT_DIR) if f.lower().endswith((".otf", ".ttf", ".ttc"))]
        if files:
            files.sort(key=lambda f: (PREFER.index(f) if f in PREFER else 99, f))
            return os.path.join(FONT_DIR, files[0]), "仓库 assets/fonts/"

    for p in SYSTEM_PATHS:
        if os.path.exists(p):
            return p, "系统字体"
    return None, None


def sha256_of(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def expected_sha():
    p = os.path.join(FONT_DIR, "SHA256SUMS")
    if not os.path.exists(p):
        return None
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[-1].endswith((".otf", ".ttf", ".ttc")):
            return parts[0].lower()
    return None


def download():
    from urllib.request import Request, urlopen
    os.makedirs(FONT_DIR, exist_ok=True)
    dst = os.path.join(FONT_DIR, FONT_NAME)
    print(f"  下载 {FONT_URL}")
    req = Request(FONT_URL, headers={"User-Agent": "concept-visual-system/bootstrap_fonts"})
    with urlopen(req, timeout=300) as r, open(dst, "wb") as f:
        shutil.copyfileobj(r, f)
    size = os.path.getsize(dst)
    print(f"  已下载 {size/1024/1024:.1f} MB → {dst}")
    if not (SIZE_MIN <= size <= SIZE_MAX):
        print(f"  [FAIL] 大小异常（{size} 字节），可能下到的是错误页，请检查网络/URL")
        return None

    exp = expected_sha()
    got = sha256_of(dst)
    if exp:
        if exp == got:
            print(f"  [OK] SHA-256 与 SHA256SUMS 一致")
        else:
            print(f"  [FAIL] SHA-256 不符\n    期望 {exp}\n    实际 {got}")
            return None
    else:
        print(f"  SHA-256 = {got}")
        print(f"  提示：把这个值写进 assets/fonts/SHA256SUMS 即可钉版本")
    return dst


def main():
    ap = argparse.ArgumentParser(description="字体引导与校验")
    ap.add_argument("--allow-download", action="store_true", help="缺失时下载思源宋体")
    ap.add_argument("--print-sha256", action="store_true", help="打印当前字体的 SHA-256")
    args = ap.parse_args()

    print("=" * 54)
    print("  中文字体引导")
    print("=" * 54)

    path, src = find_local()
    if path:
        print(f"  [OK] {path}")
        print(f"       来源：{src}")
        if args.print_sha256:
            print(f"       SHA-256 = {sha256_of(path)}")
        return 0

    print("  [FAIL] 没找到任何中文字体")
    if not args.allow_download:
        print("\n  处理：")
        print("    a) 装一个思源宋体，然后重跑本脚本")
        print("    b) python scripts/bootstrap_fonts.py --allow-download")
        return 1

    got = download()
    if not got:
        return 1
    print(f"\n  [OK] 字体就绪：{got}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
