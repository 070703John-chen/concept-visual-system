# -*- coding: utf-8 -*-
"""按拆解规则重做 03 Hero / 08 Feature
规则：一页一种类型 / 四档字号 72-26-16-12 / 文字≤480压在暗区 / 句式=部位+动词+结果
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw
from kit import S

from cfg import ASSETS as A
from cfg import OUT as OUT
W, H = 1200, 1600
BG = "#0E0B08"
FG, SUB, GOLD = "#EFE3CE", "#8A7358", "#C08A4A"

# 四档字号
T1, T2, T3, T4 = 72, 26, 16, 12

def c(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def op(n):
    im = Image.open(os.path.join(A,n)).convert("RGB")
    w,h = im.size
    return im.crop((int(w*0.02), int(h*0.04), int(w*0.96), int(h*0.94)))
def cover(im,w,h,ax=0.5,ay=0.5):
    sc=max(w/im.width,h/im.height)
    im2=im.resize((int(im.width*sc)+1,int(im.height*sc)+1),Image.LANCZOS)
    x=int((im2.width-w)*ax); y=int((im2.height-h)*ay)
    return im2.crop((x,y,x+w,y+h))
def scrim_left(cv, w, h, amax=205):
    """左侧压暗，给文字留空区"""
    m = Image.new("L",(w,1))
    for x in range(w):
        t = x/(w-1)
        m.putpixel((x,0), int(amax*max(0,(1-t))**1.25))
    cv.paste(Image.new("RGB",(w,h),(8,6,4)),(0,0),m.resize((w,h)))

# ================= 03 Hero =================
img = op("g-03-hero.jpg")
cv = cover(img, W, H, 0.52, 0.42)
scrim_left(cv, 760, H, 200)
# 顶部也压一点，给品牌行
m2 = Image.new("L",(1,240))
for i in range(240): m2.putpixel((0,i), int(150*(1-i/239)))
cv.paste(Image.new("RGB",(W,240),(8,6,4)),(0,0),m2.resize((W,240)))
d = ImageDraw.Draw(cv)

d.text((72, 56), "GUĀNSHÍ", font=S(19,"Medium"), fill=c(GOLD))
bw = d.textlength("GUĀNSHÍ", font=S(19,"Medium"))
d.text((72+bw+4, 51), "™", font=S(10,"Medium"), fill=c(GOLD))
d.text((72+bw+18, 59), "·  KEY VISUAL", font=S(T4,"Medium"), fill=c(SUB))

# 标题压在左侧暗区，宽度 ≤480
d.text((72, 470), "齿轮", font=S(T1,"Bold"), fill=c(FG))
d.text((72, 556), "不说谎", font=S(T1,"Bold"), fill=c(GOLD))
d.text((72, 668), "镂空不是设计，是把机芯放在你眼前。", font=S(T3), fill=c("#C9B393"))

# 右下角只留一行品牌注
d.text((W-72-214, H-64), "001 · 黑钢镂空 38mm", font=S(T4,"Medium"), fill=c("#8A7358"))
cv.save(os.path.join(OUT, "03-keyvisual.jpg"), quality=95, optimize=True)
print("03 hero rebuilt")

# ================= 08 Feature =================
img2 = op("g-08-side.jpg")
cv2 = cover(img2, W, H, 0.5, 0.45)
# 右侧压暗（文字放右边暗区）
m3 = Image.new("L", (620,1))
for x in range(620):
    t = x/619
    m3.putpixel((x,0), int(210*(t**1.3)))
panel = m3.resize((620,H))
cv2.paste(Image.new("RGB",(620,H),(8,6,4)),(W-620,0),panel)
# 顶部压暗给品牌行
m4 = Image.new("L",(1,200))
for i in range(200): m4.putpixel((0,i), int(140*(1-i/199)))
cv2.paste(Image.new("RGB",(W,200),(8,6,4)),(0,0),m4.resize((W,200)))
d = ImageDraw.Draw(cv2)

d.text((72, 52), "GUĀNSHÍ", font=S(19,"Medium"), fill=c(GOLD))
bw = d.textlength("GUĀNSHÍ", font=S(19,"Medium"))
d.text((72+bw+4, 47), "™", font=S(10,"Medium"), fill=c(GOLD))
d.text((72+bw+18, 55), "·  PROFILE", font=S(T4,"Medium"), fill=c(SUB))

TX = W - 72 - 480   # 文字块宽 480，右对齐到安全边
d.text((TX, 560), "10.8", font=S(T1,"Bold"), fill=c(GOLD))
bw2 = d.textlength("10.8", font=S(T1,"Bold"))
d.text((TX+bw2+12, 600), "mm", font=S(T2,"Medium"), fill=c(FG))

# 句式：部位 + 动词 + 结果
body = ["滑进袖口时，差的不是 0.2 毫米，",
        "是每天多顶一次的那一下。"]
yy = 700
for ln in body:
    d.text((TX, yy), ln, font=S(T2), fill=c("#DCC7A8"))
    yy += 44

d.text((TX, 820), "Side wall brushed, chamfer polished, one crown.", font=S(T3), fill=c(SUB))

# 右下规格（小字，一行）
d.text((TX, H-120), "10.8 mm　·　20 mm　·　38 mm　·　68 g", font=S(T3), fill=c("#A98C68"))
d.text((TX, H-84), "下一版会给真实厚度与实测重量", font=S(T4), fill=c("#6E5A42"))

cv2.save(os.path.join(OUT, "08-profile.jpg"), quality=95, optimize=True)
print("08 feature rebuilt")
