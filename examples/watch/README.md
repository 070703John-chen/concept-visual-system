# 示例一：观时 GUĀNSHÍ（暗调腕表 · 16 页）

**这条命令能在这台机器之外复现同一套页面。**

```bash
cd examples/watch
python scripts/preflight.py --out-dir ./out     # 环境自检
python scripts/run_all.py                       # 16 页 + 长图
```

产物在 `out/`：16 张页面 + `长图.jpg`（1200×25192）+ `长图-网页版.jpg`。

---

## 目录

```
config.json          色板 / 字号 / 画布 / 路径 / 文案（改这些不用碰脚本）
assets/              41 张素材（已压到 1200 宽 / q85，共 4.7 MB）
scripts/
  cfg.py             读 config.json，给出 ASSETS 与 OUT
  kit.py             字体 / 配色 / 图形组件（S() 取字体，rgb() 转色值）
  build_layout.py    01 02 04 05 06 07 09 10
  build_rules.py     03 08
  build_fill.py      05 12
  build_kv2.py       03（倒影 + 光晕）
  build_fix_4_11.py  04 11
  build_merge.py     07 11
  build_scenes2.py   10 13
  build_extra.py     14 字与格 / 15 黑白
  build_approach.py  00 设计思路（放最后）
  run_all.py         一键：逐页 → 长图 → 切回单页 → 页数校验
out/                 产物（git 已忽略）
```

---

## 改东西改哪里

| 想改 | 改哪 |
|---|---|
| 色板 | `config.json` → `palette`（注意：脚本里仍有字面量，见下方"已知限制"） |
| 字号 | `config.json` → `type` |
| 画布尺寸 | `config.json` → `canvas` |
| 某一页的文案 | 对应 `build_*.py` 里的 `d.text(...)` |
| 加一页 | 复制最接近的页面函数，改坐标与文案，然后加进 `run_all.py` 的 `ORDER` 与 `LONG_ORDER` |

---

## 已知限制（路线 1.5 的范围）

```
① 文案仍是脚本里的字面量
   config.json 的 copy 字段是"唯一真源清单"，但尚未接线
   改文案目前要改脚本 —— 这是为了保住"定稿就是这套代码跑出来的"这条事实

② 布局坐标不抽配置
   水印位置、标签框比例、封底瓶高这些参数是被验证过的，抽出来容易走样

③ 页数 16，不是定稿的 17
   少的是「作品集封面」（那张纯字体封面来自另一个项目目录）
```

---

## 复现核对表

跑完应该看到：

```
[1/2] 逐页生成    9 个脚本全 OK
[2/2] 合成连续背景长图
长图 1200×25192
页数 16（配置写的 16）
完成。产物在 out/ 目录
```

若页数不符，`run_all.py` 会直接失败并提示改 `config.json` 的 `pages`
——**不会静默少页**（这是踩过的坑）。
