# -*- coding: utf-8 -*-
"""把新的 7 张图分配进页面：04 换皮革裁切 / 10 场景重做 / 新增「夜里的三种光」"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw
from kit import S

from cfg import ASSETS as A
from cfg import OUT as OUT
W, H, M = 1200, 1600, 60
BG = "#0E0B08"
FG, SUB, GOLD, AMBER = "#EFE3CE", "#8A7358", "#C08A4A", "#FF9E4D"

def c(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0,2,4))
def op(n, trim=False):
    im = Image.open(os.path.join(A, n)).convert("RGB")
    if trim:
        w,h = im.size
        im = im.crop((int(w*0.02), int(h*0.03), int(w*0.97), int(h*0.95)))
    return im
def fit(im, w, h, ax=0.5, ay=0.5):
    sc = max(w/im.width, h/im.height)
    im2 = im.resize((int(im.width*sc)+1, int(im.height*sc)+1), Image.LANCZOS)
    x=int((im2.width-w)*ax); y=int((im2.height-h)*ay)
    return im2.crop((x,y,x+w,y+h))
def cut(im, r, tw, th, ax=0.5, ay=0.5):
    x0,y0,x1,y1 = r
    return fit(im.crop((int(im.width*x0),int(im.height*y0),int(im.width*x1),int(im.height*y1))), tw, th, ax, ay)
def head(d, en, cn, sub):
    d.text((M, 44), "GUĀNSHÍ", font=S(19,"Medium"), fill=c(GOLD))
    bw = d.textlength("GUĀNSHÍ", font=S(19,"Medium"))
    d.text((M+bw+4, 39), "™", font=S(10,"Medium"), fill=c(GOLD))
    d.text((M+bw+18, 47), "·  "+en, font=S(12,"Medium"), fill=c(SUB))
    d.text((M, 88), cn, font=S(46,"Bold"), fill=c(FG))
    d.text((M, 148), sub, font=S(18), fill=c(SUB))
    d.rectangle([M, 196, W-M, 197], fill=c("#4A3722"))
def cap(d, x, y, t, size=14):
    tw = d.textlength(t, font=S(size))
    d.rectangle([x, y, x+tw+20, y+28], fill=(12,9,7))
    d.text((x+10, y+5), t, font=S(size), fill=c("#EFE3CE"))
def foot(d, no):
    d.text((M, H-38), "虚构品牌 · 自主命题", font=S(12), fill=c("#6E5A42"))
    d.text((W-M-48, H-38), f"{no:02d} / 13", font=S(13), fill=c("#6E5A42"))

# ---------- 10 场景重做（手腕调表带 / 帐篷 / 雪窗）----------
hand = op("g-s7-hand.jpg"); tent = op("g-s3-tent.jpg"); snow = op("g-s5-snow.jpg")
cv = Image.new("RGB", (W, H), c(BG)); d = ImageDraw.Draw(cv)
head(d, "IN USE", "它在哪", "三个真实场景：手腕上、山里的夜、结霜的窗。")

Y = 216
cv.paste(fit(hand, 520, 470, 0.5, 0.45), (M, Y))
cv.paste(cut(tent, (0.02,0.10,0.98,0.95), 520, 226), (M+532, Y))
cv.paste(cut(snow, (0.02,0.10,0.98,0.95), 520, 232), (M+532, Y+238))
d = ImageDraw.Draw(cv)
cap(d, M+14, Y+470-38, "01 · 出门前调一格")
cap(d, M+546, Y+226-36, "02 · 山里，帐篷亮着", 13)
cap(d, M+546, Y+238+232-36, "03 · 窗上结霜，它在窗台", 13)

TY = Y+512
d.rectangle([M, TY, W-M, TY+1], fill=c("#4A3722"))
for i,(k,v) in enumerate([("手腕","表带调紧一格，跑步时不打手腕"),
                          ("夜宿","摘下放在帐篷外的石头上，回头看还在"),
                          ("冬天","进屋先不摘，让它在窗台上回温")]):
    yy = TY+28+i*46
    d.text((M, yy), k, font=S(19,"Medium"), fill=c(GOLD))
    d.text((M+90, yy), v, font=S(18), fill=c(FG))

BY2 = TY+200
d.rectangle([M, BY2, W-M, BY2+1], fill=c("#4A3722"))
d.text((M, BY2+26), "一句话收口", font=S(22,"Medium"), fill=c(FG))
d.text((M, BY2+70), "好表的标准不是“戴上像成功人士”，是“戴上之后忘了它”。", font=S(20), fill=c(SUB))

SY2 = BY2+150
d.rectangle([M, SY2, W-M, SY2+1], fill=c("#4A3722"))
for i,(v,k) in enumerate([("12","小时 / 天 佩戴"),("40","小时 动力储备"),("0.5","秒 / 日 误差区间"),("19","cm 以下 手腕")]):
    x0 = M + i*258
    d.text((x0, SY2+26), v, font=S(40,"Bold"), fill=c(GOLD))
    d.text((x0, SY2+82), k, font=S(14), fill=c(SUB))
d.text((M, SY2+134), "误差区间与佩戴时长为方案设定值，非实测。", font=S(13), fill=c("#6E5A42"))
foot(d, 10)
cv.save(os.path.join(OUT, "10-scenes.jpg"), quality=95, optimize=True)
print("10 rebuilt")

# ---------- 13 夜里的三种光（新页）----------
cabin = op("g-s1-cabin.jpg"); sea = op("g-s4-sea.jpg"); ice = op("g-o6-ice.jpg")
cv = Image.new("RGB", (W, H), c(BG)); d = ImageDraw.Draw(cv)
head(d, "NIGHT", "夜里的三种光", "窗光、火光、冰光 —— 它都见过。")

Y = 216
cv.paste(fit(cabin, W-2*M, 560, 0.5, 0.42), (M, Y))
d = ImageDraw.Draw(cv)
cap(d, M+14, Y+560-38, "木屋 · 窗光")
cv.paste(cut(sea, (0.02,0.12,0.98,0.92), 520, 360), (M, Y+576))
cv.paste(cut(ice, (0.02,0.12,0.98,0.92), 520, 360), (M+532, Y+576))
d = ImageDraw.Draw(cv)
cap(d, M+14, Y+576+360-38, "海边 · 火光", 13)
cap(d, M+546, Y+576+360-38, "薄冰 · 冰光", 13)

TY = Y+576+360+46
d.rectangle([M, TY, W-M, TY+1], fill=c("#4A3722"))
d.text((M, TY+28), "三个色温，同一块壳", font=S(22,"Medium"), fill=c(FG))
for i, ln in enumerate(["窗光 5600 K（散光）· 火光 1800 K（点光）· 冰光 8000 K（反射光）",
                        "色温越低，金属越偏暖；越高，镀层越显蓝。三张用同一套调色参数。"]):
    d.text((M, TY+70+i*32), ln, font=S(17), fill=c(SUB))

BY = TY+196
d.rectangle([M, BY, W-M, BY+1], fill=c("#4A3722"))
for i,(v,k) in enumerate([("3","种光源"),("0","次换电池"),("40","小时 走时"),("68","克")]):
    x0 = M + i*258
    d.text((x0, BY+26), v, font=S(40,"Bold"), fill=c(GOLD))
    d.text((x0, BY+82), k, font=S(14), fill=c(SUB))
d.text((M, BY+140), "夜拍图为概念演绎，非产品图。", font=S(13), fill=c("#6E5A42"))
foot(d, 13)
cv.save(os.path.join(OUT, "13-night.jpg"), quality=95, optimize=True)
print("13 night done")
