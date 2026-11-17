# -*- coding: utf-8 -*-
"""alpha_pages.py —— 把不透明页面重建成透明 PNG（阶段 ⑥ 的第一步）

原理（对应原始 `_alpha.py`）：
  复制页面脚本 → 把画布 `Image.new("RGB", …, 底色)` 改成 `Image.new("RGBA", …, (0,0,0,0))`
  → 输出扩展名 .jpg 改 .png → 重新执行一遍

为什么必须这么做：
  长图要"文字与图块浮在连续背景上"，而不是每页各带一块底色。
  不透明页贴上去会在页与页之间露出硬边。

用法：
    python scripts/alpha_pages.py
    python scripts/alpha_pages.py --keep-build   # 保留改写后的脚本，便于排查
"""
import os
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cfg import OUT  # noqa: E402

# 需要透明化的页面脚本（其余脚本本来就直出 PNG）
TARGETS = [
    "build_rules.py",
    "build_fill.py",
    "build_layout.py",
    "build_kv2.py",
    "build_fix_4_11.py",
    "build_merge.py",
    "build_scenes2.py",
]

# 画布替换规则（覆盖几个脚本里出现过的写法）
CANVAS_RULES = [
    ('Image.new("RGB",(W,H),c(BG))',       'Image.new("RGBA",(W,H),(0,0,0,0))'),
    ('Image.new("RGB", (W, H), c(BG))',    'Image.new("RGBA", (W, H), (0,0,0,0))'),
    ('Image.new("RGB",(W,H),(14,11,8))',   'Image.new("RGBA",(W,H),(0,0,0,0))'),
    ('Image.new("RGB",(W,H),BG)',          'Image.new("RGBA",(W,H),(0,0,0,0))'),
    ('Image.new("RGB", (W, H), rgb(PAPER))', 'Image.new("RGBA", (W, H), (0,0,0,0))'),
    ('Image.new("RGB", (W, H), rgb(DARK))',  'Image.new("RGBA", (W, H), (0,0,0,0))'),
    ('Image.new("RGB",(W,520),rgb(DARK))',   'Image.new("RGBA",(W,520),(0,0,0,0))'),
]


def patch(src_text):
    t = src_text
    # 改写副本放在 out/_alpha_build/，要让它仍能 import 到 scripts 目录下的 kit/cfg
    t = t.replace('sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))',
                  'sys.path.insert(0, %r)' % HERE)
    hit = False
    for a, b in CANVAS_RULES:
        if a in t:
            t = t.replace(a, b)
            hit = True
    # 只改"输出文件"的扩展名：锚定 save(os.path.join(OUT, "...jpg"))
    # 千万别全局替换 .jpg —— 会把素材名 g-s7-hand.jpg 也改掉（踩过）
    import re as _re
    t = _re.sub(r'(save\(\s*os\.path\.join\(\s*OUT\s*,\s*")([^"]+)\.jpg(")',
                r'\1\2.png\3', t)
    t = t.replace("quality=95, optimize=True", "")
    return t, hit


def main():
    keep = "--keep-build" in sys.argv
    build_dir = os.path.join(OUT, "_alpha_build")
    shutil.rmtree(build_dir, ignore_errors=True)
    os.makedirs(build_dir, exist_ok=True)

    env = dict(os.environ)
    env["CVS_OUT"] = OUT                     # 改写版脚本也输出到 out/
    env["PYTHONIOENCODING"] = "utf-8"

    print("=" * 54)
    print("  页面透明化（RGB → RGBA，jpg → png）")
    print("=" * 54)

    ok = 0
    for fn in TARGETS:
        src = os.path.join(HERE, fn)
        if not os.path.exists(src):
            print(f"  {fn:<22} 跳过（不存在）")
            continue
        t, hit = patch(open(src, encoding="utf-8").read())
        if not hit:
            print(f"  {fn:<22} 跳过（没找到 RGB 画布写法）")
            continue
        dst = os.path.join(build_dir, fn)
        open(dst, "w", encoding="utf-8").write(t)
        r = subprocess.run([sys.executable, dst], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=HERE, env=env)
        tail = (r.stdout or r.stderr or "").strip().splitlines()
        status = "OK" if r.returncode == 0 else "FAIL"
        print(f"  {fn:<22} {status}  {tail[-1] if tail else ''}")
        if r.returncode == 0:
            ok += 1
        else:
            print((r.stderr or "")[-400:])

    if not keep:
        shutil.rmtree(build_dir, ignore_errors=True)

    pngs = sorted(f for f in os.listdir(OUT) if f.endswith(".png") and f[0].isdigit())
    print(f"\n透明页 {len(pngs)} 张：{', '.join(pngs)}")
    print(f"成功 {ok} / {len(TARGETS)} 个脚本")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
