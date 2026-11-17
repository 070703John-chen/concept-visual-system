# -*- coding: utf-8 -*-
"""南枝 v3：12 页 = 新版 8 页 + 原版 4 张（旧图新装）"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from kit import S

from cfg import ASSETS as A, OUT as OUT   # noqa: E402
V2 = OUT      # 上一阶段产物（build_pages.py 的输出）
OLD = A       # 原片
NEW = A       # 新素材
OUT_FINAL = os.path.join(OUT, "final")
os.makedirs(OUT_FINAL, exist_ok=True)
OUT = OUT_FINAL
W, H, M = 1200, 1600, 72
def cutout_bottle():
    from collections import deque
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



def copy_page(src, dst):
    Image.open(src).convert("RGB").save(os.path.join(OUT,dst), quality=95, optimize=True)
    print("复制", dst)

# 新版 8 页直接沿用（已定稿）
copy_page(os.path.join(V2,"01-封面.jpg"), "01-封面.jpg")
copy_page(os.path.join(V2,"03-香调分析.jpg"), "02-香调分析.jpg")
copy_page(os.path.join(V2,"04-材料.jpg"), "03-材料.jpg")
copy_page(os.path.join(V2,"05-信息.jpg"), "04-信息.jpg")
copy_page(os.path.join(V2,"06-香型卡.jpg"), "05-香型卡.jpg")

INK, SUB, GOLD = (34,26,18), (100,82,58), (152,108,58)
CREAM = (238,230,214)

def tags(d, items, color=INK, y=44):
    x = M
    for t in items:
        d.text((x, y), "◆ " + t, font=S(13), fill=color+(225,))
        x += d.textlength("◆ "+t, font=S(13)) + 22
    d.line([(M, y+30),(W-M,y+30)], fill=(150,120,84,120), width=1)

def sect(d, cn, en, y=54):
    d.text((M, y), "●", font=S(13), fill=GOLD+(240,))
    d.text((M+24, y-8), cn, font=S(22,"Medium"), fill=INK+(250,))
    tw = d.textlength(en, font=S(12))
    d.text((W-M-tw, y), en, font=S(12), fill=(150,126,96,230))
    d.line([(M, y+30),(W-M,y+30)], fill=(160,134,100,150), width=1)

def crop_frac(im, f):
    w,h = im.size
    return im.crop((int(w*f[0]), int(h*f[1]), int(w*f[2]), int(h*f[3])))

# ================= 06 对比（原 P4 两张图，旧图新装） =================
base = Image.open(os.path.join(OLD,"NZ-P4-对比.jpg")).convert("RGB")
warm = crop_frac(base, (0.025, 0.175, 0.490, 0.495))
cool = crop_frac(base, (0.510, 0.175, 0.975, 0.495))

cv = Image.new("RGB",(W,H),CREAM).convert("RGBA")
d = ImageDraw.Draw(cv)
sect(d, "两种光", "TWO LIGHTS")
d.text((M, 104), "同一配方，两种情境。", font=S(34,"Bold"), fill=INK+(252,))
d.text((M, 152), "选哪一版，取决于你想让人在什么时刻想起它。", font=S(20), fill=SUB+(245,))

tw2, th2 = 510, 470
for i,(im,cap,note) in enumerate([(warm,"暖调 · 傍晚","1800–2700 K　光从侧面进来"),
                                 (cool,"冷调 · 清晨","5600 K 以上　光从正面压过来")]):
    x = M + i*(tw2+18); y = 210
    sc = max(tw2/im.width, th2/im.height)
    im2 = im.resize((int(im.width*sc)+1,int(im.height*sc)+1), Image.LANCZOS)
    im2 = im2.crop(((im2.width-tw2)//2,(im2.height-th2)//2,(im2.width-tw2)//2+tw2,(im2.height-th2)//2+th2))
    cv.paste(im2,(x,y))
    dd = ImageDraw.Draw(cv)
    dd.text((x, y+th2+16), cap, font=S(26,"Medium"), fill=INK+(250,))
    dd.text((x, y+th2+54), note, font=S(15), fill=SUB+(235,))

d = ImageDraw.Draw(cv)
NY = 210+th2+140
d.line([(M,NY),(W-M,NY)], fill=(170,144,110), width=1)
d.text((M, NY+28), "光决定它像什么", font=S(30,"Bold"), fill=INK+(252,))
for i,ln in enumerate(["同一个瓶、同一配方，换光源就能从“夜晚”变成“清晨”。",
                       "暖光下琥珀色偏橙，冷光下偏灰 —— 这是玻璃厚度造成的折射差。"]):
    d.text((M, NY+80+i*34), ln, font=S(19), fill=SUB+(245,))
d.text((M, NY+160), "Same flacon, two lighting setups. Glass thickness bends warm and cool light differently.", font=S(13), fill=(150,126,96,235))

# 对照表
TY = NY + 210
d.line([(M,TY),(W-M,TY)], fill=(170,144,110), width=1)
hdr = [("", 0), ("暖调 · 傍晚", 420), ("冷调 · 清晨", 740)]
for t,x in hdr:
    if t: d.text((M+x, TY+18), t, font=S(16,"Medium"), fill=GOLD+(245,))
rows = [("色温","1800–2700 K","5600 K 以上"),
        ("主光方向","侧面 · 低位","正面 · 高位"),
        ("玻璃观感","琥珀偏橙","灰白偏蓝"),
        ("适合场景","夜晚 · 室内 · 赠礼","清晨 · 通勤 · 自用")]
for i,(k,a,b) in enumerate(rows):
    y = TY + 56 + i*44
    d.text((M, y), k, font=S(16), fill=SUB+(235,))
    d.text((M+420, y), a, font=S(17), fill=INK+(248,))
    d.text((M+740, y), b, font=S(17), fill=INK+(248,))
    d.line([(M,y+34),(W-M,y+34)], fill=(200,180,152), width=1)
d.text((M, H-56), "NÁNZHĪ · 06", font=S(13), fill=(150,126,96,230))
d.text((W-M-58, H-56), "06", font=S(15), fill=(150,126,96,230))
cv.convert("RGB").save(os.path.join(OUT,"06-两种光.jpg"), quality=95, optimize=True)
print("06 两种光")

# ================= 07 冷调（新版 08-冷调） =================
copy_page(os.path.join(V2,"08-冷调.jpg"), "07-冷调002.jpg")

# ================= 08 冰晶（原 P11，旧图新装） =================
src = Image.open(os.path.join(OLD,"NZ-P11-冰晶002.jpg")).convert("RGB")
photo = crop_frac(src, (0.0, 0.0, 1.0, 0.615))
cv = Image.new("RGB",(W,H),CREAM).convert("RGBA")
ph = photo.resize((W, int(photo.height*W/photo.width)), Image.LANCZOS)
cv.paste(ph,(0,0))
d = ImageDraw.Draw(cv)
d.text((M, H-560), "苔原 · 冰光", font=S(52,"Bold"), fill=INK+(255,))
d.text((M, H-486), "002 冷调版本，同一支瓶。", font=S(22), fill=SUB+(248,))
d.line([(M, H-436),(M+420, H-436)], fill=GOLD+(170,), width=2)
for i,ln in enumerate(["冰面反射 8000 K 以上的冷光，玻璃边沿发蓝。",
                       "香调：湿石 / 青叶 / 苔藓 / 鸢尾 / 冷麝香 / 雪松。"]):
    d.text((M, H-404+i*32), ln, font=S(19), fill=SUB+(245,))
d.text((M, H-320), "Ice surface reflects light above 8000 K; the glass edge turns blue.", font=S(13), fill=(150,126,96,235))
d.line([(M, H-270),(W-M, H-270)], fill=(170,144,110), width=1)
for i,(v,k) in enumerate([("002","型号"),("50","ML"),("12","% EDP"),("6–8","小时")]):
    x0 = M + i*268
    d.text((x0, H-240), v, font=S(34,"Bold"), fill=GOLD+(250,))
    d.text((x0, H-188), k, font=S(14), fill=SUB+(235,))
d.text((M, H-56), "NÁNZHĪ · 08", font=S(13), fill=(150,126,96,230))
d.text((W-M-58, H-56), "08", font=S(15), fill=(150,126,96,230))
cv.convert("RGB").save(os.path.join(OUT,"08-冰晶.jpg"), quality=95, optimize=True)
print("08 冰晶")

# ================= 09 灵感溯源（原文案，新版式 + 抠瓶） =================
cv = Image.new("RGB",(W,H),CREAM).convert("RGBA")
d = ImageDraw.Draw(cv)
sect(d, "灵感溯源", "INSPIRATION")
d.text((M, 132), "雨停之后，", font=S(50,"Bold"), fill=INK+(252,))
d.text((M, 200), "木头和空气都还在滴水。", font=S(50,"Bold"), fill=INK+(252,))
d.text((M, 300), "想把那一口呼吸装进瓶子里 ——", font=S(24), fill=SUB+(248,))
d.text((M, 338), "于是有了雪松压住苔藓，白麝香在最后浮上来。", font=S(24), fill=SUB+(248,))
d.line([(M, 404),(M+200,404)], fill=GOLD+(180,), width=2)
d.text((M, 424), "After the rain, both the wood and the air keep dripping.", font=S(14), fill=(150,126,96,235))
d.text((M, 446), "We tried to bottle that one breath.", font=S(14), fill=(150,126,96,235))

# 抠瓶（同一支，无白底）
_bh = 620; _bw = int(BOTTLE.width*_bh/BOTTLE.height)
_b = BOTTLE.resize((_bw,_bh), Image.LANCZOS)
_bx = W - M - _bw; _by = 500
sh = Image.new("RGBA",(int(_bw*2.0), int(_bh*0.3)),(0,0,0,0))
yy_,xx_ = np.mgrid[0:sh.height, 0:sh.width].astype(np.float32)
ex = ((xx_-sh.width/2)/(sh.width/2))**2; ey = ((yy_-sh.height/2)/(sh.height/2))**2
fall = np.clip(1.0-(ex*0.75+ey*0.9),0,1)**2.2
arr = np.zeros((sh.height, sh.width, 4), dtype=np.uint8)
arr[:,:,0]=88; arr[:,:,1]=70; arr[:,:,2]=52; arr[:,:,3]=(fall*100).astype(np.uint8)
cv.paste(Image.fromarray(arr,"RGBA"), (_bx+_bw//2-sh.width//2, _by+_bh-40), Image.fromarray(arr,"RGBA"))
cv.paste(_b, (_bx,_by), _b)

d = ImageDraw.Draw(cv)
TY = 1180
d.line([(M,TY),(W-M,TY)], fill=(170,144,110), width=1)
d.text((M, TY+22), "三条来源，一句一条", font=S(24,"Medium"), fill=INK+(250,))
srcs = [("雨","水汽压低前调，让佛手柑只留一点涩"),
        ("雪松","木质决定主体，占比 45%"),
        ("白麝香","收尾贴皮，留香最后 2 小时")]
for i,(k,v) in enumerate(srcs):
    x = M + i*356
    d.text((x, TY+70), k, font=S(22,"Bold"), fill=GOLD+(250,))
    cur=""; yy2=TY+108
    for ch in v:
        if d.textlength(cur+ch, font=S(15)) > 330 and ch not in "，。":
            d.text((x, yy2), cur, font=S(15), fill=SUB+(240,)); yy2+=24; cur=ch
        else: cur += ch
    if cur: d.text((x, yy2), cur, font=S(15), fill=SUB+(240,))
d.text((M, H-56), "NÁNZHĪ · 09", font=S(13), fill=(150,126,96,230))
d.text((W-M-58, H-56), "09", font=S(15), fill=(150,126,96,230))
cv.convert("RGB").save(os.path.join(OUT,"09-灵感溯源.jpg"), quality=95, optimize=True)
print("09 灵感溯源")

# ================= 10 自述（新版 07） =================
copy_page(os.path.join(V2,"07-自述.jpg"), "10-自述.jpg")
# ================= 11 封底（新版 09） =================
copy_page(os.path.join(V2,"09-封底.jpg"), "11-封底.jpg")

# ================= 12 附：原版封面 =================
cv = Image.new("RGB",(W,H),(232,224,210)).convert("RGBA")
d = ImageDraw.Draw(cv)
d.text((M, 52), "◆ 附　上一版封面", font=S(14), fill=INK+(230,))
d.line([(M, 84),(W-M,84)], fill=(150,120,84,120), width=1)
old = Image.open(os.path.join(OLD,"NZ-封面-极简.jpg")).convert("RGB")
sh = 1080; sw = int(old.width*sh/old.height)
old2 = old.resize((sw,sh), Image.LANCZOS)
px = (W-sw)//2; py = 150
# 阴影
shadow = Image.new("RGBA",(sw+60, sh+60),(0,0,0,0))
sd = ImageDraw.Draw(shadow)
sd.rectangle([30,30,sw+30,sh+30], fill=(120,104,84,110))
shadow = shadow.filter(ImageFilter.GaussianBlur(18))
cv.paste(shadow,(px-30, py-10), shadow)
cv.paste(old2,(px,py))
d = ImageDraw.Draw(cv)
d.text((M, py+sh+40), "2026-11-10 版封面：白底 + 巨字水印 + 瓶身占满", font=S(19), fill=SUB+(245,))
d.text((M, py+sh+74), "留作对照 —— 新版换成了渐变底、缩小瓶身、加参数行。", font=S(19), fill=SUB+(245,))
d.text((M, H-56), "NÁNZHĪ · 附 · 12", font=S(13), fill=(150,126,96,230))
cv.convert("RGB").save(os.path.join(OUT,"12-附原版封面.jpg"), quality=95, optimize=True)
print("12 附原版封面")
print("完成 →", OUT)
