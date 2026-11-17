# -*- coding: utf-8 -*-
"""gen_images.py —— 素材生成段（MiniMax image-01）

为什么这一段必须入库：
    排版管线只能把"已有素材"排好；素材怎么来的，决定了换一个产品还能不能做出同样水准。
    没有这一步，仓库只是"某一次的排版代码"。

用法：
    # 1) 只检查环境（不花钱、不发请求）
    python scripts/gen_images.py --check

    # 2) 按提示词清单生成（需要 MINIMAX_API_KEY）
    python scripts/gen_images.py --prompts examples/watch/prompts/hero.txt --out ./gen

    # 3) 没有 key 时，走排版专用退路：只列清单，不生成
    python scripts/gen_images.py --prompts examples/watch/prompts/hero.txt --no-gen

    # 4) 单独一条提示词
    python scripts/gen_images.py --prompt "..." --n 3 --out ./gen

约定：
    key 从环境变量 MINIMAX_API_KEY 或仓库根的 .env 读取（见 .env.example）。
    生成结果文件名带时间戳，避免覆盖；每次调用把 prompt 与参数写进 gen/calls.jsonl。
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
ENV_FILE = os.path.join(ROOT, ".env")
API_URL = "https://api.minimax.chat/v1/image_generation"
MODEL = "image-01"

# 生成图必须带的负向约束（踩过的坑：正面表盘会编出假品牌名与假日历窗）
HARD_NEGATIVE = ("no text, no letters, no numbers, no brand name, no logo, "
                 "no watermark, no calendar window")


def load_key():
    key = os.environ.get("MINIMAX_API_KEY")
    if key:
        return key.strip()
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == "MINIMAX_API_KEY":
                return v.strip().strip('"').strip("'")
    return None


def check():
    key = load_key()
    print("=" * 54)
    print("  生图段环境检查")
    print("=" * 54)
    print(f"  API      {API_URL}  （模型 {MODEL}）")
    print(f"  .env     {'存在' if os.path.exists(ENV_FILE) else '不存在'}  {ENV_FILE}")
    print(f"  KEY      {'已配置（长度 %d）' % len(key) if key else '未配置'}")
    if not key:
        print("\n  没有 key 也能用：排版管线与 reproduce.py 完全不依赖生图。")
        print("  想真正生成素材：复制 .env.example 为 .env，填入 MINIMAX_API_KEY。")
        return 1
    return 0


def build_prompt(text, extra_negative=""):
    neg = HARD_NEGATIVE + ("，" + extra_negative if extra_negative else "")
    return f"{text.strip()}\n\nNegative: {neg}"


def call_api(key, prompt, n=1, aspect="3:4"):
    """MiniMax image-01：返回图片 URL 列表"""
    import urllib.request
    body = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "aspect_ratio": aspect,
        "response_format": "url",
        "n": max(1, min(4, n)),
        "prompt_optimizer": True,
    }).encode("utf-8")
    req = urllib.request.Request(API_URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=180) as r:
        data = json.loads(r.read().decode("utf-8"))
    urls = []
    for item in (data.get("data") or {}).get("image_urls", []) or []:
        urls.append(item if isinstance(item, str) else item.get("url"))
    return [u for u in urls if u], data.get("base_resp", {})


def download(url, out_dir, idx):
    import urllib.request
    os.makedirs(out_dir, exist_ok=True)
    name = f"gen-{time.strftime('%Y%m%d-%H%M%S')}-{idx}.jpg"
    path = os.path.join(out_dir, name)
    req = urllib.request.Request(url, headers={"User-Agent": "concept-visual-system/gen"})
    with urllib.request.urlopen(req, timeout=180) as r, open(path, "wb") as f:
        f.write(r.read())
    return path


def read_prompts(path):
    """一行一条提示词；# 开头是注释；空行跳过"""
    out = []
    for line in open(path, encoding="utf-8"):
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser(description="素材生成（MiniMax image-01）")
    ap.add_argument("--check", action="store_true", help="只检查环境，不发请求")
    ap.add_argument("--prompt", help="单条提示词")
    ap.add_argument("--prompts", help="提示词文件（一行一条）")
    ap.add_argument("--out", default="./gen", help="输出目录")
    ap.add_argument("--n", type=int, default=1, help="每条生成几张（1–4）")
    ap.add_argument("--aspect", default="3:4", help="比例，默认 3:4")
    ap.add_argument("--no-gen", action="store_true", help="只打印清单，不生成（无 key 时的退路）")
    args = ap.parse_args()

    if args.check:
        return check()

    key = load_key()
    prompts = []
    if args.prompts:
        prompts += read_prompts(args.prompts)
    if args.prompt:
        prompts.append(args.prompt)
    if not prompts:
        print("没给提示词。用 --prompt 或 --prompts"); return 2

    print("=" * 54)
    print(f"  素材生成 · {len(prompts)} 条 × {args.n} 张")
    print("=" * 54)

    if args.no_gen or not key:
        if not key:
            print("  [提示] 未配置 MINIMAX_API_KEY，进入 --no-gen 模式（只列清单）\n")
        for i, p in enumerate(prompts, 1):
            print(f"  [{i}] {build_prompt(p)}\n")
        print("  清单已打印。配好 key 后去掉 --no-gen 即可真正生成。")
        return 0

    os.makedirs(args.out, exist_ok=True)
    log = os.path.join(args.out, "calls.jsonl")
    total = 0
    for i, p in enumerate(prompts, 1):
        full = build_prompt(p)
        print(f"  [{i}/{len(prompts)}] 生成中… {p[:40]}")
        try:
            urls, resp = call_api(key, full, n=args.n, aspect=args.aspect)
        except Exception as e:
            print(f"      失败：{type(e).__name__}: {e}")
            continue
        if not urls:
            print(f"      无返回：{resp}")
            continue
        saved = []
        for j, u in enumerate(urls, 1):
            try:
                saved.append(download(u, args.out, f"{i}-{j}"))
            except Exception as e:
                print(f"      下载失败：{type(e).__name__}")
        total += len(saved)
        with open(log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"prompt": full, "aspect": args.aspect,
                                "n": len(saved), "files": [os.path.basename(s) for s in saved]},
                               ensure_ascii=False) + "\n")
        print(f"      存了 {len(saved)} 张")

    print(f"\n完成：{total} 张 → {args.out}")
    print("下一步：人工过一遍（假字/假品牌名/瓶型不一致的丢掉），再跑 grade.py 统一调色。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
