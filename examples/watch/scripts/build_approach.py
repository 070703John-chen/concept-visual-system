# -*- coding: utf-8 -*-
"""00 设计思路页（方法论页）—— 书面语体重写版"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw
from kit import S, rgb

from cfg import ASSETS as A
from cfg import OUT as OUT
W, H, M = 1200, 1600, 60
BG = "#0E0B08"
INK, SUB, GOLD = "#EFE3CE", "#8A7358", "#C08A4A"

cv = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(cv)
d.text((M, 44), "GUĀNSHÍ", font=S(19, "Medium"), fill=rgb(GOLD))
bw = d.textlength("GUĀNSHÍ", font=S(19, "Medium"))
d.text((M+bw+4, 39), "™", font=S(10, "Medium"), fill=rgb(GOLD))
d.text((M+bw+18, 47), "·  APPROACH", font=S(12, "Medium"), fill=rgb(SUB))
d.text((M, 88), "设计思路", font=S(46, "Bold"), fill=rgb(INK))
d.text((M, 150), "自命题概念设计 · 方法与边界", font=S(18), fill=rgb(SUB))
d.rectangle([M, 194, W-M, 195], fill=rgb("#2E2318"))

# 01 项目目标
Y = 216
d.text((M, Y), "01  项目目标", font=S(20, "Medium"), fill=rgb(GOLD))
for i, ln in enumerate(["自命题项目：为虚构腕表品牌建立完整视觉系统，共 17 页。",
                        "内容覆盖产品主张、结构、材料、参数与使用场景。"]):
    d.text((M, Y+32+i*27), ln, font=S(17), fill=rgb(INK))

# 02 目标用户与决策条件
Y = 312
d.text((M, Y), "02  目标用户与决策条件", font=S(20, "Medium"), fill=rgb(GOLD))
rows = [("人群", "24–30 岁，首次购买正装表，预算 2000–4000 元"),
        ("购买动因", "通勤与正式场合的着装完整度，非收藏用途"),
        ("浏览场景", "移动端 0.5–1 秒（信息流）；桌面端 60 秒（提案浏览）"),
        ("决策障碍", "尺寸是否合腕、价格是否匹配、参数是否可信")]
yy = Y+32
for k, v in rows:
    d.text((M, yy), k, font=S(16), fill=rgb(SUB))
    d.text((M+150, yy-2), v, font=S(17), fill=rgb(INK))
    yy += 30

# 03 图位规划
Y = 482
d.text((M, Y), "03  图位规划", font=S(20, "Medium"), fill=rgb(GOLD))
d.text((M+130, Y+4), "一页对应一个问题；页数在立项时锁定", font=S(14), fill=rgb("#6E5A42"))
grid = [("01","封面","主张"),("02","表径 38","取舍"),("03","镂空盘面","原理"),("04","材料与工艺","材料"),
        ("05","机芯五件事","结构"),("06","动力储存","性能"),("07","三处尺寸","规格"),("08","厚度","结构"),
        ("09","五种表面","变体"),("10","场景","环境"),("11","微距","细节"),("12","封底","边界")]
gx, gy = M, Y+40
cw, chh = 258, 58
for i,(no, name, role) in enumerate(grid):
    x = gx + (i%4)*(cw+8); y = gy + (i//4)*(chh+8)
    d.rectangle([x, y, x+cw, y+chh], fill=("#1A1612" if i%2==0 else "#15120E"), outline="#2E2318", width=1)
    d.text((x+12, y+8), no, font=S(14, "Bold"), fill=rgb(GOLD))
    d.text((x+44, y+5), name, font=S(16, "Medium"), fill=rgb(INK))
    d.text((x+44, y+30), role, font=S(13), fill=rgb(SUB))

# 04 视觉系统
Y = 768
d.text((M, Y), "04  视觉系统", font=S(20, "Medium"), fill=rgb(GOLD))
d.text((M, Y+30), "主色", font=S(15), fill=rgb(SUB))
sw = [("#231A12","墨"),("#8A5A2B","铜"),("#C08A4A","金"),("#6B5947","褐"),("#E8DCC8","纸")]
for i,(hx,nm) in enumerate(sw):
    x = M+70+i*96
    d.rectangle([x, Y+26, x+56, Y+82], fill=rgb(hx), outline="#2E2318", width=1)
    d.text((x, Y+88), nm, font=S(13), fill=rgb(SUB))
    d.text((x, Y+106), hx.upper(), font=S(11), fill=rgb("#6E5A42"))

d.text((M, Y+146), "字体", font=S(15), fill=rgb(SUB))
d.text((M+70, Y+142), "思源宋体（Noto Serif SC）单一家族", font=S(17), fill=rgb(INK))
d.text((M, Y+182), "字号", font=S(15), fill=rgb(SUB))
d.text((M+70, Y+178), "四档：46 / 26 / 17 / 13，不混用", font=S(17), fill=rgb(INK))
d.text((M, Y+218), "栅格", font=S(15), fill=rgb(SUB))
d.text((M+70, Y+214), "边距 60；单栏 1080；图块间距 12", font=S(17), fill=rgb(INK))
d.text((M, Y+254), "调色", font=S(15), fill=rgb(SUB))
d.text((M+70, Y+250), "黑位 3% / 高光 97%；左上主光；暗角 22%；锐化 48%", font=S(17), fill=rgb(INK))

# 05 交付清单
Y = 1066
d.text((M, Y), "05  交付清单", font=S(20, "Medium"), fill=rgb(GOLD))
d.rectangle([M, Y+36, W-M, Y+37], fill=rgb("#2E2318"))
items = [("17", "成品页 1200×1600"), ("2", "生成引擎（即梦 / MiniMax）"),
         ("1", "SOP 与图位矩阵"), ("0", "编造数据（全部标注设定值）")]
for i,(v,k) in enumerate(items):
    x0 = M + i*258
    d.text((x0, Y+58), v, font=S(38, "Bold"), fill=rgb(GOLD))
    d.text((x0, Y+110), k, font=S(14), fill=rgb(SUB))

# 06 已知限制
Y = 1216
d.text((M, Y), "06  已知限制", font=S(20, "Medium"), fill=rgb(GOLD))
for i, ln in enumerate(["AI 生成无法保证同一产品的多角度一致性；概念与场景页均标注“概念演绎”。",
                        "参数、工艺与使用数据为方案设定值，非实测；实际产品须以出厂检测为准。",
                        "无真实产品与实拍摄影；渲染质感与 3D 建模作品存在差距。"]):
    d.text((M, Y+32+i*27), ln, font=S(16), fill=rgb(SUB))

# 07 下一步
Y = 1352
d.text((M, Y), "07  下一步", font=S(20, "Medium"), fill=rgb(GOLD))
for i, ln in enumerate(["补 3D 建模或外包渲染，解决多角度一致（唯一硬差距）。",
                        "增加第二品类，验证方法论可迁移性。"]):
    d.text((M, Y+32+i*27), ln, font=S(16), fill=rgb(SUB))

d.text((M, H-38), "虚构品牌 · 自主命题 · 2026", font=S(12), fill=rgb("#6E5A42"))
d.text((W-M-56, H-38), "17 / 17", font=S(13), fill=rgb("#6E5A42"))
_rgb = Image.new("RGB", (W, H), rgb(BG))
_rgb.paste(cv, (0,0), cv)
_rgb.save(os.path.join(OUT, "00-approach.jpg"), quality=95, optimize=True)
V7 = OUT
cv.save(os.path.join(V7, "00-approach.png"))
print("00 approach rewritten (written register)")
