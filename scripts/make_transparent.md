# 页面透明化改造要点

> 目标：让每一页的**背景透明**，这样它们才能叠在同一张连续背景上。
> 不改造直接拼，长图会出现一页一页的矩形硬边。

---

## 一、如果你用代码画页面

只改三处：

```python
# ① 画布换成 RGBA，背景全透明
cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))   # 原来是 RGB + 底色

# ② 全局压黑不要"刷满"，要用带 alpha 的渐变
m = Image.new("L", (1, height))
for i in range(height):
    m.putpixel((0, i), int(255 * (1 - i / (height - 1)) ** 1.2))
band = Image.new("RGBA", (W, height), (14, 11, 8, 255))
band.putalpha(m.resize((W, height)))
cv.paste(band, (0, 0), band)                   # 注意：band 用自己当 mask

# ③ 保存为 PNG（JPEG 不支持透明）
cv.save(out + ".png")
```

---

## 二、如果页面是别人给的 jpg

不用改造，合成时走"边缘羽化"分支：

```python
def feather(im, px=60):
    w, h = im.size
    m = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(m)
    for i in range(px):
        v = int(255 * i / px)
        d.line([(0, i), (w, i)], fill=v)
        d.line([(0, h - 1 - i), (w, h - 1 - i)], fill=v)
    im = im.convert("RGBA"); im.putalpha(m)
    return im
```

**只羽化上下边**（左右本来就要贴到画布边缘），不要四边都羽化，否则左右会出现暗边。

---

## 三、三个必须注意的细节

**① 带 alpha 的色块贴在透明画布上会变成"脏斑"**
```
错误   cv.paste(Image.new("RGBA", size, (86,54,26,255)).putalpha(glow))  # 整块褐色
正确   把色块放在图片之后，用图片的颜色托住；或干脆不要局部光晕，交给连续背景
```

**② 图内渐变要跟着图走，不要跟着画布走**
```
文字压在图上时，渐变的高度 = 图的高度，不是画布高度
```

**③ 裁边要裁"透明边"，不是固定比例**
```python
bb = im.getbbox()          # 内容包围盒
im = im.crop((0, bb[1], W, bb[3]))   # 只裁上下，左右保留原宽以对齐栅格
```

---

## 四、验证清单

```
□ 每页都是 RGBA，四个角像素 alpha = 0
□ 页面里没有"整块底色"（用 getbbox 看内容范围是否异常）
□ 两张相邻页叠在纯色上时，边界处没有矩形色差
□ 合成后长图里，页面之间只有 20px 的连续背景，没有硬线
```
