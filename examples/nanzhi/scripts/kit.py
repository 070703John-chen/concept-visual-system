# -*- coding: utf-8 -*-
"""元素组件库（信息图形）：图标 / 徽章 / 对比条 / 色卡 / 流程 / 材质圆 / 缩略条 / 环图
所有函数返回绘制后的 Image 或直接在传入的 draw 上绘制，坐标为绝对像素。
"""
import math
from PIL import Image, ImageDraw, ImageFont

SERIF = r"C:\Windows\Fonts\NotoSerifSC-VF.ttf"
INK, SUB, GOLD, LINE = "#EFE3CE", "#8A7358", "#C08A4A", "#2E2318"

def S(sz, w="Regular"):
    f = ImageFont.truetype(SERIF, sz)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f

def rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# ---------- 线性图标（36–40px 画法，内部按 size 缩放） ----------
def icon(d, kind, x, y, size=40, col=GOLD, w=2):
    k = size/40.0
    def sc(*v): return [x + a*k for a in v]
    c = rgb(col) if isinstance(col, str) else col
    if kind == "sapphire":      # 菱形 + 内框
        d.polygon([ (x+20*k, y+4*k), (x+36*k, y+20*k), (x+20*k, y+36*k), (x+4*k, y+20*k) ], outline=c, width=w)
        d.polygon([ (x+20*k, y+13*k), (x+27*k, y+20*k), (x+20*k, y+27*k), (x+13*k, y+20*k) ], outline=c, width=1)
    elif kind == "water":       # 水滴
        d.arc(sc(10,14,30,38), 200, 340, fill=c, width=w)
        d.line([(x+20*k, y+4*k), (x+11*k, y+22*k)], fill=c, width=w)
        d.line([(x+20*k, y+4*k), (x+29*k, y+22*k)], fill=c, width=w)
        d.arc(sc(12,20,28,36), 0, 180, fill=c, width=w)
    elif kind == "auto":        # 循环箭头
        d.arc(sc(6,8,34,36), 30, 300, fill=c, width=w)
        d.polygon([(x+32*k,y+10*k),(x+36*k,y+18*k),(x+27*k,y+16*k)], fill=c)
    elif kind == "gear":        # 镂空齿轮
        d.ellipse(sc(10,10,30,30), outline=c, width=w)
        d.ellipse(sc(17,17,23,23), outline=c, width=1)
        for a in range(0, 360, 45):
            r1, r2 = 10*k, 14*k
            x1 = x+20*k + r1*math.cos(math.radians(a)); y1 = y+20*k + r1*math.sin(math.radians(a))
            x2 = x+20*k + r2*math.cos(math.radians(a)); y2 = y+20*k + r2*math.sin(math.radians(a))
            d.line([(x1,y1),(x2,y2)], fill=c, width=w)
    elif kind == "crown":       # 表冠（滚花圆）
        d.ellipse(sc(12,12,28,28), outline=c, width=w)
        for a in range(0, 360, 30):
            r = 8*k
            x1 = x+20*k + r*math.cos(math.radians(a)); y1 = y+20*k + r*math.sin(math.radians(a))
            x2 = x+20*k + 10*k*math.cos(math.radians(a)); y2 = y+20*k + 10*k*math.sin(math.radians(a))
            d.line([(x1,y1),(x2,y2)], fill=c, width=1)
    elif kind == "leather":     # 皮革（虚线缝）
        d.rounded_rectangle(sc(6,12,34,28), radius=4*k, outline=c, width=w)
        for i in range(9, 33, 5):
            d.line([(x+i*k, y+12*k),(x+i*k, y+28*k)], fill=c, width=1)
    elif kind == "lume":        # 夜光（星）
        d.line([(x+20*k,y+6*k),(x+20*k,y+34*k)], fill=c, width=w)
        d.line([(x+6*k,y+20*k),(x+34*k,y+20*k)], fill=c, width=w)
        d.line([(x+11*k,y+11*k),(x+29*k,y+29*k)], fill=c, width=1)
        d.line([(x+29*k,y+11*k),(x+11*k,y+29*k)], fill=c, width=1)
    elif kind == "shield":
        d.line([(x+20*k,y+4*k),(x+34*k,y+10*k)], fill=c, width=w)
        d.line([(x+20*k,y+4*k),(x+6*k,y+10*k)], fill=c, width=w)
        d.line([(x+6*k,y+10*k),(x+6*k,y+22*k)], fill=c, width=w)
        d.line([(x+34*k,y+10*k),(x+34*k,y+22*k)], fill=c, width=w)
        d.arc(sc(6,16,34,36), 0, 180, fill=c, width=w)
    elif kind == "ruler":
        d.rectangle(sc(6,16,34,26), outline=c, width=w)
        for i in range(10, 34, 6):
            d.line([(x+i*k,y+16*k),(x+i*k,y+21*k)], fill=c, width=1)
    elif kind == "clock":
        d.ellipse(sc(6,6,34,34), outline=c, width=w)
        d.line([(x+20*k,y+20*k),(x+20*k,y+11*k)], fill=c, width=w)
        d.line([(x+20*k,y+20*k),(x+27*k,y+23*k)], fill=c, width=w)

def icon_row(d, items, x, y, gap=132, size=34, label_size=15):
    """items: [(kind, label), ...] 线性图标 + 下方小字"""
    for i, (kind, label) in enumerate(items):
        cx = x + i*gap
        icon(d, kind, cx, y, size)
        d.text((cx, y+size+10), label, font=S(label_size), fill=rgb(SUB))

# ---------- 徽章 ----------
def badge(d, text, x, y, size=14, col=GOLD, bg=None, padx=12, pady=7):
    w = d.textlength(text, font=S(size, "Medium"))
    box = [x, y, x+w+padx*2, y+size+pady*2]
    if bg: d.rectangle(box, fill=rgb(bg))
    d.rectangle(box, outline=rgb(col), width=1)
    d.text((x+padx, y+pady-2), text, font=S(size, "Medium"), fill=rgb(col))
    return box[2]-box[0]

# ---------- 水平对比条 ----------
def compare_bars(d, rows, x, y, width=560, rowh=46, maxv=None, labelw=170):
    """rows: [(label, value, col, suffix)]"""
    maxv = maxv or max(r[1] for r in rows)*1.25
    for i,(label, val, col, suf) in enumerate(rows):
        yy = y + i*rowh
        d.text((x, yy+8), label, font=S(15), fill=rgb(SUB))
        bl = int(width * val/maxv)
        d.rectangle([x+labelw, yy+10, x+labelw+bl, yy+26], fill=rgb(col))
        d.text((x+labelw+bl+10, yy+7), f"{val}{suf}", font=S(16, "Medium"), fill=rgb(INK))

# ---------- 色卡 ----------
def swatches(d, cols, x, y, size=54, gap=16, show_hex=True):
    """cols: [(hex, name)]"""
    for i,(hx, name) in enumerate(cols):
        cx = x + i*(size+gap)
        d.rectangle([cx, y, cx+size, y+size], fill=rgb(hx), outline="#C9B99F", width=1)
        if show_hex:
            d.text((cx, y+size+8), hx.upper(), font=S(12), fill=rgb(SUB))
            d.text((cx, y+size+26), name, font=S(13), fill=rgb(INK))

# ---------- 流程 ----------
def flow(d, steps, x, y, gap=150, size=13):
    for i, s in enumerate(steps):
        cx = x + i*gap
        d.ellipse([cx, y, cx+30, y+30], outline=rgb(GOLD), width=2)
        t = str(i+1)
        tw = d.textlength(t, font=S(14, "Bold"))
        d.text((cx+15-tw/2, y+7), t, font=S(14, "Bold"), fill=rgb(GOLD))
        d.text((cx-4, y+40), s, font=S(size), fill=rgb(SUB))
        if i < len(steps)-1:
            d.line([(cx+36, y+15), (cx+gap-10, y+15)], fill="#C9B99F", width=1)
            d.polygon([(cx+gap-10, y+15),(cx+gap-18, y+11),(cx+gap-18, y+19)], fill=rgb("#C9B99F"))

# ---------- 材质圆（小样） ----------
def material_dots(cv, items, x, y, r=44, gap=118):
    """items: [(path, crop_center_frac(x,y), label)]"""
    for i,(path, (fx, fy), label) in enumerate(items):
        im = Image.open(path).convert("RGB")
        s = int(r*2*1.6)
        left = max(0, min(im.width-s, int(im.width*fx - s/2)))
        top  = max(0, min(im.height-s, int(im.height*fy - s/2)))
        crop = im.crop((left, top, left+s, top+s)).resize((r*2, r*2), Image.LANCZOS)
        mask = Image.new("L", (r*2, r*2), 0)
        ImageDraw.Draw(mask).ellipse([0,0,r*2,r*2], fill=255)
        cx = x + i*gap
        cv.paste(crop, (cx, y), mask)

# ---------- 环图 ----------
def ring(d, pct, x, y, r=42, col=GOLD, label=""):
    d.arc([x-r, y-r, x+r, y+r], 0, 360, fill="#DED2BE", width=9)
    d.arc([x-r, y-r, x+r, y+r], -90, -90+int(360*pct), fill=rgb(col), width=9)
    t = f"{int(pct/3.6)}%"
    tw = d.textlength(t, font=S(18, "Medium"))
    d.text((x-tw/2, y-12), t, font=S(18, "Medium"), fill=rgb(INK))
    if label:
        d.text((x-30, y+r+10), label, font=S(13), fill=rgb(SUB))

# ---------- 缩略条 ----------
def thumbs(cv, items, x, y, w=132, h=132, gap=12):
    """items: [(path, caption)]"""
    for i,(path, cap) in enumerate(items):
        im = Image.open(path).convert("RGB")
        sc = max(w/im.width, h/im.height)
        im2 = im.resize((int(im.width*sc)+1, int(im.height*sc)+1), Image.LANCZOS)
        cx_, cy_ = (im2.width-w)//2, (im2.height-h)//2
        cv.paste(im2.crop((cx_, cy_, cx_+w, cy_+h)), (x+i*(w+gap), y))
        d = ImageDraw.Draw(cv)
        d.rectangle([x+i*(w+gap), y, x+i*(w+gap)+w, y+h], outline="#C9B99F", width=1)
        d.text((x+i*(w+gap), y+h+8), cap, font=S(13), fill=rgb(SUB))

# ---------- 版块标题 ----------
def section(d, title, x, y, note=None, width=1056):
    d.text((x, y), title, font=S(22, "Medium"), fill=rgb(INK))
    if note:
        tw = d.textlength(title, font=S(22, "Medium"))
        d.text((x+tw+14, y+6), note, font=S(14), fill=rgb("#9C8B75"))
    d.line([(x, y+38), (x+width, y+38)], fill=rgb(LINE), width=1)
    return y+56
