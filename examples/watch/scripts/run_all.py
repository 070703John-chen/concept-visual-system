# -*- coding: utf-8 -*-
"""run_all.py —— 一键复现定稿（在 examples/watch 目录下运行）

    python scripts/run_all.py

链路（缺一步就对不上定稿）：
    ① 页面脚本        → out/*.jpg（不透明）
    ② alpha_pages.py  → out/*.png（透明层）
    ③ build_cover_book → out/00-cover.png（作品集封面）
    ④ build_extra / build_approach → 14/15/00
    ⑤ build_long.py   → 长图 1200×25438 + 切回 17 页 + manifest

验收：页数 17、长图 1200×25438 与 config.json 的 expected_long 一致，否则失败退出。
"""
import json
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from cfg import CFG, ASSETS, OUT  # noqa: E402

PY = sys.executable

# ① 不透明页面（顺序有讲究：后跑的覆盖同名输出）
PAGE_SCRIPTS = [
    "build_rules.py",
    "build_fill.py",
    "build_layout.py",
    "build_kv2.py",
    "build_fix_4_11.py",
    "build_merge.py",
    "build_scenes2.py",
]

# ② 本身就是透明 PNG 的页
PNG_SCRIPTS = ["build_extra.py", "build_approach.py", "build_cover_book.py"]


def run(script):
    p = os.path.join(HERE, script)
    if not os.path.exists(p):
        print(f"  {script:<22} 跳过（不存在）")
        return True
    r = subprocess.run([PY, p], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=HERE)
    tail = (r.stdout or r.stderr or "").strip().splitlines()
    print(f"  {script:<22} {'OK' if r.returncode == 0 else 'FAIL'}  {tail[-1] if tail else ''}")
    if r.returncode != 0:
        print((r.stderr or "")[-600:])
        return False
    return True


def main():
    expect_pages = CFG.get("pages")
    expect_long = CFG.get("expected_long")

    print("=" * 58)
    print(f"  {CFG.get('name', 'example')}")
    print(f"  素材 {ASSETS}")
    print(f"  输出 {OUT}")
    print(f"  基准 {expect_pages} 页 / 长图 {expect_long}")
    print("=" * 58)

    print("\n[1/3] 不透明页面")
    for s in PAGE_SCRIPTS:
        if not run(s):
            return 1

    print("\n[2/3] 透明化 + 专属页")
    if not run("alpha_pages.py"):
        return 1
    for s in PNG_SCRIPTS:
        if not run(s):
            return 1

    print("\n[3/3] 合成定稿级长图")
    if not run("build_long.py"):
        return 1

    # ---- 二次校验（不信任中间脚本的自述，直接量产物）----
    from PIL import Image
    long_path = os.path.join(OUT, "长图-17页.jpg")
    man_path = os.path.join(OUT, "manifest.json")
    if not os.path.exists(long_path):
        print("  [FAIL] 没生成长图"); return 1
    w, h = Image.open(long_path).size
    man = json.load(open(man_path, encoding="utf-8"))
    print("\n" + "-" * 58)
    print(f"  长图   {w}×{h}")
    print(f"  页数   {man['pages']}")
    ok = True
    if expect_long and [w, h] != list(expect_long):
        print(f"  [FAIL] 长图尺寸与基准 {expect_long} 不符"); ok = False
    if expect_pages and man["pages"] != expect_pages:
        print(f"  [FAIL] 页数与基准 {expect_pages} 不符"); ok = False
    if ok:
        print(f"  [PASS] 与定稿基准一致")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
