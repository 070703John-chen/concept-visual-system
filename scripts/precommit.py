# -*- coding: utf-8 -*-
"""precommit.py —— 提交前闸门：五项校验全过才允许提交

用法（手动）：
    python scripts/precommit.py

安装为 git 钩子（一次即可）：
    python scripts/install_hooks.py

校验项：
    1. checkregister   文档书写规范（docs/STYLE.md 第 2 节）
    2. checkcopy       文案禁用词
    3. selftest        脚本冒烟（含规范校验）
    4. reproduce       watch 复现验收（不重跑，只比对）
    5. reproduce       nanzhi 复现验收（不重跑，只比对）

退出码：0 全部通过；1 有失败项（git 会中止提交）
"""
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable

CHECKS = [
    ("checkregister", [os.path.join(HERE, "checkregister.py"), ROOT]),
    ("checkcopy", [os.path.join(HERE, "checkcopy.py"), ROOT, "--ext", ".md,.py,.txt"]),
    ("selftest", [os.path.join(HERE, "selftest.py")]),
    ("reproduce-watch", [os.path.join(HERE, "reproduce.py"), "--case", "watch", "--no-run"]),
    ("reproduce-nanzhi", [os.path.join(HERE, "reproduce.py"), "--case", "nanzhi", "--no-run"]),
]


def main():
    print("=" * 54)
    print("  提交前闸门")
    print("=" * 54)
    failed = []
    for name, cmd in CHECKS:
        r = subprocess.run([PY] + cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=ROOT)
        code = r.returncode
        tail = ((r.stdout or r.stderr or "").strip().splitlines() or [""])[-1]
        print(f"  {name:<18} 退出码 {code}   {tail[:60]}")
        if code != 0:
            failed.append((name, r.stdout or r.stderr))

    print("-" * 54)
    if not failed:
        print("  全部通过")
        return 0

    print(f"  {len(failed)} 项未通过，提交已中止：")
    for name, out in failed:
        print(f"\n[{name}]")
        print((out or "")[-800:])
    return 1


if __name__ == "__main__":
    sys.exit(main())
