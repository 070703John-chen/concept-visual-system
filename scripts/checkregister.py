# -*- coding: utf-8 -*-
"""checkregister.py —— 文档书写规范校验（对应 docs/STYLE.md 第 2 节）

用法：
    python scripts/checkregister.py .              # 校验仓库内 Markdown
    python scripts/checkregister.py docs README.md
    python scripts/checkregister.py . --warn-only

判定：
  1. 禁止词命中（祈使/口语/口号/拟人/主观程度）
  2. 标题为疑问句或祈使句
  3. 数值格式（容差、百分比、尺寸）

退出码：0 通过；1 命中
"""
import argparse
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 禁止词 → 建议改法（按 docs/STYLE.md 第 2 节）
BANNED = {
    "别写": "改为规则陈述，如「限用四档字号」",
    "别指望": "改为边界陈述，如「提示词的作用边界」",
    "不要用": "改为规则陈述",
    "不许": "改为「禁止」或「限用」",
    "不要": "改为「禁止」或删除",
    "其实": "删除",
    "反正": "删除",
    "说白了": "删除",
    "搞定": "改为「完成」",
    "咱们": "改为「本仓库」",
    "踩坑": "改为「已知问题」",
    "踩过": "改为「已记录」",
    "一句话：": "改为「概述：」",
    "很弱": "附判定值",
    "特别乱": "附判定值",
    "非常明显": "附判定值",
}

# 允许出现的上下文（引号内引用、代码块、规范自身举例）
CODE_FENCE = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`]*`")
QUOTED = re.compile(r"「[^」]*」|\"[^\"]*\"|“[^”]*”")

HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.M)
QUESTION_TAIL = re.compile(r"[？?]\s*$")
IMPERATIVE_HEAD = re.compile(r"^(为什么|怎么|如何|别|不要|不许|要不要|能不能)")

# 数值格式检查
BAD_TOLERANCE = re.compile(r"容差\s*[0-9]+(?!/)")
BAD_PERCENT = re.compile(r"(?<![0-9])[0-9]{1,3}\s*％")


def strip_noise(text):
    """移除代码块、行内代码、引号内容，避免规范自身举例被误判"""
    t = CODE_FENCE.sub(" ", text)
    t = INLINE_CODE.sub(" ", t)
    t = QUOTED.sub(" ", t)
    return t


def iter_md(paths):
    for p in paths:
        if os.path.isfile(p) and p.endswith(".md"):
            yield p
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in (".git", "out", "node_modules", "__pycache__")]
                for f in files:
                    if f.endswith(".md"):
                        yield os.path.join(root, f)


def check_file(path, warn_only):
    try:
        raw = open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return 0, 0
    body = strip_noise(raw)
    hits = []

    # 1) 禁止词
    for lineno, line in enumerate(body.splitlines(), 1):
        for w, fix in BANNED.items():
            if w in line:
                hits.append((lineno, "禁止词", w, fix, line.strip()[:60]))

    # 2) 标题句式（标题行不参与 strip_noise 的引号处理，需用原文）
    for m in HEADING.finditer(raw):
        title = m.group(2).strip()
        lineno = raw[:m.start()].count("\n") + 1
        if QUESTION_TAIL.search(title) or IMPERATIVE_HEAD.search(title):
            hits.append((lineno, "标题句式", title[:20], "改为名词短语", title[:60]))

    # 3) 数值格式
    for lineno, line in enumerate(body.splitlines(), 1):
        if BAD_PERCENT.search(line):
            hits.append((lineno, "数值格式", "全角百分号", "改为半角 %", line.strip()[:60]))

    if not hits:
        return 0, 0
    rel = path
    print(f"\n{rel}")
    for lineno, kind, detail, fix, snippet in hits:
        print(f"  {lineno:>5} 行  [{kind}] {detail}  → {fix}")
        print(f"          {snippet}")
    return len(hits), len(hits) if warn_only else 0


def main():
    ap = argparse.ArgumentParser(description="Markdown 书写规范校验")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--warn-only", action="store_true", help="只报不失败")
    args = ap.parse_args()

    files = list(iter_md(args.paths))
    if not files:
        print("没有找到 Markdown 文件")
        return 0

    total = 0
    bad = 0
    for f in files:
        n, _ = check_file(f, args.warn_only)
        if n:
            total += n
            bad += 1

    print("\n" + "-" * 52)
    if total == 0:
        print(f"通过：{len(files)} 个 Markdown，未命中禁止项")
        return 0
    print(f"命中 {total} 处，涉及 {bad} 个文件（共 {len(files)} 个）")
    print("规则见 docs/STYLE.md 第 2 节")
    return 0 if args.warn_only else 1


if __name__ == "__main__":
    sys.exit(main())
