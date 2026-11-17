# -*- coding: utf-8 -*-
"""install_hooks.py —— 安装 git 提交前钩子（每个 clone 执行一次）

    python scripts/install_hooks.py

安装后，每次 `git commit` 都会先执行 `scripts/precommit.py`，
任一校验失败即中止提交。跳过（不推荐）：

    git commit --no-verify
"""
import os
import stat
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOOK = """#!/bin/sh
# 由 scripts/install_hooks.py 生成
exec python "{root}/scripts/precommit.py"
""".format(root=ROOT.replace("\\", "/"))


def main():
    hooks_dir = os.path.join(ROOT, ".git", "hooks")
    if not os.path.isdir(hooks_dir):
        print("当前目录不是 git 仓库根目录：", ROOT)
        return 2

    path = os.path.join(hooks_dir, "pre-commit")
    if os.path.exists(path):
        print(f"已存在 {path}，将覆盖")

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(HOOK)
    # Unix 下需要可执行权限；Windows 忽略
    try:
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    except Exception:
        pass

    print(f"已安装钩子：{path}")
    print("验证：python scripts/precommit.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
