# -*- coding: utf-8 -*-
"""南枝 v2：9 页（保留的新素材 + 原有素材）"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from kit import S
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cfg import ASSETS as A, OUT as OUT   # 素材目录与输出目录都来自 config.json
OLD = A     # 原片（.jpg 平铺在 assets/ 下）
NEW = A     # 新素材同目录，脚本按文件名取用
os.makedirs(OUT, exist_ok=True)

W, H, M = 1200, 1600, 72
INK, SUB, GOLD = (34,26,18), (100,82,58), (152,108,58)
CREAM = (238,230,214)

# ---------- 抠瓶 ----------
def cutout_bottle():
    src = Image.open(os.path.join(OLD, "NZ-主图-白底-1200.jpg")).convert("RGB")
    a = np.asarray(src).astype(np.float32); hh, ww, _ = a.shape
    white = (a[:,:,0]>238)&(a[:,:,1]>238)&(a[:,:,2]>238)
    mk = np.zeros((hh,ww),dtype=bool); dq=deque()
    for x in range(ww):
        for y in (0,hh-1):
            if white[y,x] and not mk[y,x]: mk[y,x]=True; dq.append((y,x))
    for y in range(hh):
        for x in (0,ww-1):
            if white[y,x] and not mk[y,x]: mk[y,x]=True; dq.append((y,x))
    while dq:
        y,x = dq.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx=y+dy,x+dx
            if 0<=ny<hh and 0<=nx<ww and white[ny,nx] and not mk[ny,nx]:
                mk[ny,nx]=True; dq.append((ny,nx))
    al = Image.fromarray(((~mk)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))
    b = src.convert("RGBA"); b.putalpha(al)
    return b.crop(b.getbbox())

BOTTLE = cutout_bottle()


def make_cool(bt):
    arr = np.asarray(bt).astype(np.float32)
    h = arr.shape[0]
    cap_h = int(h*0.30)          # 上半部：盖
    # 盖：去饱和偏银
    cap = arr[:cap_h, :, :3]
    g = cap.mean(axis=2, keepdims=True)
    cap = g*0.98 + (cap - g)*0.12
    cap[:,:,2] = np.clip(cap[:,:,2] + 12, 0, 255)
    arr[:cap_h, :, :3] = cap
    # 瓶身：整体压冷、降饱和
    body = arr[cap_h:, :, :3]
    gb = body.mean(axis=2, keepdims=True)
    body = gb + (body - gb)*0.55
    body[:,:,0] *= 0.90; body[:,:,1] *= 0.98; body[:,:,2] = np.clip(body[:,:,2]*1.12, 0, 255)
    arr[cap_h:, :, :3] = body
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8), "RGBA")

BOTTLE_COOL = make_cool(BOTTLE)


def find_label_box(bt):
    """在原瓶图上找米色标签的实际范围"""
    a = np.asarray(bt).astype(np.int16)
    rgb = a[:,:,:3]
    # 标签米色 ~ (232,214,186)
    m = (np.abs(rgb[:,:,0]-232)<26) & (np.abs(rgb[:,:,1]-214)<26) & (np.abs(rgb[:,:,2]-186)<28)
    m &= (a[:,:,3] > 200)
    ys, xs = np.where(m)
    if len(xs) < 500:
        w, h = bt.size
        return (int(w*0.20), int(h*0.50), int(w*0.80), int(h*0.78))
    return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))

# 实测（网格量取）：标签矩形 x 0.255–0.765 / y 0.375–0.735
_w0, _h0 = BOTTLE.size
LABEL_BOX = (int(_w0*0.232), int(_h0*0.366), int(_w0*0.828), int(_h0*0.748))

def relabel(bt, title, sub="EAU DE PARFUM", vol="50 ML"):
    """在瓶身上重绘标签（同形不同名）"""
    out = bt.copy()
    d = ImageDraw.Draw(out)
    w, h = out.size
    lx0, ly0, lx1, ly1 = LABEL_BOX
    lx0 += 2; ly0 += 2; lx1 -= 2; ly1 -= 2
    d.rectangle([lx0, ly0, lx1, ly1], fill=(240,233,221,255))
    cx = (lx0+lx1)//2
    def center(y, txt, font, fill):
        tw = d.textlength(txt, font=font)
        d.text((cx-tw/2, y), txt, font=font, fill=fill)
    center(ly0+14, "N A N Z H I", S(15,"Medium"), (66,54,42))
    d.line([(cx-30, ly0+44),(cx+30, ly0+44)], fill=(130,108,84), width=1)
    center(ly0+56, title, S(26,"Bold"), (48,40,30))
    center(ly0+92, sub, S(11), (112,94,72))
    center(ly0+112, vol, S(11), (132,114,90))
    return out

BOTTLE_002 = relabel(BOTTLE_COOL, "晨露苔原")

def grad(w,h,top,bot,vign=0.16,angle=0.22):
    t = np.linspace(0,1,h)[:,None]
    tp = np.array(top,dtype=np.float32); bt = np.array(bot,dtype=np.float32)
    g = tp[None,None,:]*(1-t[:,:,None]) + bt[None,None,:]*t[:,:,None]
    g = np.repeat(g, w, axis=1)
    x = np.linspace(0,1,w)[None,:,None]
    g = g*(1-angle) + np.repeat(tp[None,None,:]*(1-x)+bt[None,None,:]*x, h, axis=0)*angle
    yy,xx = np.mgrid[0:h,0:w].astype(np.float32)
    r = np.sqrt(((xx-w/2)/(w/2))**2 + ((yy-h/2)/(h/2))**2)
    g = g*(1-vign*np.clip(r-0.4,0,1.4)**1.4)[:,:,None]
    return Image.fromarray(np.clip(g,0,255).astype(np.uint8)).convert("RGBA")

def bg_blur(path, blur=26, dark=0.18):
    im = Image.open(path).convert("RGB")
    sc = max(W/im.width, H/im.height)*1.12
    im = im.resize((int(im.width*sc)+1,int(im.height*sc)+1), Image.LANCZOS)
    im = im.crop(((im.width-W)//2,(im.height-H)//2,(im.width-W)//2+W,(im.height-H)//2+H))
    im = im.filter(ImageFilter.GaussianBlur(blur))
    if dark:
        a = np.asarray(im).astype(np.float32)*(1-dark)
        im = Image.fromarray(np.clip(a,0,255).astype(np.uint8))
    return im.convert("RGBA")

def tags(d, items, color=INK):
    x = M
    for t in items:
        d.text((x, 44), "◆ " + t, font=S(13), fill=color+(225,))
        x += d.textlength("◆ "+t, font=S(13)) + 22
    d.line([(M, 74),(W-M,74)], fill=(150,120,84,120), width=1)

def sect(d, cn, en, color=INK, y=54):
    d.text((M, y), "●", font=S(13), fill=GOLD+(240,))
    d.text((M+24, y-8), cn, font=S(22,"Medium"), fill=color+(250,))
    tw = d.textlength(en, font=S(12))
    d.text((W-M-tw, y), en, font=S(12), fill=(150,126,96,230))
    d.line([(M, y+30),(W-M,y+30)], fill=(160,134,100,150), width=1)

def paste_bottle(cv, target_h, cx, bottom_y, shadow=True, alpha=115, src=None):
    _b = src if src is not None else BOTTLE
    ph = target_h; pw = int(_b.width*ph/_b.height)
    b = _b.resize((pw,ph), Image.LANCZOS)
    px = int(cx - pw/2); py = int(bottom_y - ph)
    if shadow:
        sw_, sh_ = int(pw*2.2), int(ph*0.34)
        yy_, xx_ = np.mgrid[0:sh_, 0:sw_].astype(np.float32)
        ex = ((xx_-sw_/2)/(sw_/2))**2
        ey = ((yy_-sh_/2)/(sh_/2))**2
        fall = np.clip(1.0-(ex*0.75+ey*0.9), 0, 1)**2.2
        arr = np.zeros((sh_, sw_, 4), dtype=np.uint8)
        arr[:,:,0]=88; arr[:,:,1]=70; arr[:,:,2]=52
        arr[:,:,3]=(fall*alpha).astype(np.uint8)
        sh = Image.fromarray(arr,"RGBA")
        cv.paste(sh,(int(cx-sw_/2), int(bottom_y-sh_*0.42)), sh)
    cv.paste(b,(px,py),b)

def tile(cv, path, box, cap=None, note=None, d_color=INK, ax=0.5, ay=0.5):
    im = Image.open(path).convert("RGB")
    w2,h2 = box[2]-box[0], box[3]-box[1]
    sc = max(w2/im.width, h2/im.height)
    im = im.resize((int(im.width*sc)+1,int(im.height*sc)+1), Image.LANCZOS)
    ox = int((im.width-w2)*ax); oy = int((im.height-h2)*ay)
    im = im.crop((ox, oy, ox+w2, oy+h2))
    cv.paste(im,(box[0],box[1]))
    if cap:
        dd = ImageDraw.Draw(cv)
        dd.text((box[0], box[3]+12), cap, font=S(20,"Medium"), fill=d_color+(250,))
        if note: dd.text((box[0], box[3]+44), note, font=S(13), fill=(120,98,72,235))

# ================= 01 封面 =================
cv = grad(W,H,(242,235,222),(210,196,172))
d = ImageDraw.Draw(cv)

# 背景水印：中文「南枝」竖排（右内侧）+ 英文 NÁNZHĪ 横排（下方居中），都很淡
# 版心细框（水印与它对边）
d.rectangle([M, M, W-M, H-M], outline=(120,96,66,70), width=1)
# 水印：中文竖排撑满版心高度（左上角对齐框内），英文压框底、左对齐
# 水印：从标题下方起排，落到框底；左边线与框左线对齐，不越界、不压产品
_wm_size = 400
_wm_cn = S(_wm_size, "Bold")
_cn_x = M + 12
_cn_top = 470
for i, ch in enumerate("南枝"):
    d.text((_cn_x, _cn_top + i*(_wm_size + 20)), ch, font=_wm_cn, fill=(120,96,66,16))
_wm_en = S(66, "Bold")
_en = "N Á N Z H Ī"
d.text((M + 12, 1392), _en, font=_wm_en, fill=(120,96,66,15))

tags(d, ["NÁNZHĪ","EAU DE PARFUM","2026","AFTER THE RAIN"])
d.text((M, 150), "雨后木质", font=S(86,"Bold"), fill=INK+(255,))
d.text((M, 260), "雪松 · 苔藓 · 白麝香", font=S(26,"Medium"), fill=SUB+(245,))
d.line([(M, 316),(M+470,316)], fill=GOLD+(170,), width=2)
d.text((M, 348), "50 ML · EAU DE PARFUM 12% · 留香 6–8 小时", font=S(17), fill=SUB+(235,))
paste_bottle(cv, 760, W*0.70, 1400)
d = ImageDraw.Draw(cv)
d.text((M, H-70), "虚构品牌 · 自主命题方案", font=S(13), fill=(150,128,100,225))
d.text((W-M-58, H-70), "01", font=S(15), fill=(150,128,100,225))
cv.convert("RGB").save(os.path.join(OUT,"01-封面.jpg"), quality=95, optimize=True)
print("01")

# ================= 02 关键词 =================
cv = bg_blur(os.path.join(OLD,"NZ-P1-场景.jpg"), blur=26, dark=0.20)
d = ImageDraw.Draw(cv)
tags(d, ["NÁNZHĪ","EAU DE PARFUM","2026","AFTER THE RAIN"], (222,204,178))
words = [("木质","wood"),("苔藓","moss"),("雨后","rain")]
cw = (W-2*M)//3
for i,(cn,en) in enumerate(words):
    cx = M + i*cw + cw//2
    w1 = d.textlength(cn, font=S(78,"Bold"))
    d.text((cx-w1/2, 600), cn, font=S(78,"Bold"), fill=(244,234,216,255))
    w2 = d.textlength(en, font=S(24))
    d.text((cx-w2/2, 706), en, font=S(24), fill=(202,180,148,235))
    if i < 2: d.text((M+cw*(i+1)-18, 612), "×", font=S(48), fill=(190,160,120,220))
d.text((M, H-152), "一支香水的三个关键词，也是它的配方顺序。", font=S(21), fill=(226,208,180,245))
d.text((M, H-116), "Three words, in the order they arrive on skin.", font=S(14), fill=(186,164,134,215))
d.text((W-M-58, H-116), "02", font=S(15), fill=(186,164,134,215))
cv.convert("RGB").save(os.path.join(OUT,"02-关键词.jpg"), quality=95, optimize=True)
print("02")

# ================= 03 香调分析 =================
cv = Image.new("RGB",(W,H),CREAM).convert("RGBA")
d = ImageDraw.Draw(cv)
sect(d, "香调分析", "NOTES ANALYSIS")
facts = ["○ 前调占比 30%","○ 中调占比 45%","○ 后调占比 25%","○ 留香 6–8 小时"]
for i,f in enumerate(facts):
    d.text((M + (i%2)*530, 110 + (i//2)*44), f, font=S(20), fill=INK+(250,))
d.text((M, 214), "○ 中调最高：雪松 45%，决定这支香的主体", font=S(21), fill=INK+(252,))
d.text((M, 252), "前调 30 秒内散掉，后调贴皮 6 小时以上；中调占比决定它是不是一支木质调。", font=S(16), fill=SUB+(245,))
d.text((M, 282), "数据为方案设定值，非实测。", font=S(12), fill=(150,126,96,230))
tile(cv, os.path.join(OLD,"NZ-P9-手持.jpg"), [M, 320, M+510, 880], "握在手里", "瓶身 38 × 82 mm")
tile(cv, os.path.join(NEW,"N4-纸盒平面.jpg"), [M+530, 320, M+1058, 880], "纸盒", "350 g 灰板 · 磁吸")
d = ImageDraw.Draw(cv)
BY = 1010
d.text((M, BY), "配方比例", font=S(27,"Medium"), fill=INK+(252,))
for i,(label,bar) in enumerate([("前调 30%",0.30),("中调 45%",0.45),("后调 25%",0.25)]):
    y = BY+52+i*74
    d.text((M, y), label, font=S(21), fill=SUB+(245,))
    d.rectangle([M+250, y+8, M+1000, y+28], fill=(198,178,150))
    d.rectangle([M+250, y+8, M+250+int(750*bar), y+28], fill=(152,108,58))
d.line([(M,1236),(W-M,1236)], fill=(170,144,110), width=1)
d.text((M, 1258), "为什么中调占比最高", font=S(25,"Medium"), fill=INK+(252,))
d.text((M, 1300), "前调负责第一印象，30 秒内散尽；后调贴皮最久，但强度低。", font=S(18), fill=INK+(250,))
d.text((M, 1330), "真正持续 4 小时以上的是中调，所以雪松占到 45%。", font=S(18), fill=INK+(250,))
d.text((M, 1370), "The top note lasts seconds. The base sits close to skin but reads soft.", font=S(13), fill=(150,126,96,235))
d.text((M, 1392), "The heart is what stays for hours — that is why cedar takes 45%.", font=S(13), fill=(150,126,96,235))
d.text((M, H-52), "NÁNZHĪ · 03", font=S(13), fill=(150,126,96,230))
cv.convert("RGB").save(os.path.join(OUT,"03-香调分析.jpg"), quality=95, optimize=True)
print("03")

# ================= 04 材料三格 =================
cv = Image.new("RGB",(W,H),CREAM).convert("RGBA")
d = ImageDraw.Draw(cv)
sect(d, "玻璃、金属、纸", "MATERIALS")
d.text((M, 104), "一支香水由三种材料承担全部触感。", font=S(25,"Medium"), fill=SUB+(245,))
tw3 = 340
# 第一格：金属盖（照片）
tile(cv, os.path.join(NEW,"N3-金属盖内侧.jpg"),
     [M, 170, M+tw3, 640], "金属盖", "螺纹 + 喷头，壁厚 0.8 mm")
# 第二格：玻璃（用抠出的瓶身，画在米底上，不引旧页面文字）
gx0 = M + (tw3+18)
card = Image.new("RGBA",(tw3, 470),(243,236,223,255))
_bh = 420; _bw = int(BOTTLE.width*_bh/BOTTLE.height)
_b = BOTTLE.resize((_bw,_bh), Image.LANCZOS)
card.paste(_b, ((tw3-_bw)//2, 24), _b)
cv.paste(card,(gx0,170),card)
d_ = ImageDraw.Draw(cv)
d_.text((gx0, 652), "玻璃", font=S(20,"Medium"), fill=INK+(250,))
d_.text((gx0, 684), "厚底，肩壁 1.8 mm", font=S(13), fill=(120,98,72,235))
# 第三格：纸盒（照片）
tile(cv, os.path.join(NEW,"N4-纸盒平面.jpg"),
     [M+2*(tw3+18), 170, M+2*(tw3+18)+tw3, 640], "纸盒", "350 g 灰板，烫金压边")
d = ImageDraw.Draw(cv)
NY = 760
d.line([(M,NY),(W-M,NY)], fill=(170,144,110), width=1)
d.text((M, NY+28), "三种材料，三条手感", font=S(36,"Bold"), fill=INK+(252,))
for i, ln in enumerate([
    "玻璃决定透光：厚底折射出暖金色，薄壁会发白。",
    "金属盖决定第一下重量：壁厚 0.8 mm，旋合 1.5 圈到底。",
    "纸盒决定开箱手感：350 g 灰板，磁吸开合，无塑料内衬。"]):
    d.text((M, NY+92+i*40), ln, font=S(21), fill=SUB+(248,))
d.text((M, NY+240), "Three materials decide three parts of the hand-feel: light, weight, and the first second of unboxing.", font=S(13), fill=(150,126,96,235))
d.line([(M, NY+300),(M+420, NY+300)], fill=(170,144,110,150), width=1)
d.text((M, NY+318), "0.8 mm", font=S(34,"Bold"), fill=GOLD+(250,))
d.text((M, NY+364), "金属盖壁厚", font=S(14), fill=SUB+(235,))
d.text((M+220, NY+318), "350 g", font=S(34,"Bold"), fill=GOLD+(250,))
d.text((M+220, NY+364), "灰板克重", font=S(14), fill=SUB+(235,))
paste_bottle(cv, 640, W*0.78, 1500)
d = ImageDraw.Draw(cv)
d.text((M, H-56), "材料参数为方案设定值", font=S(13), fill=(150,126,96,230))
d.text((W-M-58, H-56), "04", font=S(15), fill=(150,126,96,230))
cv.convert("RGB").save(os.path.join(OUT,"04-材料.jpg"), quality=95, optimize=True)
print("04")

# ================= 05 信息页 =================
cv = grad(W,H,(240,232,216),(206,190,164))
d = ImageDraw.Draw(cv)
tags(d, ["NÁNZHĪ","EAU DE PARFUM","2026","50 ML"])
d.text((M, 150), "雨后木质", font=S(72,"Bold"), fill=INK+(255,))
d.text((M, 246), "雪松 · 苔藓 · 白麝香", font=S(25,"Medium"), fill=SUB+(245,))
d.line([(M, 300),(M+460,300)], fill=GOLD+(170,), width=2)
yy = 336
for label,name,pct,bar in [("前调","佛手柑","30%",0.30),("中调","雪松","45%",0.45),("后调","白麝香","25%",0.25)]:
    d.text((M, yy+4), label, font=S(18), fill=SUB+(230,))
    d.text((M+70, yy-2), name, font=S(32,"Medium"), fill=INK+(250,))
    d.text((M+368, yy+2), pct, font=S(26,"Medium"), fill=GOLD+(240,))
    d.rectangle([M, yy+50, M+436, yy+55], fill=(150,120,84,90))
    d.rectangle([M, yy+50, M+int(436*bar), yy+55], fill=GOLD+(235,))
    yy += 104
d.text((M, 668), "配方比例按方案设定：前 30 / 中 45 / 后 25。", font=S(19), fill=SUB+(245,))
d.text((M, 702), "中调占比最高 —— 主体在后半段，不在开瓶那一下。", font=S(19), fill=SUB+(245,))
d.text((M, 736), "依据：方案设定值，非实测。", font=S(14), fill=(150,126,96,230))
paste_bottle(cv, int(H*0.50), W*0.74, 1250)
d = ImageDraw.Draw(cv)
BY = H-200
d.line([(M,BY),(W-M,BY)], fill=(150,120,84,110), width=1)
for i,(v,k) in enumerate([("50","ML 容量"),("12","% 浓度"),("6–8","小时 留香"),("2","款 香型")]):
    x0 = M + i*268
    d.text((x0, BY+24), v, font=S(50,"Bold"), fill=INK+(252,))
    d.text((x0, BY+86), k, font=S(16), fill=SUB+(240,))
d.text((M, H-56), "NÁNZHĪ · 05", font=S(13), fill=(150,126,96,230))
cv.convert("RGB").save(os.path.join(OUT,"05-信息.jpg"), quality=95, optimize=True)
print("05")

# ================= 06 香型卡 =================
t = np.linspace(0,1,H)[:,None]
tp = np.array([236,222,200],dtype=np.float32); bt = np.array([198,178,150],dtype=np.float32)
g = np.repeat(tp[None,None,:]*(1-t[:,:,None]) + bt[None,None,:]*t[:,:,None], W, axis=1)
rng = np.random.default_rng(7); g = g + rng.normal(0,6,(H,W,1))
cv = Image.fromarray(np.clip(g,0,255).astype(np.uint8)).convert("RGBA")
d = ImageDraw.Draw(cv)
tags(d, ["NÁNZHĪ","两款香型","TWO EDITIONS","2026"])
cards = [
 ("01","雨后木质","AFTER THE RAIN",["前调  佛手柑 / 黑胡椒","中调  雪松 / 苔藓","基调  白麝香 / 琥珀"], os.path.join(OLD,"NZ-P1-场景.jpg"), (0.16,0.02,0.86,0.60)),
 ("02","晨露苔原","MORNING MOSS",["前调  湿石 / 青叶","中调  苔藓 / 鸢尾","基调  冷麝香 / 雪松"], os.path.join(OLD,"NZ-P11-冰晶002.jpg"), (0.20,0.10,0.80,0.62)),
]
CW2, CH2, GAP = 470, 760, 40
x0 = (W - (2*CW2+GAP))//2
for i,(no,cn,en,notes,img,cf) in enumerate(cards):
    x = x0 + i*(CW2+GAP); y = 180
    card = Image.new("RGBA",(CW2,CH2),(246,239,226,255)); cd = ImageDraw.Draw(card)
    # 卡片图直接用抠出的瓶子（保证整支完整），002 做冷调
    iw, ih = CW2-52, 430
    box = Image.new("RGB",(iw,ih),(243,236,223))
    _bh = ih - 26
    _bw = max(1, int(BOTTLE.width*_bh/BOTTLE.height))
    _b = BOTTLE.resize((_bw,_bh), Image.LANCZOS)
    if i == 1:  # 002 冷调
        arr = np.asarray(_b).astype(np.float32)
        arr[:,:,0] *= 0.88; arr[:,:,1] *= 0.95; arr[:,:,2] *= 1.10
        arr[:,:,2] = np.clip(arr[:,:,2], 0, 255)
        _b = Image.fromarray(arr.astype(np.uint8), "RGBA")
    box.paste(_b, ((iw-_bw)//2, (ih-_bh)//2), _b)
    card.paste(box,(26,26))
    yy = 476
    for ln in notes:
        cd.text((26, yy), ln, font=S(18), fill=(52,40,28)); yy += 46
    cd.rectangle([CW2-140, 474, CW2-26, 566], outline=(150,120,84), width=2)
    cd.text((CW2-128, 486), no, font=S(56,"Bold"), fill=(40,30,20))
    cd.line([(26, CH2-150),(CW2-26,CH2-150)], fill=(170,145,110), width=1)
    cd.text((26, CH2-126), cn, font=S(30,"Bold"), fill=(34,26,18))
    cd.text((26, CH2-82), en, font=S(14), fill=(120,98,74))
    cd.text((CW2-56, CH2-82), "南\n枝", font=S(16), fill=(150,110,60))
    cv.paste(card,(x,y),card)
d = ImageDraw.Draw(cv)
NY2 = 180+CH2+70
d.line([(M,NY2),(W-M,NY2)], fill=(150,120,84,120), width=1)
d.text((M, NY2+26), "两款香型，同一套瓶型与标签", font=S(34,"Bold"), fill=INK+(252,))
d.text((M, NY2+80), "001 米金暖调，002 冷灰调 —— 只换色，不换形。", font=S(19), fill=SUB+(245,))
d.text((M, NY2+112), "Same flacon, same label grid. Only the glass tint and cap finish change.", font=S(13), fill=(150,126,96,235))
d.text((M, H-56), "NÁNZHĪ · 06", font=S(13), fill=(150,126,96,230))
cv.convert("RGB").save(os.path.join(OUT,"06-香型卡.jpg"), quality=95, optimize=True)
print("06")

# ================= 07 品牌自述 =================
cv = bg_blur(os.path.join(OLD,"NZ-P11-冰晶002.jpg"), blur=30, dark=0.44)
d = ImageDraw.Draw(cv)
tags(d, ["NÁNZHĪ","EAU DE PARFUM","2026","AFTER THE RAIN"], (218,200,172))
d.text((M, 420), "雨停之后，", font=S(60,"Bold"), fill=(244,234,216,255))
d.text((M, 502), "木头才开始说话", font=S(60,"Bold"), fill=(222,196,156,255))
d.text((M, 600), "After the rain stops,", font=S(23), fill=(206,186,158,238))
d.text((M, 636), "the wood starts to speak.", font=S(23), fill=(206,186,158,238))
d.line([(M, 706),(M+140,706)], fill=(190,158,120,210), width=1)
d.text((M, 726), "NÁNZHĪ 品牌自述", font=S(16), fill=(190,168,138,230))
d.text((M, H-216), "不写前调多惊艳 —— 只写半小时后，它还在不在。", font=S(21), fill=(228,210,182,245))
d.text((M, H-178), "We do not write about the opening. We write about what remains.", font=S(14), fill=(184,162,132,220))
d.text((W-M-58, H-56), "07", font=S(15), fill=(150,128,100,210))
cv.convert("RGB").save(os.path.join(OUT,"07-自述.jpg"), quality=95, optimize=True)
print("07")

# ================= 08 冷调单页 =================
cv = grad(W,H,(206,214,220),(120,134,148))
d = ImageDraw.Draw(cv)
tags(d, ["NÁNZHĪ","002 · 晨露苔原","2026","COLD EDITION"])
d.text((M, 150), "晨露苔原", font=S(84,"Bold"), fill=INK+(255,))
d.text((M, 258), "苔藓 · 湿石 · 冷麝香", font=S(26,"Medium"), fill=(70,80,92)+(248,))
d.line([(M, 314),(M+470,314)], fill=(90,102,116)+(180,), width=2)
d.text((M, 346), "同一套瓶型，冷灰玻璃与拉丝银盖。", font=S(20), fill=(66,76,88)+(240,))
d.text((M, 380), "Same flacon. Cool glass, brushed silver cap.", font=S(14), fill=(96,106,118)+(230,))
paste_bottle(cv, 780, W*0.50, 1500, src=BOTTLE_002)
d = ImageDraw.Draw(cv)
d.text((M, H-70), "NÁNZHĪ · 002 · 虚构品牌 · 自主命题方案", font=S(13), fill=(74,84,96)+(230,))
d.text((W-M-58, H-70), "08", font=S(15), fill=(74,84,96)+(230,))
cv.convert("RGB").save(os.path.join(OUT,"08-冷调.jpg"), quality=95, optimize=True)
print("08")

# ================= 09 封底 =================
cv = Image.new("RGB",(W,H),CREAM).convert("RGBA")
d = ImageDraw.Draw(cv)
sect(d, "方法与边界", "METHOD & LIMITS")
blocks = [
 ("01  做法", ["抠瓶 + 单色渐变背景 + 信息排版；全册 9 页共用一套字号与栅格。",
               "抠瓶来自白底主图，瓶型全程不变；背景由代码生成，可换色不换形。"]),
 ("02  参考", ["版式语法参照站酷香水品牌全案：关键词页、分析页、香型卡、自述页。",
               "中英双语、○ 数据条目、比例条、卡片编号 —— 都来自参考作品。"]),
 ("03  边界", ["无真实产品与实拍；瓶身与包装为 AI 生成后抠图合成。",
               "配方比例 30/45/25、留香 6–8 小时、壁厚等参数均为方案设定值，非实测。",
               "未能实现：实体道具摆拍（道具背景不纯，合成后透视与光位对不上）。"]),
]
y = 120
for title, lines in blocks:
    d.text((M, y), title, font=S(24,"Medium"), fill=GOLD+(250,))
    yy = y+42
    for ln in lines:
        cur = ""; 
        for ch in ln:
            if d.textlength(cur+ch, font=S(19)) > 1000 and ch not in "，。；：":
                d.text((M, yy), cur, font=S(19), fill=INK+(245,)); yy += 32; cur = ch
            else: cur += ch
        if cur: d.text((M, yy), cur, font=S(19), fill=INK+(245,)); yy += 32
    y = yy + 40
d.line([(M, y),(W-M,y)], fill=(170,144,110), width=1)
for i,(v,k) in enumerate([("9","页成品"),("1","套瓶型"),("2","种香型"),("0","编造数据")]):
    x0 = M + i*268
    d.text((x0, y+34), v, font=S(52,"Bold"), fill=GOLD+(252,))
    d.text((x0, y+100), k, font=S(16), fill=SUB+(240,))
paste_bottle(cv, 700, W*0.50, 1545)
d = ImageDraw.Draw(cv)
d.text((M, H-56), "NÁNZHĪ · 虚构品牌 · 自主命题方案 · 2026", font=S(13), fill=(150,126,96,230))
d.text((W-M-58, H-56), "09", font=S(15), fill=(150,126,96,230))
cv.convert("RGB").save(os.path.join(OUT,"09-封底.jpg"), quality=95, optimize=True)
print("09")
print("全部完成 →", OUT)
