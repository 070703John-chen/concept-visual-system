# -*- coding: utf-8 -*-
"""selftest.py —— 冒烟测试：用合成样图跑一遍全流程，确认脚本没被改坏

用法：
    python selftest.py                 # 在临时目录里跑，结束自动清理
    python selftest.py --keep          # 保留临时目录，便于看产物

检查项：
  1. grade.py       能处理图片，输出尺寸不变、色值有变化、不产生 NaN
  2. compose_long.py 能合成透明页，长图高度 = 各页高 + 间距，切回单页尺寸一致
  3. 长图底部不存在整行纯黑（说明羽化/背景生效）

退出码：0 = 全过；1 = 有失败
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GRADE = os.path.join(HERE, "grade.py")
COMPOSE = os.path.join(HERE, "compose_long.py")
PY = sys.executable


def make_samples(d):
    """造三张合成样图：渐变底 + 圆，避免依赖任何真实素材"""
    from PIL import Image, ImageDraw
    import numpy as np
    paths = []
    for i, (c1, c2) in enumerate([((90, 60, 40), (20, 16, 12)),
                                  ((60, 70, 90), (14, 16, 20)),
                                  ((110, 90, 60), (30, 22, 16))]):
        w, h = 600, 800
        t = np.linspace(0, 1, h)[:, None]
        a = (np.array(c1)[None, None, :] * (1 - t[:, :, None]) +
             np.array(c2)[None, None, :] * t[:, :, None])
        a = np.repeat(a, w, axis=1).astype(np.uint8)
        im = Image.fromarray(a)
        dr = ImageDraw.Draw(im)
        dr.ellipse([150, 250, 450, 600], fill=(200, 180, 150))
        p = os.path.join(d, f"sample{i}.jpg")
        im.save(p, quality=92)
        paths.append(p)
    return paths


def make_pages(d, n=2):
    """造两页透明 PNG（模拟成品页）"""
    from PIL import Image, ImageDraw
    pages = []
    for i in range(n):
        im = Image.new("RGBA", (1200, 900), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        dr.rectangle([72, 72, 1128, 828], outline=(192, 138, 74, 255), width=2)
        dr.text((100, 120), f"PAGE {i+1}", fill=(240, 230, 210, 255))
        p = os.path.join(d, f"p{i+1}.png")
        im.save(p)
        pages.append(p)
    return pages


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


FAILED = [0]


def check(name, cond, detail=""):
    print(("  [PASS] " if cond else "  [FAIL] ") + name + ("" if cond else f"  → {detail}"))
    if not cond:
        FAILED[0] += 1
    return cond


def main():
    ap = argparse.ArgumentParser(description="脚本冒烟测试")
    ap.add_argument("--keep", action="store_true", help="保留临时目录")
    args = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="cvs_selftest_")
    print("=" * 54)
    print("  视觉系统 · 冒烟测试")
    print("=" * 54)
    print(f"临时目录：{tmp}\n")

    try:
        # ---- 1) grade ----
        print("[1/4] grade.py 统一调色")
        src_dir = os.path.join(tmp, "src")
        os.makedirs(src_dir, exist_ok=True)
        samples = make_samples(src_dir)
        out_dir = os.path.join(tmp, "graded")
        code, log = run([PY, GRADE, src_dir, "-o", out_dir])
        ok = check("grade.py 正常退出", code == 0, log.strip()[-200:])
        if ok:
            from PIL import Image
            import numpy as np
            outs = [f for f in os.listdir(out_dir) if f.lower().endswith((".jpg", ".png"))]
            ok2 = check("输出文件数 = 输入数", len(outs) == len(samples), f"{len(outs)} vs {len(samples)}")
            if ok2:
                a = np.asarray(Image.open(os.path.join(src_dir, "sample0.jpg")).convert("RGB")).astype(float)
                b = np.asarray(Image.open(os.path.join(out_dir, "sample0.jpg")).convert("RGB")).astype(float)
                check("尺寸未变", a.shape == b.shape, f"{a.shape} vs {b.shape}")
                check("确实改过色（均值差 > 2）", abs(a.mean() - b.mean()) > 2, f"diff={abs(a.mean()-b.mean()):.2f}")
                check("无 NaN / 全黑", b.max() > 10 and not np.isnan(b).any())

        # ---- 2) compose_long ----
        print("\n[2/4] compose_long.py 连续背景长图")
        page_dir = os.path.join(tmp, "pages")
        os.makedirs(page_dir, exist_ok=True)
        pages = make_pages(page_dir)
        code, log = run([PY, COMPOSE, page_dir])
        ok = check("compose_long.py 正常退出", code == 0, log.strip()[-200:])
        if ok:
            from PIL import Image
            import numpy as np
            long_img = os.path.join(page_dir, "长图.jpg")
            ok2 = check("长图已生成", os.path.exists(long_img))
            if ok2:
                im = Image.open(long_img)
                # compose_long 会按 alpha bbox 裁掉透明边，预期高度要按裁切后算
                hs = []
                for p in pages:
                    pi = Image.open(p).convert("RGBA")
                    bb = pi.getbbox()
                    hs.append((bb[3] - bb[1]) if bb else pi.height)
                exp_h = sum(hs) + 20 * (len(pages) - 1)
                check("长图高度正确", im.height == exp_h, f"{im.height} vs {exp_h}")
                check("长图宽度 = 1200", im.width == 1200, str(im.width))
                seg = np.asarray(im.convert("L")).astype(float)
                rows = seg.mean(axis=1)
                check("无整行纯黑", rows.min() > 2, f"最暗行均值 {rows.min():.2f}")
                back = [f for f in os.listdir(page_dir) if f.startswith("p") and f.endswith(".jpg")]
                check("切回单页数量正确", len(back) == len(pages), f"{len(back)}")
                if back:
                    s = Image.open(os.path.join(page_dir, sorted(back)[0]))
                    check("切回单页尺寸正确", s.width == 1200, str(s.size))

        # ---- 3) 文档规范 ----
        print("\n[3/4] checkregister.py 文档规范")
        code, log = run([PY, os.path.join(HERE, "checkregister.py"), ROOT])
        check("文档规范校验通过", code == 0, (log or "").strip()[-200:])

        # ---- 4) 文案扫描器 ----
        print("\n[4/4] checkcopy.py 禁用词扫描")
        bad = os.path.join(tmp, "bad.py")
        with open(bad, "w", encoding="utf-8") as f:
            f.write('d.text((M, 92), "高级质感 · 行业第一", font=S(40))\n')  # checkcopy:ignore 测试用故意违规串
        code, log = run([PY, os.path.join(HERE, "checkcopy.py"), bad])
        check("违规文件返回退出码 1", code == 1, f"exit={code}")
        clean = os.path.join(tmp, "clean.py")
        with open(clean, "w", encoding="utf-8") as f:
            f.write('d.text((M, 92), "10.8 mm · 滑进袖口 · 不顶那一下", font=S(40))\n')
        code2, _ = run([PY, os.path.join(HERE, "checkcopy.py"), clean])
        check("干净文件返回退出码 0", code2 == 0, f"exit={code2}")

    finally:
        if args.keep:
            print(f"\n产物保留在：{tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "-" * 54)
    if FAILED[0]:
        print(f"失败 {FAILED[0]} 项 —— 脚本被改坏了，先修再交付")
        return 1
    print("全部通过 —— 三个脚本的功能正常")
    return 0


if __name__ == "__main__":
    sys.exit(main())
