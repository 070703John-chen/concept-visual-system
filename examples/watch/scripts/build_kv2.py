# -*- coding: utf-8 -*-
"""03 主视觉 · 加倒影 + 光效 + 装饰边框（对照散热器/打火机那套手法）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from kit import S

from cfg import ASSETS as A
from cfg import OUT as OUT
W, H, M = 1200, 1600, 72
BG = "#0E0B08"
FG, SUB, GOLD = "#EFE3CE", "#8A7358", "#C08A4A"
T1, T2, T3, T4 = 72, 26, 16, 12

def c(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def op(n, trim=True):
    im = Image.open(os.path.join(A,n)).convert("RGB")
    if trim:
        w,h = im.size
        im = im.crop((int(w*0.03), int(h*0.12), int(w*0.94), int(h*0.90)))
    return im
def contain(im,w,h):
    sc=min(w/im.width,h/im.height)
    return im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)

cv = Image.new("RGB",(W,H),c(BG))

# ---------- 背景光效：中央暖光晕 ----------
glow = Image.new("L",(W,H),0)
gd = ImageDraw.Draw(glow)
gd.ellipse([W*0.10, H*0.18, W*0.90, H*0.72], fill=52)
glow = glow.filter(ImageFilter.GaussianBlur(220))
cv.paste(Image.new("RGB",(W,H),(96,62,32)),(0,0),glow)

d = ImageDraw.Draw(cv)

# ---------- 装饰角线 ----------
cw = 46
for (x,y,sx,sy) in [(M,240,1,1),(W-M,240,-1,1),(M,H-220,1,-1),(W-M,H-220,-1,-1)]:
    d.line([(x,y),(x+sx*cw,y)], fill=c("#5C452C"), width=1)
    d.line([(x,y),(x,y+sy*cw)], fill=c("#5C452C"), width=1)

# ---------- 产品 + 倒影 ----------
prod = op("g-03-hero.jpg")
PW, PH = 940, 640
pic = contain(prod, PW, PH)
PX = (W-pic.width)//2
PY = 300
cv.paste(pic,(PX,PY))

# 倒影：取产品图底部一条，翻转 → 模糊 → 渐隐
RH = 200
ref_src = pic.crop((0, max(0,pic.height-RH), pic.width, pic.height))
ref = ref_src.transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(3.0))
mask = Image.new("L",(ref.width, ref.height), 0)
md = ImageDraw.Draw(mask)
for i in range(ref.height):
    a = int(115*(1-i/(ref.height-1))**1.9)
    md.line([(0,i),(ref.width,i)], fill=a)
cv.paste(ref, (PX, PY+pic.height), mask)

# 接缝处一条极窄压暗，避免硬边
seam = Image.new("L",(1,60))
for i in range(60):
    v = 255-int(200*(1-abs(i-30)/30))
    seam.putpixel((0,i), max(0,v))
cv.paste(Image.new("RGB",(W,60),c(BG)),(0,PY+pic.height-30), seam.resize((W,60)))

d = ImageDraw.Draw(cv)

# ---------- 页头 ----------
d.text((M, 44), "GUĀNSHÍ", font=S(19,"Medium"), fill=c(GOLD))
bw = d.textlength("GUĀNSHÍ", font=S(19,"Medium"))
d.text((M+bw+4, 39), "™", font=S(10,"Medium"), fill=c(GOLD))
d.text((M+bw+18, 47), "·  KEY VISUAL", font=S(T4,"Medium"), fill=c(SUB))
d.text((W-M-24, 47), "03", font=S(T4,"Medium"), fill=c("#6E5A42"))

# ---------- 标题（图上暗区，不压产品） ----------
d.text((M, 120), "镂空：把三处露出来", font=S(50,"Bold"), fill=c(FG))
d.text((M, 186), "去掉约 62% 的盘面遮挡，摆轮、游丝、擒纵叉可直接目视。", font=S(T3), fill=c("#C9B393"))
d.text((M, 214), "依据：盘面开孔面积按设计稿测算，非实测。", font=S(T4), fill=c("#8A7358"))

# ---------- 底部：三处标注 + 规格 ----------
BY = H-190
d.rectangle([M, BY, W-M, BY+1], fill=c("#4A3722"))
notes = [("Skeleton dial","镂空盘 · 摆轮直视"),("Sandwich case","壳带一体收口"),("38 mm","表径 38 · 厚 10.8")]
for i,(en,cn) in enumerate(notes):
    x0 = M + i*360
    d.text((x0, BY+26), en, font=S(T3,"Medium"), fill=c(GOLD))
    d.text((x0, BY+54), cn, font=S(T4), fill=c(SUB))

d.text((M, H-70), "38 mm　·　10.8 mm　·　40 h　·　68 g　·　5 ATM", font=S(T4), fill=c("#8A7358"))
cv.save(os.path.join(OUT,"03-keyvisual.jpg"), quality=95, optimize=True)
print("03 with reflection + glow")
