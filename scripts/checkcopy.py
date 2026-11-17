# -*- coding: utf-8 -*-
"""checkcopy.py —— 扫源文件里的禁用词

用法：
    python checkcopy.py <路径...> [选项]

示例：
    python checkcopy.py D:\\项目\\build_layout.py
    python checkcopy.py D:\\项目 --ext .py,.md
    python checkcopy.py D:\\项目 --warn-only      # 只报不退出错误

规则表默认读同目录上层的 templates/forbidden-claims.txt，
也可以 --banned 指定自己的表。

退出码：0 = 干净；1 = 命中禁用词；2 = 参数/文件问题
"""
import os
import sys
import argparse
import re

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

_TPL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
DEFAULT_BANNED = os.path.join(_TPL, "forbidden-claims.txt")
DEFAULT_ALLOW = os.path.join(_TPL, "allowlist.txt")


def load_banned(path):
    words = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            words.append(s)
    # 长词优先，避免"匠心"先命中"匠心力作"
    words.sort(key=len, reverse=True)
    return words


def load_allow(path):
    """白名单短语：命中禁用词前先剔除这些片段，避免"第一辑"被当成"第一" """
    out = []
    if not path or not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                out.append(s)
    out.sort(key=len, reverse=True)
    return out


QUOTE_PAT = re.compile(r'"[^"]*"|\u201c[^\u201d]*\u201d|\u300c[^\u300d]*\u300d')


def mask_quotes(line):
    """把引号内的内容（中英文双引号/直角引号）替换成占位符：文档里引用禁用词不算违规"""
    return QUOTE_PAT.sub(lambda m: "\u3000" * len(m.group(0)), line)


def mask_allow(line, allow):
    """把白名单短语替换成等长的占位符，位置不变、长度不变"""
    for a in allow:
        if a in line:
            line = line.replace(a, "\u3000" * len(a))
    return line


SKIP_NAMES = {"forbidden-claims.txt", "allowlist.txt"}


def iter_files(paths, exts, excludes=()):
    import fnmatch
    for p in paths:
        if os.path.isfile(p):
            yield p
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                if "__pycache__" in root or ".git" in root:
                    continue
                for fn in files:
                    if os.path.splitext(fn)[1].lower() not in exts:
                        continue
                    if fn in SKIP_NAMES:
                        continue
                    full = os.path.join(root, fn)
                    if any(fnmatch.fnmatch(full.replace("\\", "/"), pat) for pat in excludes):
                        continue
                    yield full


def scan_file(path, words, allow=(), skip_comments=True):
    is_doc = os.path.splitext(path)[1].lower() in (".md", ".txt")
    hits = []
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            for no, line in enumerate(f, 1):
                # 只有文档才把引号内当引用；代码里的字符串就是文案，不能被屏蔽
                raw = mask_allow(mask_quotes(line) if is_doc else line, allow)
                if skip_comments:
                    s = raw.lstrip()
                    # 跳过整行注释（# 或 // 或 *），减少误报
                    # 文档里的"反例行"不算违规：✗ / ❌ / - ✗
                    _strip = s.lstrip("-*• ").lstrip()
                    NEG_MARKS = ("✗", "❌", "不许写", "不能写", "禁用", "禁止", "不要写", "checkcopy:ignore")
                    if (s.startswith("#") or s.startswith("//") or s.startswith("*")
                            or _strip.startswith("✗") or _strip.startswith("❌")
                            or any(k in _strip for k in NEG_MARKS)):
                        continue
                for w in words:
                    if w in raw:
                        col = raw.find(w) + 1
                        hits.append((no, col, w, raw.strip()[:90]))
                        break  # 一行只报一次，避免刷屏
    except Exception as e:
        print(f"  [读取失败] {path}: {type(e).__name__}", file=sys.stderr)
    return hits


def main():
    ap = argparse.ArgumentParser(description="扫描源文件中的禁用词（空形容词/大词/促销话术/编造数据）")
    ap.add_argument("paths", nargs="+", help="要扫的文件或目录")
    ap.add_argument("--ext", default=".py,.md,.txt,.json,.html",
                    help="目录下要扫的扩展名，逗号分隔（默认 .py,.md,.txt,.json,.html）")
    ap.add_argument("--banned", default=DEFAULT_BANNED, help="禁用词表路径")
    ap.add_argument("--warn-only", action="store_true", help="只报不报错（退出码仍为 0）")
    ap.add_argument("--all", action="store_true", help="连注释行一起扫（默认跳过）")
    ap.add_argument("--allow", default=DEFAULT_ALLOW, help="白名单文件路径")
    ap.add_argument("--exclude", default="", help="排除的文件 glob，逗号分隔，例如 *_test.py,*/reference/*")
    args = ap.parse_args()

    if not os.path.exists(args.banned):
        print(f"[错误] 找不到禁用词表：{args.banned}", file=sys.stderr)
        return 2

    words = load_banned(args.banned)
    allow = load_allow(args.allow)
    exts = tuple(x.strip().lower() for x in args.ext.split(",") if x.strip())

    excludes = [x.strip() for x in args.exclude.split(",") if x.strip()]
    files = list(iter_files(args.paths, exts, excludes))
    if not files:
        print("[提示] 没找到可扫的文件（检查 --ext 或路径）")
        return 0

    total = 0
    bad_files = 0
    for fp in files:
        hits = scan_file(fp, words, allow=allow, skip_comments=not args.all)
        if not hits:
            continue
        bad_files += 1
        total += len(hits)
        print(f"\n{fp}")
        for no, col, w, snippet in hits:
            print(f"  {no:>5} 行  「{w}」  {snippet}")

    print("\n" + "─" * 52)
    if total == 0:
        print(f"通过：扫了 {len(files)} 个文件，没有禁用词")
        return 0
    print(f"命中 {total} 处，涉及 {bad_files} 个文件（扫了 {len(files)} 个文件）")
    print("处理：改成「部位 + 动词 + 结果 + 依据」，或删掉这句")
    return 0 if args.warn_only else 1


if __name__ == "__main__":
    sys.exit(main())
