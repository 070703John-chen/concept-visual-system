# -*- coding: utf-8 -*-
"""按参考排版规则整体重排 14 页
五种页面类型：HERO / FEATURE / SPEC / GRID / BRAND
四档字号：T1=72 T2=26 T3=16 T4=12
文字一律压在压暗区，永不压产品
"""
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
TXTW = 480          # 文字块最大宽度

def c(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def op(n, trim=True):
    im = Image.open(os.path.join(A,n)).convert("RGB")
    if trim:
        w,h = im.size
        im = im.crop((int(w*0.02), int(h*0.04), int(w*0.96), int(h*0.94)))
    return im
def cover(im,w,h,ax=0.5,ay=0.5):
    sc=max(w/im.width,h/im.height)
    im2=im.resize((int(im.width*sc)+1,int(im.height*sc)+1),Image.LANCZOS)
    x=int((im2.width-w)*ax); y=int((im2.height-h)*ay)
    return im2.crop((x,y,x+w,y+h))
def contain(im,w,h):
    sc=min(w/im.width,h/im.height)
    return im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)

def scrim_grad(cv, box, direction="left", amax=215, color=(8,6,4)):
    """在 box 区域画方向渐变的暗色遮罩"""
    x0,y0,x1,y1 = box
    w,h = x1-x0, y1-y0
    if w<=0 or h<=0: return
    if direction in ("left","right"):
        m = Image.new("L",(w,1))
        for i in range(w):
            t = i/(w-1) if w>1 else 0
            v = (1-t) if direction=="left" else t
            m.putpixel((i,0), int(amax*(v**1.2)))
        cv.paste(Image.new("RGB",(w,h),color),(x0,y0),m.resize((w,h)))
    else:
        m = Image.new("L",(1,h))
        for i in range(h):
            t = i/(h-1) if h>1 else 0
            v = (1-t) if direction=="top" else t
            m.putpixel((0,i), int(amax*(v**1.2)))
        cv.paste(Image.new("RGB",(w,h),color),(x0,y0),m.resize((w,h)))

def header(d, en, no, total=14):
    d.text((M, 44), "GUĀNSHÍ", font=S(19,"Medium"), fill=c(GOLD))
    bw = d.textlength("GUĀNSHÍ", font=S(19,"Medium"))
    d.text((M+bw+4, 39), "™", font=S(10,"Medium"), fill=c(GOLD))
    d.text((M+bw+18, 47), "·  "+en, font=S(T4,"Medium"), fill=c(SUB))
    d.text((W-M-72, 47), f"{no:02d}", font=S(T4,"Medium"), fill=c("#6E5A42"))

def footer_brand(d, note="虚构品牌 · 自主命题"):
    d.text((M, H-46), note, font=S(T4), fill=c("#6E5A42"))

# ============================================================
# 01 HERO（封面）
# ============================================================
img = op("g-03-hero.jpg")
cv = cover(img, W, H, 0.52, 0.42)
scrim_grad(cv, (0,0,560,H), "left", 205)
scrim_grad(cv, (0,0,W,240), "top", 140)
d = ImageDraw.Draw(cv)
d.text((M, 64), "GUĀNSHÍ", font=S(24,"Medium"), fill=c(GOLD))
bw = d.textlength("GUĀNSHÍ", font=S(24,"Medium"))
d.text((M+bw+6, 58), "™", font=S(11,"Medium"), fill=c(GOLD))
d.text((M, 108), "自命题概念设计 · 第一辑 / 2026", font=S(T3), fill=c(SUB))
d.text((M, 300), "38", font=S(132,"Bold"), fill=c(FG))
_w38 = d.textlength("38", font=S(132,"Bold"))
d.text((M+_w38+22, 352), "mm", font=S(30,"Medium"), fill=c(GOLD))
d.text((M, 462), "表径 38 · 厚 10.8 · 表带 20 · 重 68 g", font=S(25,"Medium"), fill=c("#E8D6B8"))
d.text((M, 508), "自动上链 · 40 小时动力储存 · 蓝宝石单面防眩 · 5 ATM", font=S(T3), fill=c("#C9B393"))
d.text((M, 548), "依据：方案设定值，非实测", font=S(T4), fill=c(SUB))
d.text((M, H-96), "GUĀNSHÍ · 38 mm automatic · 2026", font=S(T3), fill=c("#A98C68"))
cv.save(os.path.join(OUT,"01-cover.jpg"), quality=95, optimize=True)
print("01 HERO")

# ============================================================
# 02 FEATURE（为什么是 38）
img = op("g-o2-hands.jpg", trim=False)
cv = cover(img, W, H, 0.5, 0.28)
scrim_grad(cv, (0,0,W,760), "top", 235)
scrim_grad(cv, (0,0,640,H), "left", 200)
d = ImageDraw.Draw(cv)
header(d, "MANIFESTO", 2)
d.text((M, 92), "表径 38 mm：同级普遍 40–44", font=S(42,"Bold"), fill=c(FG))

# 大数字 + 说明，全部压在上方暗区（不碰表）
d.text((M, 210), "38", font=S(96,"Bold"), fill=c(GOLD))
bw = d.textlength("38", font=S(96,"Bold"))
d.text((M+bw+12, 262), "mm", font=S(30,"Medium"), fill=c(FG))
d.text((M+bw+120, 256), "男表惯例 40–44", font=S(T3), fill=c("#A98C68"))

d.text((M, 352), "收益：袖口内径 42 mm 以上不顶壳。", font=S(28,"Medium"), fill=c("#E8D6B8"))
d.text((M, 404), "代价：机芯空间更小，摆轮直径被压缩，走时更难调稳。", font=S(T3), fill=c("#B39A78"))
d.text((M, 436), "适用：手腕周长 15–18 cm；超过 19 cm 建议换 20 mm 表带。", font=S(T3), fill=c("#B39A78"))
d.text((M, 476), "依据：同级公开规格 40–44 mm · 本表参数为方案设定值，非实测", font=S(T4,"Medium"), fill=c("#8A7358"))

# 底部：三格规格（暗区，不压产品）
by = H-250
scrim_grad(cv, (0,H-280,W,H), "bottom", 225)
d = ImageDraw.Draw(cv)
for i,(v,k) in enumerate([("38 mm","表径"),("10.8 mm","厚度"),("68 g","重量")]):
    x0 = M + i*300
    d.text((x0, by), v, font=S(38,"Medium"), fill=c(FG))
    d.text((x0, by+50), k, font=S(T4), fill=c(SUB))
footer_brand(d)
cv.save(os.path.join(OUT,"02-manifesto.jpg"), quality=95, optimize=True)
print("02 FEATURE")

# 04 GRID（皮与钢）3-2-1 阶梯
cv = Image.new("RGB",(W,H),c(BG)); d = ImageDraw.Draw(cv)
header(d, "MATERIAL & CRAFT", 4)
d.text((M, 92), "六处近看：三处工艺，三处结构", font=S(40,"Bold"), fill=c(FG))
d.text((M, 152), "上排决定摸起来怎么样，下排决定用久了会不会坏。", font=S(T3), fill=c(SUB))

# 第一排：三处工艺
row1 = [("g-s6-leather.jpg","马鞍针 · 两根线交叉"),("g-04-buckle.jpg","316L 针扣"),("g-08-crown.jpg","滚花表冠")]
GW = (W-2*M-2*12)//3
GH = 250
Y = 226
for i,(f,cap) in enumerate(row1):
    im = op(f, False)
    x = M + i*(GW+12)
    cv.paste(cover(im, GW, GH, 0.5, 0.45), (x, Y))
    d = ImageDraw.Draw(cv)
    d.text((x, Y+GH+8), cap, font=S(T4,"Medium"), fill=c("#C9B393"))

# 第二排：两处结构
Y2 = Y + GH + 54
GW2 = (W-2*M-12)//2
GH2 = 300
row2 = [("g-11-detail.jpg","摆轮 · 机芯微距"),("g-05-exploded.jpg","机芯分层 · 五个部件")]
for i,(f,cap) in enumerate(row2):
    im = op(f, False)
    x = M + i*(GW2+12)
    box = [x, Y2, x+GW2, Y2+GH2]
    if f == "g-05-exploded.jpg":
        d.rectangle(box, fill="#0B0A08")
        pic = contain(im, GW2-10, GH2-10)
        cv.paste(pic, (x+(GW2-pic.width)//2, Y2+(GH2-pic.height)//2))
    else:
        cv.paste(cover(im, GW2, GH2, 0.5, 0.5), (x, Y2))
    d = ImageDraw.Draw(cv)
    d.text((x, Y2+GH2+8), cap, font=S(T4,"Medium"), fill=c("#C9B393"))

# 第三排：整表（最大，突出）
Y3 = Y2 + GH2 + 54
BIG = [M, Y3, W-M, Y3+540]
d.rectangle(BIG, fill="#131009")
_ht = Image.open(os.path.join(A,"g-03-hero.jpg")).convert("RGB")
_w,_h=_ht.size
ht = _ht.crop((int(_w*0.03), int(_h*0.13), int(_w*0.93), int(_h*0.90)))
pic = contain(ht, BIG[2]-BIG[0]-16, BIG[3]-BIG[1]-16)
cv.paste(pic, (BIG[0]+(BIG[2]-BIG[0]-pic.width)//2, BIG[1]+(BIG[3]-BIG[1]-pic.height)//2))
d = ImageDraw.Draw(cv)
d.text((M, Y3+556), "整表 · 38mm 黑钢镂空（不裁切）", font=S(T3,"Medium"), fill=c(FG))
d.text((M, Y3+592), "头层牛皮 1.2 mm · 双针马鞍缝 · 线径 0.6 mm · 表带 20 mm", font=S(T3), fill=c(SUB))
d.text((M, Y3+622), "依据：材料与工艺为方案设定值，非实测", font=S(T4), fill=c("#6E5A42"))
# 底部：工序三步（具体怎么做）
SY = Y3+664
d.rectangle([M, SY, W-M, SY+1], fill=c("#4A3722"))
d.text((M, SY+18), "表带怎么做：三步", font=S(T4,"Medium"), fill=c(SUB))
steps = [
 ("01","裁切","按 20 mm 宽度裁条，边缘削薄至 0.8 mm，再对折压合"),
 ("02","打孔","菱锥每 4 mm 打一孔，两排孔错开 2 mm，孔距误差 ±0.3 mm"),
 ("03","马鞍缝","两根线同向穿，每针回拉锁死 —— 断一处，其余仍锁住"),
]
cw = (W-2*M-24)//3
for i,(no,title,desc) in enumerate(steps):
    x0 = M + i*(cw+12)
    d.text((x0, SY+52), no, font=S(22,"Bold"), fill=c(GOLD))
    d.text((x0+42, SY+56), title, font=S(19,"Medium"), fill=c(FG))
    # 两句以内换行
    cur=""; yy=SY+92
    for ch in desc:
        if d.textlength(cur+ch, font=S(13)) > cw-10 and ch not in "，。；":
            d.text((x0, yy), cur, font=S(13), fill=c("#A98C68")); yy+=22; cur=ch
        else:
            cur+=ch
    if cur: d.text((x0, yy), cur, font=S(13), fill=c("#A98C68"))
    if i < 2:
        d.text((x0+cw-2, SY+58), "→", font=S(16), fill=c("#5C452C"))
cv.save(os.path.join(OUT,"04-material.jpg"), quality=95, optimize=True)
print("04 GRID 3-2-1")

# 05 SPEC（机芯五件事 —— 图 + 五行参数）
# ============================================================
im = op("g-05-exploded.jpg")
cv = Image.new("RGB",(W,H),c(BG)); d = ImageDraw.Draw(cv)
header(d, "MOVEMENT", 5)
d.text((M, 92), "机芯里的五件事", font=S(52,"Bold"), fill=c(FG))
BOX = [M, 200, W-M, 1080]
d.rectangle(BOX, fill="#0B0A08")
pic = contain(im, BOX[2]-BOX[0]-24, BOX[3]-BOX[1]-24)
PX = BOX[0]+(BOX[2]-BOX[0]-pic.width)//2
PY = BOX[1]+(BOX[3]-BOX[1]-pic.height)//2
cv.paste(pic, (PX, PY))
d = ImageDraw.Draw(cv)
# 编号点 + 右侧文字（文字在图右侧暗区）
parts = [("01","主夹板","托住所有零件",0.07),("02","齿轮系","把动力层层减速",0.30),
         ("03","擒纵","每秒放行 6 次",0.50),("04","发条盒","存 40 小时",0.63),
         ("05","摆轮","决定准不准",0.87)]
LX = BOX[2] - 300
for no,name,desc,fr in parts:
    yy = PY + int(pic.height*fr)
    X = PX + pic.width//2
    d.ellipse([X-12, yy-12, X+12, yy+12], fill=(10,8,6), outline=c(GOLD), width=2)
    tw = d.textlength(no, font=S(T4,"Bold"))
    d.text((X-tw/2, yy-8), no, font=S(T4,"Bold"), fill=c(GOLD))
    d.line([(X+12, yy),(LX-8, yy)], fill="#4A3B2A", width=1)
    d.text((LX, yy-26), name, font=S(22,"Medium"), fill=c(FG))
    d.text((LX, yy+2), desc, font=S(T4), fill=c(SUB))

BY = 1120
d.rectangle([M, BY, W-M, BY+1], fill=c("#4A3722"))
for i,(v,k) in enumerate([("21600","次 / 小时"),("40","小时动力"),("7","颗宝石"),("0","计时按钮")]):
    x0 = M + i*264
    d.text((x0, BY+24), v, font=S(38,"Bold"), fill=c(GOLD))
    d.text((x0, BY+74), k, font=S(T4), fill=c(SUB))
d.text((M, BY+120), "以上为方案设定值，非实测。", font=S(T4), fill=c("#6E5A42"))
footer_brand(d)
cv.save(os.path.join(OUT,"05-anatomy.jpg"), quality=95, optimize=True)
print("05 SPEC")

# ============================================================
# 06 HERO（十一点）
# ============================================================
img = op("g-campfire.jpg", trim=False)
cv = cover(img, W, H, 0.5, 0.45)
scrim_grad(cv, (0,0,520,H), "left", 210)
scrim_grad(cv, (0,0,W,240), "top", 140)
d = ImageDraw.Draw(cv)
header(d, "NIGHT", 6)
d.text((M, 330), "40", font=S(150,"Bold"), fill=c(GOLD))
d.text((M+230, 430), "小时", font=S(34,"Medium"), fill=c(FG))
d.text((M, 530), "动力储存：静置一夜仍在走。", font=S(T2), fill=c(FG))
d.text((M, 576), "日常佩戴 8 小时即可上满；满弦后平放 40 小时不停表。", font=S(T3), fill=c("#B39A78"))
d.text((M, 608), "依据：自动上链机构 · 方案设定值，非实测", font=S(T4), fill=c(SUB))
d.text((M, H-96), "概念演绎 · 非产品图", font=S(T4), fill=c("#6E5A42"))
cv.save(os.path.join(OUT,"06-night.jpg"), quality=95, optimize=True)
print("06 HERO")

# ============================================================
# 07 SPEC（参数）
# ============================================================
im = op("g-07-tight.jpg", trim=False)
cv = Image.new("RGB",(W,H),c(BG)); d = ImageDraw.Draw(cv)
header(d, "SPECIFICATION", 7)
d.text((M, 92), "参数", font=S(52,"Bold"), fill=c(FG))
# 左：产品图（contain，完整）
LB = [M, 210, M+470, 1010]
d.rectangle(LB, fill="#131009")
pic = contain(im, LB[2]-LB[0]-20, LB[3]-LB[1]-20)
cv.paste(pic, (LB[0]+(LB[2]-LB[0]-pic.width)//2, LB[1]+(LB[3]-LB[1]-pic.height)//2))
d = ImageDraw.Draw(cv)
# 右：12 行
TX = M+520
rows = [("型号","GS-3801"),("机芯","自动上链 · 40h"),("表壳","316L · 拉丝"),
        ("表冠","推拉式 · 单表冠"),("前圈","哑黑 · 抛光边"),("表盘","哑黑 · 镂空"),
        ("表针","剑形 · 玫瑰金"),("表镜","蓝宝石 · 单面防眩"),("后盖","316L · 螺旋透底"),
        ("表带","头层牛皮 · 深棕"),("表扣","针扣"),("防水","5 ATM")]
y = 214
for k,v in rows:
    d.line([(TX, y), (W-M, y)], fill="#2E2318", width=1)
    d.text((TX, y+14), k, font=S(T4), fill=c(SUB))
    d.text((TX+92, y+10), v, font=S(T3,"Medium"), fill=c(FG))
    y += 66
d.line([(TX, y), (W-M, y)], fill="#2E2318", width=1)
# 底部：五个尺寸
BY = 1070
d.rectangle([M, BY, W-M, BY+1], fill=c("#4A3722"))
for i,(v,k) in enumerate([("38","表径 mm"),("10.8","厚度 mm"),("20","表带 mm"),("115","长度 mm"),("68","重量 g")]):
    x0 = M + i*210
    d.text((x0, BY+26), v, font=S(34,"Medium"), fill=c(FG))
    d.text((x0, BY+70), k, font=S(T4), fill=c(SUB))
d.text((M, BY+120), "佩戴建议：手腕周长 < 19cm　·　以上为方案设定值", font=S(T4), fill=c("#6E5A42"))
footer_brand(d)
cv.save(os.path.join(OUT,"07-spec.jpg"), quality=95, optimize=True)
print("07 SPEC")

# ============================================================
# 09 SPEC（五种表面）
# ============================================================
cv = Image.new("RGB",(W,H),c(BG)); d = ImageDraw.Draw(cv)
header(d, "VARIANTS", 9)
d.text((M, 92), "五种表面，一套壳型", font=S(44,"Bold"), fill=c(FG))
d.text((M, 152), "换电镀、盘漆与表带，壳型不动 —— 一条模具能扩成五支。", font=S(T3), fill=c(SUB))

sw = [("#1B1B1B","哑黑钢","PVD"),("#8A5A2B","玫瑰金","电镀"),("#B9B5AD","拉丝银","316L"),
      ("#3B2A1E","深褐皮","头层"),("#E8DCC8","米白盘","哑光")]
for i,(hx,name,note) in enumerate(sw):
    x0 = M + i*210
    d.rectangle([x0, 240, x0+150, 390], fill=c(hx), outline="#3A2C1E", width=1)
    d.text((x0, 402), name, font=S(T3,"Medium"), fill=c(FG))
    d.text((x0, 428), note, font=S(T4), fill=c(SUB))
    d.text((x0, 450), hx.upper(), font=S(T4), fill=c("#6E5A42"))

BY = 560
d.rectangle([M, BY, W-M, BY+1], fill=c("#4A3722"))
d.text((M, BY+30), "组合规则", font=S(24,"Medium"), fill=c(GOLD))
rules = [("壳色 × 盘色","任意组合",True),("壳色 × 表带","任意组合",True),
         ("电镀壳 × 刻字","可做，需加固化层",True),("米白盘 × 夜光","不可做 —— 反差不足",False)]
for i,(a,b,ok) in enumerate(rules):
    yy = BY+80+i*52
    d.text((M, yy), a, font=S(T3,"Medium"), fill=c(FG))
    d.text((M+300, yy), b, font=S(T3), fill=c(GOLD if ok else "#C06A4A"))

CY = BY+320
d.rectangle([M, CY, W-M, CY+1], fill=c("#4A3722"))
d.text((M, CY+30), "为什么列“不可做”", font=S(24,"Medium"), fill=c(FG))
d.text((M, CY+74), "把限制写出来，下单时才不会来回改三次。", font=S(T3), fill=c(SUB))
d.text((M, CY+106), "A spec sheet that hides limits costs more time than it saves.", font=S(T3), fill=c("#A98C68"))
footer_brand(d)
cv.save(os.path.join(OUT,"09-variants.jpg"), quality=95, optimize=True)
print("09 SPEC")

# ============================================================
# 10 GRID（它在哪）—— 上排暖调 / 下排冷调
items = [("g-s7-hand.jpg","01 · 出门前调一格","暖"),
         ("g-10-desk.jpg","02 · 桌上，笔和冷掉的咖啡","暖"),
         ("g-s3-tent.jpg","03 · 山里，帐篷亮着","冷"),
         ("g-s5-snow.jpg","04 · 结霜的窗台","冷")]
cv = Image.new("RGB",(W,H),c(BG)); d = ImageDraw.Draw(cv)
header(d, "IN USE", 10)
d.text((M, 92), "四个场景，两种色温", font=S(44,"Bold"), fill=c(FG))
d.text((M, 152), "上排 2700–3200 K（室内暖光），下排 5600 K 以上（日光/雪地）。", font=S(T3), fill=c(SUB))

GW = (W-2*M-12)//2; GH = 430
for i,(f,cap,tone) in enumerate(items):
    im = op(f, trim=False)
    x = M if i%2==0 else M+GW+12
    y = 230 + (i//2)*(GH+56)
    cv.paste(cover(im, GW, GH, 0.5, 0.45), (x, y))
    d = ImageDraw.Draw(cv)
    d.text((x, y+GH+8), cap, font=S(T4,"Medium"), fill=c(FG))
    tw = d.textlength(tone, font=S(T4,"Medium"))
    d.text((x+GW-tw-4, y+GH+8), tone, font=S(T4,"Medium"), fill=c(GOLD))

BY = 230 + 2*(GH+56) + 8
d.rectangle([M, BY, W-M, BY+1], fill=c("#4A3722"))
d.text((M, BY+26), "暗处不反光，亮处不刺眼。", font=S(T2), fill=c(FG))
d.text((M, BY+78), "场景图为概念演绎，非产品图。", font=S(T4), fill=c("#6E5A42"))
footer_brand(d)
cv.save(os.path.join(OUT,"10-scenes.jpg"), quality=95, optimize=True)
print("10 GRID 暖冷分组")
