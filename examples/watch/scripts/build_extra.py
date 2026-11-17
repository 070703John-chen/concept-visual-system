# -*- coding: utf-8 -*-
"""新增两页（打破单一）：14 字体与版式 / 15 黑白实验"""
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
def head(d, en, no):
    d.text((M, 44), "GUĀNSHÍ", font=S(19,"Medium"), fill=c(GOLD))
    bw = d.textlength("GUĀNSHÍ", font=S(19,"Medium"))
    d.text((M+bw+4, 39), "™", font=S(10,"Medium"), fill=c(GOLD))
    d.text((M+bw+18, 47), "·  "+en, font=S(T4,"Medium"), fill=c(SUB))
    d.text((W-M-24, 47), f"{no:02d}", font=S(T4,"Medium"), fill=c("#6E5A42"))

# ============================================================
# 14 字体与版式（纯排版页，无产品图）
# ============================================================
cv = Image.new("RGBA",(W,H),(0,0,0,0)); d = ImageDraw.Draw(cv)
head(d, "TYPEFACE", 14)
d.text((M, 92), "字与格", font=S(52,"Bold"), fill=c(FG))
d.text((M, 158), "一套字体，六个字号，一条栅格线。", font=S(T3), fill=c(SUB))

Y = 230
d.rectangle([M, Y, W-M, Y+1], fill=c("#4A3722"))
sizes = [("Aa 观时", 72, "T1 标题"), ("Aa 齿轮不说谎", 40, "T2 副标"),
         ("Aa 38mm 自动上链 40 小时", 26, "T3 正文"), ("Aa 蓝宝石单面防眩 · 头层牛皮", 18, "T4 小字"),
         ("Aa 虚构品牌 · 自主命题", 14, "T5 注")]
yy = Y+34
for txt, sz, label in sizes:
    d.text((M, yy), txt, font=S(sz,"Medium" if sz<40 else "Bold"), fill=c(FG))
    lw = d.textlength(label, font=S(T4))
    d.text((W-M-lw, yy+6), label, font=S(T4), fill=c("#6E5A42"))
    yy += max(sz+26, 54)

Y2 = yy+20
d.rectangle([M, Y2, W-M, Y2+1], fill=c("#4A3722"))
d.text((M, Y2+26), "栅格", font=S(22,"Medium"), fill=c(FG))
# 画栅格：12 列
gx0, gx1 = M, W-M
cols = 12
gap = 12
colw = (gx1-gx0-(cols-1)*gap)//cols
for i in range(cols):
    x = gx0 + i*(colw+gap)
    d.rectangle([x, Y2+70, x+colw, Y2+250], fill=(28,22,17))
    d.text((x, Y2+258), f"{i+1:02d}", font=S(T4), fill=c("#5C452C"))
d.text((M, Y2+292), "12 列 · 列宽 78 · 间距 12 · 左右边距 72 —— 所有页面都按这条线排。", font=S(T3), fill=c(SUB))

Y3 = Y2+340
d.rectangle([M, Y3, W-M, Y3+1], fill=c("#4A3722"))
d.text((M, Y3+26), "为什么只用一种字体", font=S(22,"Medium"), fill=c(FG))
for i, ln in enumerate(["混排三种字体，看起来是三个人做的。",
                        "一种字体，靠字号、字重、字距分出层次，才像一个人做的。",
                        "这条规矩比任何一张效果图都更能说明“专业”。"]):
    d.text((M, Y3+68+i*32), ln, font=S(17), fill=c(SUB))

# 底部：字距／字重演示
Y4 = Y3+200
d.text((M, Y4), "字距", font=S(T4), fill=c("#6E5A42"))
d.text((M+60, Y4-10), "G U Ā N S H Í", font=S(30,"Medium"), fill=c(GOLD))
d.text((M+400, Y4), "英文品牌行统一 +8% 字距", font=S(T3), fill=c(SUB))
cv.save(os.path.join(OUT,"14-typography.png"))
print("14 typography done")

# ============================================================
# 15 黑白实验（把现有图做单色，制造视觉变化）
# ============================================================
def mono(path, warm=True):
    im = Image.open(os.path.join(A,path)).convert("RGB")
    w,h = im.size
    im = im.crop((int(w*0.03), int(h*0.06), int(w*0.96), int(h*0.94)))
    g = np.asarray(im.convert("L")).astype(np.float32)/255.0
    g = np.clip((g-0.03)/0.93, 0, 1)**0.95
    if warm:
        tint = np.array([1.02, 0.97, 0.90])
    else:
        tint = np.array([0.94, 0.97, 1.02])
    a = np.stack([g*tint[0], g*tint[1], g*tint[2]], axis=2)
    rng = np.random.default_rng(9)
    a = a + rng.normal(0, 0.012, (a.shape[0], a.shape[1], 1))
    return Image.fromarray(np.clip(a*255,0,255).astype(np.uint8))

cv = Image.new("RGBA",(W,H),(0,0,0,0)); d = ImageDraw.Draw(cv)
head(d, "MONOCHROME", 15)
d.text((M, 92), "黑白", font=S(52,"Bold"), fill=c(FG))
d.text((M, 158), "三张原图 · 单色处理 · 同一套调色参数", font=S(T3), fill=c(SUB))

top = mono("g-03-hero.jpg", True)
bot1 = mono("g-11-detail.jpg", False)
bot2 = mono("g-s1-cabin.jpg", True)

def cov(im,w,h,ax=0.5,ay=0.5):
    sc=max(w/im.width,h/im.height)
    im2=im.resize((int(im.width*sc)+1,int(im.height*sc)+1),Image.LANCZOS)
    x=int((im2.width-w)*ax); y=int((im2.height-h)*ay)
    return im2.crop((x,y,x+w,y+h))

Y=210
cv.paste(cov(top, W-2*M, 520, 0.5, 0.45), (M, Y))
cv.paste(cov(bot1, (W-2*M-12)//2, 380, 0.5, 0.5), (M, Y+532))
cv.paste(cov(bot2, (W-2*M-12)//2, 380, 0.5, 0.5), (M+(W-2*M-12)//2+12, Y+532))
d = ImageDraw.Draw(cv)
d.text((M+14, Y+520-34), "整表 · 明暗关系", font=S(T4,"Medium"), fill=c("#C9B393"))
d.text((M+14, Y+532+380-34), "机芯 · 冷调", font=S(T4,"Medium"), fill=c("#A98C68"))
d.text((M+(W-2*M-12)//2+26, Y+532+380-34), "木屋 · 暖调", font=S(T4,"Medium"), fill=c("#C9B393"))

BY = Y+532+380+46
d.rectangle([M, BY, W-M, BY+1], fill=c("#4A3722"))
d.text((M, BY+26), "单色处理参数", font=S(22,"Medium"), fill=c(FG))
for i, ln in enumerate(["亮度归一：黑位 3%、高光 97%，与全站调色一致。",
                        "冷暖分离：暖调 +6% 红、冷调 +10% 蓝，只保留明暗关系。",
                        "依据：同一批素材，同一套调色参数，未做局部修饰。" ]):
    d.text((M, BY+68+i*32), ln, font=S(17), fill=c(SUB))

CY = BY+200
d.rectangle([M, CY, W-M, CY+1], fill=c("#4A3722"))
for i,(v,k) in enumerate([("1","页黑白"),("2","种色调（暖/冷）"),("0","个彩色元素")]):
    x0 = M + i*300
    d.text((x0, CY+24), v, font=S(40,"Bold"), fill=c(GOLD))
    d.text((x0, CY+80), k, font=S(T4), fill=c(SUB))
cv.save(os.path.join(OUT,"15-mono.png"))
print("15 mono done")
