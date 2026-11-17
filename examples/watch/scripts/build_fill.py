# -*- coding: utf-8 -*-
"""补齐 08 侧面 / 10 场景 / 12 封底，并换 05 用新的分解图"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw
from kit import S, rgb

from cfg import ASSETS as A
from cfg import OUT as OUT
W, H, M = 1200, 1600, 60
PAPER = "#0E0B08"
INK, SUB, GOLD = "#EFE3CE", "#8A7358", "#C08A4A"
DARK = "#0E0B08"

def op(name, trim=True):
    im = Image.open(os.path.join(A, name)).convert("RGB")
    if trim:
        w,h = im.size
        im = im.crop((int(w*0.02), int(h*0.04), int(w*0.96), int(h*0.94)))
    return im

def fit(im, w, h, ax=0.5, ay=0.5):
    sc = max(w/im.width, h/im.height)
    im2 = im.resize((int(im.width*sc)+1, int(im.height*sc)+1), Image.LANCZOS)
    x=int((im2.width-w)*ax); y=int((im2.height-h)*ay)
    return im2.crop((x,y,x+w,y+h))

def boxcut(im, r, tw, th, ax=0.5, ay=0.5):
    x0,y0,x1,y1 = r
    c = im.crop((int(im.width*x0), int(im.height*y0), int(im.width*x1), int(im.height*y1)))
    return fit(c, tw, th, ax, ay)

def cap(d, x, y, t, size=14):
    tw = d.textlength(t, font=S(size))
    d.rectangle([x, y, x+tw+20, y+28], fill=(18,14,10))
    d.text((x+10, y+5), t, font=S(size), fill=rgb("#EFE3CE"))

def head(d, en, cn, sub):
    d.text((M, 44), "GUĀNSHÍ", font=S(19, "Medium"), fill=rgb(GOLD))
    bw = d.textlength("GUĀNSHÍ", font=S(19, "Medium"))
    d.text((M+bw+4, 39), "™", font=S(10, "Medium"), fill=rgb(GOLD))
    d.text((M+bw+18, 47), "·  " + en, font=S(12, "Medium"), fill=rgb(SUB))
    d.text((M, 88), cn, font=S(46, "Bold"), fill=rgb(INK))
    d.text((M, 148), sub, font=S(18), fill=rgb(SUB))
    d.rectangle([M, 196, W-M, 197], fill=rgb("#2E2318"))

# ================= 08 侧面 =================
side = op("g-08-side.jpg"); crown = op("g-08-crown.jpg"); roll = op("g-12-leather-roll.jpg")
cv = Image.new("RGB", (W, H), rgb(PAPER)); d = ImageDraw.Draw(cv)
head(d, "PROFILE", "厚度", "机芯 4.6 + 壳壁 1.8 + 盘面 0.6 + 底盖 3.8 = 10.8 mm")

cv.paste(fit(side, W-2*M, 470), (M, 210)); d = ImageDraw.Draw(cv)
cap(d, M+14, 210+470-38, "10.8mm · 侧壁拉丝 · 抛光倒角")

Y1 = 700
w2 = (W-2*M-14)//2
cv.paste(boxcut(crown, (0.05,0.10,0.95,0.90), w2, 300), (M, Y1))
cv.paste(boxcut(roll,  (0.05,0.10,0.95,0.90), w2, 300), (M+w2+14, Y1))
d = ImageDraw.Draw(cv)
cap(d, M+14, Y1+300-38, "滚花表冠 · 单表冠")
cap(d, M+w2+28, Y1+300-38, "皮革厚度 · 可卷")

TY = Y1+340
d.rectangle([M, TY, W-M, TY+1], fill=rgb("#2E2318"))
d.text((M, TY+26), "厚度怎么定：三个数卡出来", font=S(22, "Medium"), fill=rgb(INK))
for i, ln in enumerate(["袖口内径 42 mm：超过这个数，抬腕会卡一次。",
                        "机芯 4.6 mm + 壳壁 1.8 mm + 盘面 0.6 mm + 底盖 3.8 mm = 10.8 mm。",
                        "每减 1 mm，机芯可用的摆轮直径少 0.3 mm —— 所以停在 10.8。"]):
    d.text((M, TY+68+i*30), ln, font=S(17), fill=rgb(SUB))

SY = TY+190
d.rectangle([M, SY, W-M, SY+1], fill=rgb("#2E2318"))
for i,(v,k) in enumerate([("10.8","毫米 厚度"),("20","毫米 表带"),("38","毫米 表径"),("68","克 重量")]):
    x0 = M + i*258
    d.text((x0, SY+26), v, font=S(42, "Bold"), fill=rgb(GOLD))
    d.text((x0, SY+84), k, font=S(14), fill=rgb(SUB))

d.text((M, H-38), "虚构品牌 · 自主命题", font=S(12), fill=rgb("#6E5A42"))
d.text((W-M-48, H-38), "08 / 12", font=S(13), fill=rgb("#6E5A42"))
cv.save(os.path.join(OUT, "08-profile.jpg"), quality=95, optimize=True)
print("08 done")

# ================= 10 场景 =================
acc = op("g-10-accessories.jpg"); desk = op("g-10-desk.jpg"); night = op("g-01-concept.jpg")
cv = Image.new("RGB", (W, H), rgb(PAPER)); d = ImageDraw.Draw(cv)
head(d, "IN USE", "它在哪", "三个真实场景：桌上、口袋里、夜里。")

Y = 210
cv.paste(boxcut(desk, (0.05,0.05,0.95,0.95), 520, 470), (M, Y))
cv.paste(boxcut(acc,  (0.05,0.05,0.95,0.95), 520, 226), (M+532, Y))
cv.paste(boxcut(night,(0.05,0.20,0.95,0.85), 520, 232), (M+532, Y+238))
d = ImageDraw.Draw(cv)
cap(d, M+14, Y+470-38, "01 · 桌面：笔、纸、一杯冷的咖啡")
cap(d, M+546, Y+226-36, "02 · 出门：皮夹、袖扣、钢笔", 13)
cap(d, M+546, Y+238+232-36, "03 · 夜里：窗台、雨、一盏灯", 13)

TY = Y+510
d.rectangle([M, TY, W-M, TY+1], fill=rgb("#2E2318"))
scenes = [("桌面", "开会时摘下来放在纸上，不占地方"),
          ("出门", "塞进外套内袋，皮带不怕磨"),
          ("夜里", "上链之后放回窗台，第二天接着走")]
yy = TY+28
for k, v in scenes:
    d.text((M, yy), k, font=S(19, "Medium"), fill=rgb(GOLD))
    d.text((M+90, yy), v, font=S(18), fill=rgb(INK))
    yy += 46

BY2 = TY+210
d.rectangle([M, BY2, W-M, BY2+1], fill=rgb("#2E2318"))
d.text((M, BY2+26), "一句话收口", font=S(22, "Medium"), fill=rgb(INK))
d.text((M, BY2+70), "好表的标准不是“戴上像成功人士”，是“戴上之后忘了它”。", font=S(20), fill=rgb(SUB))

# 使用数据行，填满底部
SY2 = BY2+150
d.rectangle([M, SY2, W-M, SY2+1], fill=rgb("#2E2318"))
for i,(v,k) in enumerate([("12","小时 / 天 佩戴"),("40","小时 动力储备"),("0.5","秒 / 日 误差区间"),("19","cm 以下 手腕")]):
    x0 = M + i*258
    d.text((x0, SY2+26), v, font=S(40, "Bold"), fill=rgb(GOLD))
    d.text((x0, SY2+82), k, font=S(14), fill=rgb(SUB))
d.text((M, SY2+134), "误差区间与佩戴时长为方案设定值，非实测；真实产品须以出厂检测为准。", font=S(13), fill=rgb("#6E5A42"))

d.text((M, H-38), "虚构品牌 · 自主命题　·　场景图为概念演绎", font=S(12), fill=rgb("#6E5A42"))
d.text((W-M-48, H-38), "10 / 12", font=S(13), fill=rgb("#6E5A42"))
cv.save(os.path.join(OUT, "10-scenes.jpg"), quality=95, optimize=True)
print("10 done")

# ================= 12 封底 =================
box = op("g-13-box.jpg")
cv = Image.new("RGB", (W, H), rgb(DARK)); d = ImageDraw.Draw(cv)
cv.paste(fit(box, W, 900, 0.5, 0.45), (0, 0))
d = ImageDraw.Draw(cv)
# 渐变过渡
mm = Image.new("L",(1,520))
for i in range(520): mm.putpixel((0,i), int(255*min(1,(i/519)**0.6)))
cv.paste(Image.new("RGB",(W,520),rgb(DARK)),(0,720),mm.resize((W,520)))
d = ImageDraw.Draw(cv)

d.text((M, H-660), "GUĀNSHÍ", font=S(52, "Medium"), fill=rgb("#C08A4A"))
bw = d.textlength("GUĀNSHÍ", font=S(52, "Medium"))
d.text((M+bw+8, H-664), "™", font=S(16, "Medium"), fill=rgb("#C08A4A"))
d.text((M, H-594), "观时 · 第一辑　2026", font=S(20), fill=rgb("#8A7358"))

d.rectangle([M, H-548, M+260, H-547], fill=rgb("#4A3826"))

txt = ["这是一份虚构品牌的视觉方案。",
       "产品图为 AI 生成（即梦 / MiniMax），版式、字体系统、参数分级与文案为本方案原创。",
       "没有真实产品，也没有真实销售。",
       "留下的是一套可以复用的判断方法：先定图位，再做图；先分级，再写文案。"]
yy = H-510
for ln in txt:
    d.text((M, yy), ln, font=S(18), fill=rgb("#A98C68"))
    yy += 34

info = [("品牌","观时 GUĀNSHÍ（虚构）"),("产品","38mm 自动机械腕表"),
        ("页数","12"),("尺寸","1200 × 1600")]
yy = H-350
for k, v in info:
    d.text((M, yy), k, font=S(15), fill=rgb("#6E5A42"))
    d.text((M+110, yy-2), v, font=S(18, "Medium"), fill=rgb("#DCC7A8"))
    yy += 42

d.text((M, H-56), "虚构品牌 · 自主命题", font=S(13), fill=rgb("#6E5A42"))
d.text((W-M-52, H-56), "12 / 12", font=S(14), fill=rgb("#6E5A42"))
cv.save(os.path.join(OUT, "12-colophon.jpg"), quality=95, optimize=True)
print("12 done")

# ================= 05 换新分解图 =================
exp5 = op("g-05-exploded.jpg")
cv = Image.new("RGB", (W, H), rgb(PAPER)); d = ImageDraw.Draw(cv)
head(d, "MOVEMENT", "机芯里的五件事", "拆开看，自动机械只有五个部分在动。")
IMGB = [M, 210, M+700, 1150]
d.rectangle(IMGB, fill="#0E0B08")
pic = fit(exp5, IMGB[2]-IMGB[0]-40, IMGB[3]-IMGB[1]-40)
cv.paste(pic, (IMGB[0]+20, IMGB[1]+20))
d = ImageDraw.Draw(cv)
PX, PY = IMGB[0]+20, IMGB[1]+20
parts = [("01","主夹板","托住所有零件",0.06),("02","齿轮系","把动力一层层减速",0.30),
         ("03","擒纵","每秒放行 6 次",0.50),("04","发条盒","存 40 小时动力",0.62),
         ("05","摆轮","决定走时准不准",0.86)]
LX = IMGB[2] + 36
for no, name, desc, fr in parts:
    cy = PY + int(pic.height*fr)
    X = PX + pic.width//2
    d.ellipse([X-13, cy-13, X+13, cy+13], fill=(14,11,8), outline=rgb(GOLD), width=2)
    tw = d.textlength(no, font=S(14, "Bold"))
    d.text((X-tw/2, cy-10), no, font=S(14, "Bold"), fill=rgb(GOLD))
    d.line([(X+14, cy), (LX-10, cy)], fill="#C9B99F", width=1)
    d.line([(LX-10, cy), (LX-2, cy)], fill=rgb(GOLD), width=2)
    d.text((LX, cy-28), name, font=S(22, "Medium"), fill=rgb(INK))
    d.text((LX, cy+4), desc, font=S(14), fill=rgb(SUB))

TY = 1190
d.rectangle([M, TY, W-M, TY+1], fill=rgb("#2E2318"))
d.text((M, TY+26), "为什么只做四层外壳", font=S(22, "Medium"), fill=rgb(INK))
for i, ln in enumerate(["自动机械的复杂度不在层数，在于每一层都要能单独换。",
                        "表镜碎了换表镜，机芯保养换机芯，表带磨了换表带。",
                        "拆得开，才配叫耐用品。"]):
    d.text((M, TY+68+i*30), ln, font=S(17), fill=rgb(SUB))
d.text((M, H-38), "虚构品牌 · 自主命题　·　图示为机芯分解示意", font=S(12), fill=rgb("#6E5A42"))
d.text((W-M-48, H-38), "05 / 12", font=S(13), fill=rgb("#6E5A42"))
cv.save(os.path.join(OUT, "05-anatomy.jpg"), quality=95, optimize=True)
print("05 done (new exploded)")
