# -*- coding: utf-8 -*-
"""P1 作品集封面（纯字体，重写）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw
from kit import S

from cfg import OUT as OUT   # noqa: E402
W, H, M = 1200, 1600, 72
FG, SUB, GOLD = "#EFE3CE", "#8A7358", "#C08A4A"
T4 = 12

def c(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))

cv = Image.new("RGBA",(W,H),(0,0,0,0))
d = ImageDraw.Draw(cv)

# 顶部品牌
d.text((M, 60), "GUĀNSHÍ", font=S(24,"Medium"), fill=c(GOLD))
bw = d.textlength("GUĀNSHÍ", font=S(24,"Medium"))
d.text((M+bw+6, 54), "™", font=S(11,"Medium"), fill=c(GOLD))
d.text((M, 104), "A SELF-INITIATED CONCEPT PROJECT", font=S(T4), fill=c(SUB))

# 巨型英文三行
d.text((M-6, 330), "MECHANICAL", font=S(100,"Bold"), fill=c(FG))
d.text((M-6, 446), "WATCH", font=S(100,"Bold"), fill=c(FG))
d.text((M-6, 562), "VISUAL SYSTEM", font=S(100,"Bold"), fill=c(GOLD))

# 细线 + 中文
d.line([(M, 726), (W-M, 726)], fill=c("#4A3722"), width=1)
d.text((M, 756), "机械腕表 · 自命题概念设计 · 2026", font=S(26,"Medium"), fill=c("#DCC7A8"))
d.text((M, 806), "18 PAGES  /  1200 × 1600  /  SEEDREAM + MINIMAX", font=S(T4), fill=c(SUB))

# 底部数据行
d.line([(M, H-300), (W-M, H-300)], fill=c("#4A3722"), width=1)
info = [("18","页成品"),("5","种页面类型"),("2","生成引擎"),("1","套可复现流程")]
for i,(v,k) in enumerate(info):
    x0 = M + i*270
    d.text((x0, H-262), v, font=S(46,"Bold"), fill=c(GOLD))
    d.text((x0, H-200), k, font=S(T4), fill=c("#8A7358"))

# 最底行
d.line([(M, H-120), (W-M, H-120)], fill=c("#2E2318"), width=1)
d.text((M, H-92), "虚构品牌 · 自主命题 · 第一辑", font=S(T4), fill=c("#6E5A42"))
d.text((W-M-70, H-92), "00 / 18", font=S(T4), fill=c("#6E5A42"))

cv.save(os.path.join(OUT,"00-cover.png"))
print("00 作品集封面 done")
