# -*- coding: utf-8 -*-
"""reproduce.py —— 确定的复现验收：重跑 → 与 reference/ 逐页比对 → PASS / FAIL

用法：
    python scripts/reproduce.py --case watch
    python scripts/reproduce.py --case nanzhi
    python scripts/reproduce.py --case watch --no-run     # 只比对（用已生成的 out/）
    python scripts/reproduce.py --case watch --tolerance 8

判定标准（三条全过才 PASS）：
    1. 页数一致
    2. 每页高度一致（像素级高度必须相同 —— 版式一变就会差几十像素）
    3. 每页平均像素差 ≤ tolerance（默认 6；JPEG 重编码本身约 0.5–4）

说明：
    reference/ 里放的是发布包里的定稿成品（17 页 + 长图 / 11 页 + 长图），
    它是"效果标尺"，不是"可以随脚本一起改的东西"。
    改脚本后如果 FAIL，先看是哪一页，别急着调 tolerance。
"""
import argparse
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

CASES = {
    "watch": {
        "dir": os.path.join(ROOT, "examples", "watch"),
        "pages": ["00-cover", "01-hero", "02-feature", "03-hero", "04-grid", "05-spec",
                  "06-hero", "07-spec", "08-feature", "09-spec", "10-grid", "11-feature",
                  "12-brand", "13-hero", "14-doc", "15-mono", "17-doc"],
        "long": "长图-17页.jpg",
        "run": [["scripts/run_all.py"]],
    },
    "nanzhi": {
        "dir": os.path.join(ROOT, "examples", "nanzhi"),
        "pages": ["01-封面", "02-香调分析", "03-材料", "04-信息", "05-香型卡",
                  "06-两种光", "07-冷调002", "08-冰晶", "09-灵感溯源", "10-自述", "11-封底"],
        "long": "长图-11页.jpg",
        "run": [["scripts/build_pages.py"], ["scripts/build_final.py"], ["scripts/build_long.py"]],
    },
}


def run_case(case):
    print(f"[1/2] 重跑 {case} ……")
    for cmd in CASES[case]["run"]:
        script = os.path.join(CASES[case]["dir"], cmd[0])
        if not os.path.exists(script):
            print(f"  缺脚本 {script}")
            return False
        r = subprocess.run([PY, script] + cmd[1:], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=CASES[case]["dir"])
        tail = (r.stdout or r.stderr or "").strip().splitlines()
        print(f"  {cmd[0]:<28} {'OK' if r.returncode == 0 else 'FAIL'}  {tail[-1] if tail else ''}")
        if r.returncode != 0:
            print((r.stderr or "")[-600:])
            return False
    return True


def compare(case, tolerance):
    c = CASES[case]
    out_dir = os.path.join(c["dir"], "out")
    ref_dir = os.path.join(c["dir"], "reference")
    if not os.path.isdir(ref_dir):
        print(f"  缺基准目录 {ref_dir}")
        return False

    print(f"\n[2/2] 与 reference 比对（容差 {tolerance}）")
    print(f"  {'页':<14}{'我们h':>7}{'基准h':>7}{'像素差':>9}  ")
    fails = []
    for name in c["pages"]:
        a_p = os.path.join(out_dir, name + ".jpg")
        b_p = os.path.join(ref_dir, name + ".jpg")
        if not (os.path.exists(a_p) and os.path.exists(b_p)):
            print(f"  {name:<14}{'缺文件':>23}")
            fails.append((name, "缺文件")); continue
        a, b = Image.open(a_p), Image.open(b_p)
        if a.size != b.size:
            print(f"  {name:<14}{a.height:>7}{b.height:>7}{'尺寸不同':>9}")
            fails.append((name, f"{a.size}≠{b.size}")); continue
        aa = np.asarray(a.convert("RGB")).astype(np.int16)
        bb = np.asarray(b.convert("RGB")).astype(np.int16)
        d = float(np.abs(aa - bb).mean())
        mark = "OK" if d <= tolerance else "DIFF"
        print(f"  {name:<14}{a.height:>7}{b.height:>7}{d:>9.2f}  {mark}")
        if d > tolerance:
            fails.append((name, f"diff {d:.2f} > {tolerance}"))

    # 长图
    la = os.path.join(out_dir, c["long"])
    lb = os.path.join(ref_dir, "长图.jpg")
    if os.path.exists(la) and os.path.exists(lb):
        sa, sb = Image.open(la).size, Image.open(lb).size
        same = sa == sb
        print(f"  {'长图':<14}{sa[1]:>7}{sb[1]:>7}   {sa} vs {sb}  {'OK' if same else 'DIFF'}")
        if not same:
            fails.append(("长图", f"{sa}≠{sb}"))
    else:
        print("  长图缺失"); fails.append(("长图", "缺文件"))

    print("\n" + "-" * 54)
    if fails:
        print(f"  FAIL：{len(fails)} 项不符")
        for n, why in fails[:10]:
            print(f"    · {n}: {why}")
        return False
    print(f"  PASS：{len(c['pages'])} 页 + 长图 与定稿基准一致")
    return True


def main():
    ap = argparse.ArgumentParser(description="复现验收：重跑并与定稿基准比对")
    ap.add_argument("--case", choices=list(CASES), required=True)
    ap.add_argument("--tolerance", type=float, default=6.0, help="每页平均像素差上限（默认 6）")
    ap.add_argument("--no-run", action="store_true", help="不重跑，只比对现有 out/")
    args = ap.parse_args()

    print("=" * 54)
    print(f"  复现验收 · {args.case}")
    print("=" * 54)
    if not args.no_run and not run_case(args.case):
        print("\n重跑失败，停止")
        return 1
    return 0 if compare(args.case, args.tolerance) else 1


if __name__ == "__main__":
    sys.exit(main())
