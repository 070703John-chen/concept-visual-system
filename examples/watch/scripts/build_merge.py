# -*- coding: utf-8 -*-
"""11 收回框内（旧版结构）+ 07 合并两版（旧版结构 + 新版圆形/英文块）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw
from kit import S

from cfg import ASSETS as A
from cfg import OUT as OUT
W, H, M = 1200, 1600, 72
BG = "#0E0B08"
FG, SUB, GOLD = "#EFE3CE", "#8A7358", "#C08A4A"
T1, T2, T3, T4 = 72, 26, 16, 12
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
# 11 放大看机芯（旧版结构 + 图收进框内）
# ============================================================
src = op("g-11-detail.jpg", False)
cv = Image.new("RGB",(W,H),c(BG)); d = ImageDraw.Draw(cv)
head(d, "DETAIL", 11)
d.text((M, 92), "放大看机芯", font=S(48,"Bold"), fill=c(FG))
d.text((M, 156), "三个地方值得近看：摆轮、游丝、螺丝。", font=S(T3), fill=c(SUB))

# 图放在内边框里（INSET+20）
MB = [INSET+22, 210, W-INSET-22, 1000]
big = cover(src, MB[2]-MB[0], MB[3]-MB[1], 0.5, 0.5)
cv.paste(big,(MB[0],MB[1]))
d = ImageDraw.Draw(cv)
d.rectangle([MB[0]-1, MB[1]-1, MB[2], MB[3]], outline=(70,52,34), width=2)

def magnify(cf, r, dst):
    s=int(r*2)
    cxp=int(big.width*cf[0]); cyp=int(big.height*cf[1])
    crop=big.crop((cxp-s//2,cyp-s//2,cxp+s//2,cyp+s//2)).resize((dst,dst),Image.LANCZOS)
    mask=Image.new("L",(dst,dst),0); ImageDraw.Draw(mask).ellipse([0,0,dst-1,dst-1],fill=255)
    return crop,mask,(MB[0]+cxp,MB[1]+cyp)

specs=[((0.50,0.24),150,215,"游丝与摆轮","21600 次/小时"),((0.32,0.60),120,192,"红宝石轴承","7 颗 · 设定值")]
dx,dy = MB[2]-24-215, 700
for i,(cf,r,size,t1,t2) in enumerate(specs):
    crop,mask,(cxp,cyp)=magnify(cf,r,size)
    X = dx if i==0 else dx+56
    Y = dy if i==0 else dy+236
    d.line([(cxp,cyp),(X+size//2,Y+size//2)],fill="#5C452C",width=1)
    d.ellipse([cxp-5,cyp-5,cxp+5,cyp+5],outline=c(GOLD),width=2)
    cv.paste(crop,(X,Y),mask); d=ImageDraw.Draw(cv)
    d.ellipse([X,Y,X+size,Y+size],outline=(255,255,255),width=3)
    d.ellipse([X-2,Y-2,X+size+2,Y+size+2],outline=c(GOLD),width=1)
    d.rectangle([X+5, Y+size-44, X+size-5, Y+size-6], fill=(10,8,6))
    d.text((X+13, Y+size-40), t1, font=S(13,"Medium"), fill=c(FG))
    d.text((X+13, Y+size-23), t2, font=S(11), fill=c("#A98C68"))

BY = 1030
d.rectangle([M, BY, W-M, BY+1], fill=c("#4A3722"))
for i,(k,v) in enumerate([("摆轮","决定走时准不准，每秒摆动 6 次"),
                          ("游丝","蓝钢材质，温度变化下走时更稳"),
                          ("螺丝","蓝钢抛光倒角，装配时不留毛刺")]):
    yy = BY+26+i*44
    d.text((M, yy), k, font=S(18,"Medium"), fill=c(GOLD))
    d.text((M+90, yy), v, font=S(18), fill=c(FG))

DY = 1170
d.rectangle([M, DY, W-M, DY+1], fill=c("#4A3722"))
for i,(v,k) in enumerate([("21600","次 / 小时"),("7","颗合成红宝石"),("40","小时动力"),("0","计时按钮")]):
    x0 = M + i*258
    d.text((x0, DY+24), v, font=S(40,"Bold"), fill=c(GOLD))
    d.text((x0, DY+80), k, font=S(T4), fill=c(SUB))

CY2 = DY+150
d.rectangle([M, CY2, W-M, CY2+1], fill=c("#4A3722"))
d.text((M, CY2+24), "能对上账的只有三样", font=S(22,"Medium"), fill=c(FG))
for i, ln in enumerate(["摆轮：每小时 21600 次，直径 8.4 mm",
                        "游丝：蓝钢材质，厚度 0.03 mm；螺丝：抛光倒角，不留毛刺"]):
    d.text((M, CY2+62+i*30), ln, font=S(17), fill=c(SUB))
cv.save(os.path.join(OUT,"11-detail.jpg"), quality=95, optimize=True)
print("11 fixed inside frame")

# ============================================================
# 07 合并版：旧版结构（左图 + 三条引线标注）+ 新版（圆形放大 + 英文块）
# ============================================================
im = op("g-07-tight.jpg", False)
cv = Image.new("RGB",(W,H),c(BG)); d = ImageDraw.Draw(cv)
head(d, "SPECIFICATION", 7)
d.text((M, 92), "三处尺寸，三个特征", font=S(46,"Bold"), fill=c(FG))
d.text((M, 156), "尺寸按实物比例标注；特征是能验证的，不是形容词。", font=S(T3), fill=c(SUB))

# 左：白底图版（收在框内）
LB = [M, 210, M+520, 900]
d.rectangle(LB, fill="#F4F1EA", outline="#3A2C1E", width=1)
pic = contain(im, LB[2]-LB[0]-24, LB[3]-LB[1]-24)
PX = LB[0]+(LB[2]-LB[0]-pic.width)//2
PY = LB[1]+(LB[3]-LB[1]-pic.height)//2
cv.paste(pic,(PX,PY))
d = ImageDraw.Draw(cv)

# 尺寸线（38 / 20）
cx = PX + pic.width//2
diam_y = PY + int(pic.height*0.34)
cw_ = int(pic.width*0.52)
d.line([(cx-cw_//2, diam_y),(cx+cw_//2, diam_y)], fill=c("#8A5A2B"), width=2)
for X,sg in ((cx-cw_//2,1),(cx+cw_//2,-1)):
    d.line([(X,diam_y),(X+12*sg,diam_y-6)], fill=c("#8A5A2B"), width=2)
    d.line([(X,diam_y),(X+12*sg,diam_y+6)], fill=c("#8A5A2B"), width=2)
d.text((cx-26, diam_y+12), "38 mm", font=S(T3,"Medium"), fill=c("#3A2C1E"))

strap_y = PY + int(pic.height*0.86)
sw_ = int(pic.width*0.26)
d.line([(cx-sw_//2, strap_y),(cx+sw_//2, strap_y)], fill=c("#8A5A2B"), width=2)
for X,sg in ((cx-sw_//2,1),(cx+sw_//2,-1)):
    d.line([(X,strap_y),(X+10*sg,strap_y-5)], fill=c("#8A5A2B"), width=2)
    d.line([(X,strap_y),(X+10*sg,strap_y+5)], fill=c("#8A5A2B"), width=2)
d.text((cx-24, strap_y+10), "20 mm", font=S(T3,"Medium"), fill=c("#3A2C1E"))

# 右：文案 + 三条特征（旧版结构）
RX = M+560
d.text((RX, 214), "From the side,", font=S(T2,"Medium"), fill=c(FG))
d.text((RX, 248), "it disappears.", font=S(T2,"Medium"), fill=c(GOLD))
d.text((RX, 296), "38mm 表壳，10.8mm 厚度。", font=S(T3), fill=c(SUB))

feats = [("1","蓝宝石 · 单面防眩","镀膜朝外，内侧不镀。"),
         ("2","镂空表盘 · 摆轮可见","每秒摆 6 次，直接露在盘上。"),
         ("3","头层牛皮 · 双线缝制","20mm 收口，颗粒纹随佩戴变深。")]
fy = 350
for no,t,v in feats:
    d.ellipse([RX, fy+2, RX+22, fy+24], outline=c(GOLD), width=1)
    tw = d.textlength(no, font=S(12,"Bold"))
    d.text((RX+11-tw/2, fy+6), no, font=S(12,"Bold"), fill=c(GOLD))
    d.text((RX+34, fy-2), t, font=S(T3,"Medium"), fill=c(FG))
    d.text((RX+34, fy+26), v, font=S(T4), fill=c(SUB))
    fy += 84

# 新版元素：三个圆形放大（横排，放右下方）
CY = 660
circles = [("g-07-tight.jpg","表盘细节"),("g-08-caseback.jpg","螺旋底盖"),("g-08-side.jpg","表耳收口")]
cs = 128
for i,(f,name) in enumerate(circles):
    i2 = op(f)
    x = RX + i*168
    crop = cover(i2, cs, cs, 0.5, 0.5)
    mask = Image.new("L",(cs,cs),0); ImageDraw.Draw(mask).ellipse([0,0,cs-1,cs-1],fill=255)
    cv.paste(crop,(x,CY),mask)
    d = ImageDraw.Draw(cv)
    d.ellipse([x,CY,x+cs,CY+cs], outline=c(GOLD), width=1)
    d.text((x, CY+cs+8), name, font=S(T4,"Medium"), fill=c(FG))

# 底部：五行参数（旧版精简）
BY = 900
d.rectangle([M, BY, W-M, BY+1], fill=c("#4A3722"))
rows = [("表径","38 mm"),("厚度","10.8 mm"),("表带宽","20 mm"),("重量","68 g"),("防水","5 ATM")]
for i,(k,v) in enumerate(rows):
    x0 = M + i*212
    d.text((x0, BY+24), v, font=S(28,"Medium"), fill=c(FG))
    d.text((x0, BY+64), k, font=S(T4), fill=c(SUB))

# 底部：图标流程条（新版）
SY = 1030
d.rectangle([M, SY, W-M, SY+1], fill=c("#4A3722"))
d.text((M, SY+20), "How it works", font=S(T3,"Medium"), fill=c(SUB))
labels = ["戴上","上链","走时","40 h"]
SW = (W-2*M)//4
for i,lb in enumerate(labels):
    cx0 = M + i*SW + SW//2
    cy0 = SY+110
    r = 30
    d.ellipse([cx0-r, cy0-r, cx0+r, cy0+r], outline=c(GOLD), width=2)
    d.text((cx0-12, cy0+40), lb, font=S(T4), fill=c(FG))
    if i < 3:
        ax = M + (i+1)*SW - 10
        d.line([(ax-24, cy0),(ax-4, cy0)], fill=c("#5C452C"), width=1)
        d.polygon([(ax,cy0),(ax-8,cy0-4),(ax-8,cy0+4)], fill=c("#5C452C"))

d.text((M, SY+180), "设定值，非实测；真实产品须以出厂检测为准。", font=S(T4), fill=c("#6E5A42"))
cv.save(os.path.join(OUT,"07-spec.jpg"), quality=95, optimize=True)
print("07 merged (old structure + new circles)")
