# -*- coding: utf-8 -*-
"""gen_batch.py —— 按矩阵批量生成素材，并回写溯源记录

解决的问题：
    gen_images.py 只能处理"一行一条提示词"的平铺文件，生成结果与页面、
    与提示词之间没有对应关系，事后无法追溯某张素材出自哪条提示词。

数据结构（examples/<case>/prompts.jsonl，一行一条 JSON）：

    {
      "asset":     "g-03-hero",            // 素材标识，与 assets/ 文件名对应
      "page":      "01-hero",              // 目标页面
      "prompt":    "…身份锁/场景锁/创意锁…",
      "aspect":    "3:4",
      "n":         1,
      "granularity": "asset",             // asset=逐张记录；category=按类记录
      "verdict":   "pending",             // pending / accepted / rejected
      "note":      "",                    // 裁决理由
      "files":     []                     // 生成后回写：实际产出文件
    }

用法：
    python scripts/gen_batch.py --case watch --dry-run          # 只校验结构
    python scripts/gen_batch.py --case watch --only 01-hero     # 只生成指定页
    python scripts/gen_batch.py --case watch                    # 全量（跳过 verdict=accepted）
    python scripts/gen_batch.py --case watch --mark g-03-hero accepted --note "无虚构文本"

说明：
    - 已 accepted 的条目默认跳过（--force 可覆盖）
    - 生成结果写入 examples/<case>/assets/gen/，文件名前缀为 asset 标识
    - 每次调用追加到 examples/<case>/prompts.calls.jsonl
    - 无 MINIMAX_API_KEY 时自动进入 --dry-run 语义，不会静默失败
"""
import argparse
import json
import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import gen_images  # noqa: E402  复用 key 读取与 API 调用

REQUIRED = ("asset", "prompt")
VALID_VERDICT = ("pending", "accepted", "rejected")


def load(path):
    items = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path} 第 {i} 行不是合法 JSON：{e}")
            for k in REQUIRED:
                if k not in obj:
                    raise SystemExit(f"{path} 第 {i} 行缺少字段 {k}")
            obj.setdefault("aspect", "3:4")
            obj.setdefault("n", 1)
            obj.setdefault("granularity", "asset")
            obj.setdefault("verdict", "pending")
            obj.setdefault("note", "")
            obj.setdefault("files", [])
            if obj["verdict"] not in VALID_VERDICT:
                raise SystemExit(f"{path} 第 {i} 行 verdict 非法：{obj['verdict']}")
            items.append(obj)
    return items


def save(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


def report(items):
    from collections import Counter
    c = Counter(it["verdict"] for it in items)
    g = Counter(it["granularity"] for it in items)
    pages = len({it.get("page") for it in items if it.get("page")})
    print(f"  条目 {len(items)} 条，覆盖 {pages} 页")
    print(f"  裁决 {dict(c)}")
    print(f"  记录粒度 {dict(g)}")
    if g.get("category"):
        print("  注意：granularity=category 表示按类别记录，无法逐张重生成")


def main():
    ap = argparse.ArgumentParser(description="按矩阵批量生成素材并回写溯源")
    ap.add_argument("--case", required=True, choices=["watch", "nanzhi"])
    ap.add_argument("--only", help="只处理指定 page")
    ap.add_argument("--dry-run", action="store_true", help="只校验结构与统计")
    ap.add_argument("--force", action="store_true", help="accepted 条目也重新生成")
    ap.add_argument("--mark", nargs=2, metavar=("ASSET", "VERDICT"),
                    help="人工裁决某条：--mark g-03-hero accepted")
    ap.add_argument("--note", default="", help="配合 --mark 记录裁决理由")
    args = ap.parse_args()

    case_dir = os.path.join(ROOT, "examples", args.case)
    path = os.path.join(case_dir, "prompts.jsonl")
    if not os.path.exists(path):
        print(f"缺少 {path}")
        return 2

    items = load(path)

    # 人工裁决模式
    if args.mark:
        asset, verdict = args.mark
        if verdict not in VALID_VERDICT:
            print(f"verdict 须为 {VALID_VERDICT}")
            return 2
        hit = 0
        for it in items:
            if it["asset"] == asset:
                it["verdict"] = verdict
                if args.note:
                    it["note"] = args.note
                hit += 1
        if not hit:
            print(f"未找到 asset={asset}")
            return 2
        save(path, items)
        print(f"已标记 {asset} → {verdict}")
        return 0

    print("=" * 56)
    print(f"  批量素材生成 · {args.case}")
    print("=" * 56)
    report(items)

    if args.dry_run:
        print("\n  dry-run：未发起请求")
        for it in items[:5]:
            print(f"    {it['asset']:<14} 页 {it.get('page','-'):<10} {it['prompt'][:30]}…")
        return 0

    key = gen_images.load_key()
    if not key:
        print("\n  未配置 MINIMAX_API_KEY，转入 dry-run（结构已校验）")
        return 0

    todo = [it for it in items
            if (args.force or it["verdict"] != "accepted")
            and (not args.only or it.get("page") == args.only)]
    if not todo:
        print("\n  没有待生成条目（全部 accepted，或用 --force 覆盖）")
        return 0

    out_dir = os.path.join(case_dir, "assets", "gen")
    os.makedirs(out_dir, exist_ok=True)
    calls_log = os.path.join(case_dir, "prompts.calls.jsonl")

    ok = fail = 0
    for i, it in enumerate(todo, 1):
        print(f"  [{i}/{len(todo)}] {it['asset']}  ({it.get('page','-')})")
        full = gen_images.build_prompt(it["prompt"])
        try:
            urls, resp = gen_images.call_api(key, full, n=int(it["n"]), aspect=it["aspect"])
        except Exception as e:
            print(f"      失败：{type(e).__name__}: {e}")
            fail += 1
            continue
        if not urls:
            print(f"      无返回：{resp}")
            fail += 1
            continue
        saved = []
        for j, u in enumerate(urls, 1):
            try:
                # 用 asset 标识命名，便于与 prompts.jsonl 对应
                name = f"{it['asset']}-{time.strftime('%Y%m%d-%H%M%S')}-{j}.jpg"
                p = os.path.join(out_dir, name)
                gp = gen_images.download(u, out_dir, f"{it['asset']}-{j}")
                os.replace(gp, p)
                saved.append(os.path.relpath(p, case_dir))
            except Exception as e:
                print(f"      下载失败：{type(e).__name__}")
        it["files"] = saved
        it["verdict"] = "pending" if saved else it["verdict"]
        ok += len(saved)
        with open(calls_log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"asset": it["asset"], "page": it.get("page"),
                                "prompt": full, "n": len(saved), "files": saved},
                               ensure_ascii=False) + "\n")
        save(path, items)   # 每条生成后落盘，支持中断续跑
        print(f"      存了 {len(saved)} 张")

    print(f"\n完成：{ok} 张，失败 {fail} 条")
    print("下一步：逐张人工裁决（虚构文本、瓶型漂移）→ --mark <asset> accepted/rejected")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
