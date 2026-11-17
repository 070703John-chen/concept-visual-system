# -*- coding: utf-8 -*-
"""修正 04（去整表，改全细节/结构）+ 重建 11（双放大圆，暗底框内）+ 新增 14（六元素页）"""
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
T1, T2, T3, T4 = 56, 24, 16, 12
INSET = 34

def c(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def op(n, trim=True):
    im = Image.open(os.path.join(A,n)).convert("RGB")
    if trim:
        w,h = im.size
        im = im.crop((int(w*0.03), int(h*0.13), int(w*0.93), int(h*0.90)))
    return im
def cover(im,w,h,ax=0.5,ay=0.5):
    sc=max(w/im.width,h/im.height)
    im2=im.resize((int(im.width*sc)+1,int(im.height*sc)+1),Image.LANCZOS)
    x=int((im2.width-w)*ax); y=int((im2.height-h)*ay)
    return im2.crop((x,y,x+w,y+h))
def contain(im,w,h):
    sc=min(w/im.width,h/im.height)
    return im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
def head(d, en, no):
    d.text((M, 44), "GUĀNSHÍ", font=S(19,"Medium"), fill=c(GOLD))
    bw = d.textlength("GUĀNSHÍ", font=S(19,"Medium"))
    d.text((M+bw+4, 39), "™", font=S(10,"Medium"), fill=c(GOLD))
    d.text((M+bw+18, 47), "·  "+en, font=S(T4,"Medium"), fill=c(SUB))
    d.text((W-M-24, 47), f"{no:02d}", font=S(T4,"Medium"), fill=c("#6E5A42"))

# ============================================================
# 04 皮与钢：3 工艺 + 3 结构（去掉整表）
# ============================================================
cv = Image.new("RGB",(W,H),c(BG)); d = ImageDraw.Draw(cv)
head(d, "MATERIAL & CRAFT", 4)
d.text((M, 84), "材料与工艺", font=S(46,"Bold"), fill=c(FG))

d.text((M, 152), "表带 20 mm · 壳 38 mm · 厚 10.8 mm · 重 68 g", font=S(19,"Medium"), fill=c("#C9B393"))


GW = (W-2*M-2*12)//3
GH = 250
Y = 216
row1 = [("g-s6-leather.jpg","马鞍针 · 两根线交叉"),("g-04-buckle.jpg","316L 针扣"),("g-08-crown.jpg","滚花表冠")]
for i,(f,cap) in enumerate(row1):
    im = op(f, False)
    x = M + i*(GW+12)
    cv.paste(cover(im, GW, GH, 0.5, 0.45), (x, Y))
    d = ImageDraw.Draw(cv)
    d.text((x, Y+GH+8), cap, font=S(T4,"Medium"), fill=c("#C9B393"))

Y2 = Y + GH + 54
GH2 = 300
row2 = [("g-11-detail.jpg","摆轮与宝石轴承"),("g-05-exploded.jpg","机芯分层 · 五部件"),("g-08-caseback.jpg","底盖 · 螺旋透视")]
def op2(n):
    im = Image.open(os.path.join(A,n)).convert("RGB")
    w,h = im.size
    return im.crop((int(w*0.06), int(h*0.16), int(w*0.90), int(h*0.86)))
for i,(f,cap) in enumerate(row2):
    im = op2(f)
    x = M + i*(GW+12)
    box = [x, Y2, x+GW, Y2+GH2]
    d.rectangle(box, fill="#0B0A08")
    pic = contain(im, GW-10, GH2-10)
    cv.paste(pic, (x+(GW-pic.width)//2, Y2+(GH2-pic.height)//2))
    d = ImageDraw.Draw(cv)
    d.text((x, Y2+GH2+8), cap, font=S(T4,"Medium"), fill=c("#C9B393"))

BY = Y2 + GH2 + 30
d.rectangle([M, BY, W-M, BY+1], fill=c("#4A3722"))

# 材料事实（可核，不编产地）
d.text((M, BY+20), "材料", font=S(T4,"Medium"), fill=c(SUB))
mat = [("头层牛皮", "1.2 mm · 深棕"), ("316L 不锈钢", "拉丝 · 针扣 20 mm"), ("蓝宝石", "单面镀膜 · 厚 1.1 mm")]
for i,(a,b) in enumerate(mat):
    x0 = M + i*330
    d.text((x0, BY+44), a, font=S(17,"Medium"), fill=c(FG))
    d.text((x0, BY+70), b, font=S(13), fill=c("#A98C68"))

# 工序三步（具体怎么做）
SY = BY + 104
d.text((M, SY), "工序 · 表带三步", font=S(T4,"Medium"), fill=c(SUB))
steps = [("01","裁切","按 20 mm 裁条，边缘削薄到 0.8 mm 再对折"),
         ("02","打孔","菱锥每 4 mm 一孔，两排错开 2 mm"),
         ("03","马鞍缝","两线同向穿，每针回拉锁死；断一处仍锁住")]
cw = (W-2*M-24)//3
for i,(no,title,desc) in enumerate(steps):
    x0 = M + i*(cw+12)
    d.text((x0, SY+26), no, font=S(20,"Bold"), fill=c(GOLD))
    d.text((x0+36, SY+29), title, font=S(18,"Medium"), fill=c(FG))
    cur=""; yy=SY+60
    for ch in desc:
        if d.textlength(cur+ch, font=S(13)) > cw-8 and ch not in "，。；":
            d.text((x0, yy), cur, font=S(13), fill=c("#A98C68")); yy+=20; cur=ch
        else:
            cur+=ch
    if cur: d.text((x0, yy), cur, font=S(13), fill=c("#A98C68"))
    if i < 2:
        d.text((x0+cw-4, SY+30), "→", font=S(15), fill=c("#5C452C"))

d.text((M, SY+120), "依据：材料与工艺为方案设定值，非实测", font=S(T4), fill=c("#6E5A42"))
cv.save(os.path.join(OUT,"04-material.jpg"), quality=95, optimize=True)
print("04 rebuilt (no whole watch)")

# ============================================================
# 11 放大看机芯：双放大圆（暗底，框内）
# ============================================================
src = op("g-11-detail.jpg", False)
cv = Image.new("RGB",(W,H),c(BG)); d = ImageDraw.Draw(cv)
head(d, "DETAIL", 11)
d.text((M, 92), "放大看机芯", font=S(48,"Bold"), fill=c(FG))
d.text((M, 156), "三个地方值得近看：摆轮、游丝、螺丝。", font=S(T3), fill=c(SUB))

MB = [INSET+16, 210, W-INSET-16, 980]
big = cover(src, MB[2]-MB[0], MB[3]-MB[1], 0.5, 0.5)
cv.paste(big,(MB[0],MB[1]))
d = ImageDraw.Draw(cv)
d.rectangle([MB[0],MB[1],MB[2],MB[3]], outline=(58,42,28), width=1)

def magnify(cf, r, dst):
    s=int(r*2)
    cxp=int(big.width*cf[0]); cyp=int(big.height*cf[1])
    crop=big.crop((cxp-s//2,cyp-s//2,cxp+s//2,cyp+s//2)).resize((dst,dst),Image.LANCZOS)
    mask=Image.new("L",(dst,dst),0); ImageDraw.Draw(mask).ellipse([0,0,dst-1,dst-1],fill=255)
    return crop,mask,(MB[0]+cxp,MB[1]+cyp)

specs=[((0.50,0.26),150,220,"游丝与摆轮","21600 次/小时"),((0.30,0.62),120,196,"红宝石轴承","7 颗 · 设定值")]
dx,dy = W-INSET-24-220, 660
for i,(cf,r,size,t1,t2) in enumerate(specs):
    crop,mask,(cxp,cyp)=magnify(cf,r,size)
    X = dx if i==0 else dx+70
    Y = dy if i==0 else dy+240
    d.line([(cxp,cyp),(X+size//2,Y+size//2)],fill="#5C452C",width=1)
    d.ellipse([cxp-5,cyp-5,cxp+5,cyp+5],outline=c(GOLD),width=2)
    cv.paste(crop,(X,Y),mask); d=ImageDraw.Draw(cv)
    d.ellipse([X,Y,X+size,Y+size],outline=(255,255,255),width=3)
    d.ellipse([X-2,Y-2,X+size+2,Y+size+2],outline=c(GOLD),width=1)
    d.rectangle([X+6, Y+size-46, X+size-6, Y+size-8], fill=(10,8,6))
    d.text((X+14, Y+size-42), t1, font=S(14,"Medium"), fill=FG_col if False else c(FG))
    d.text((X+14, Y+size-25), t2, font=S(11), fill=c("#A98C68"))

BY = 1010
d.rectangle([M, BY, W-M, BY+1], fill=c("#4A3722"))
for i,(k,v) in enumerate([("摆轮","决定走时准不准，每秒摆动 6 次"),
                          ("游丝","蓝钢材质，温度变化下走时更稳"),
                          ("螺丝","蓝钢抛光倒角，装配时不留毛刺")]):
    yy = BY+26+i*44
    d.text((M, yy), k, font=S(18,"Medium"), fill=c(GOLD))
    d.text((M+90, yy), v, font=S(18), fill=c(FG))

DY = 1150
d.rectangle([M, DY, W-M, DY+1], fill=c("#4A3722"))
for i,(v,k) in enumerate([("21600","次 / 小时"),("7","颗合成红宝石"),("40","小时动力"),("0","计时按钮")]):
    x0 = M + i*258
    d.text((x0, DY+24), v, font=S(40,"Bold"), fill=c(GOLD))
    d.text((x0, DY+80), k, font=S(T4), fill=c(SUB))
d.text((M, DY+124), "以上为方案设定值，非实测。", font=S(T4), fill=c("#6E5A42"))

CY2 = DY+180
d.rectangle([M, CY2, W-M, CY2+1], fill=c("#4A3722"))
d.text((M, CY2+24), "能对上账的只有三样", font=S(22,"Medium"), fill=c(FG))
for i, ln in enumerate(["摆轮：每小时 21600 次，直径 8.4 mm",
                        "游丝：蓝钢材质，厚度 0.03 mm；螺丝：抛光倒角，不留毛刺"]):
    d.text((M, CY2+62+i*30), ln, font=S(17), fill=c(SUB))
cv.save(os.path.join(OUT,"11-detail.jpg"), quality=95, optimize=True)
print("11 rebuilt (double magnifier)")
