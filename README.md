# concept-visual-system

**一套把「N 张各自还行的图」做成「一个品牌」的流程。**

不是提示词库，也不是模板合集。它是一份可执行的工作手册 + 三个能真跑的脚本：
从输入契约、图位矩阵，到统一调色、连续背景长图，再到交付前的机器自检。

> 来自两次真实交付：一个虚构腕表品牌（暗调，17 页 + 1200×25438 长图）、
> 一个虚构香水品牌（亮调，11 页 + 1200×17800 长图，从旧电商页改造）。

---

## 它解决什么

不做这件事，会出现三种失败，而且不是同一种：

| 失败 | 症状 | 本仓库的解法 |
|---|---|---|
| **一叠图，不是一个品牌** | 每页单独还行，翻起来像不同人做的 | 阶段 ⑥ 统一收口：调色 + 连续背景 + 长图 |
| **话说得漂亮，但什么都没说** | "高级、优雅、引领"，读者记不住也验证不了 | 文案公式 + 禁用词扫描器（机器拦） |
| **结构对了，节奏错了** | 页页同类型，翻三页就疲 | 五种页面类型 + 每三页换型 |

---

## 目录

```
SKILL.md                 主文档：失败模式 / 两个裁判 / 六阶段门禁 / 铁律
CHANGELOG.md             变更记录

examples/
  watch/                  暗调腕表 16 页（素材 + 脚本 + config + 一键脚本）
  nanzhi/                 亮调香水 11 页（含"旧页面改造"两段流程）

reference/
  input-contract.md        输入契约：素材五样 + 四条拒收
  样例-输入契约-观时.md     填好的契约（照着改）
  page-types.md            五种页面类型 + 图位矩阵
  layout-specs.md          字号/色板/栅格（像素级）
  copy-formulas.md         文案句式（部位+动词+结果+依据）
  pitfalls.md              18 条真踩过的坑
  case-watch.md            案例一：暗调 17 页
  case-nanzhi.md           案例二：亮调 11 页（旧页改造）

scripts/
  preflight.py             开工自检（Python/Pillow/numpy/中文字体/磁盘）
  grade.py                 统一调色（黑位/高光/冷暖分离/暗角/锐化）
  compose_long.py          连续背景长图 + 切回单页
  checkcopy.py             文案禁用词扫描（命中即退出码 1）
  selftest.py              冒烟测试（14 项，改脚本后必跑）
  make_transparent.md      页面透明化要点

templates/
  forbidden-claims.txt     禁用词表（五类）
  allowlist.txt            白名单（版本号/专有名词）
  矩阵.csv                  图位矩阵空表
  矩阵-观时17页.csv         填好的 17 行
  page-skeleton.py         页面骨架（可跑，亮底/暗底）
  pitfall-template.md      踩坑入库格式
```

---

## 两个可直接复现的示例（`examples/`）

```bash
cd examples/watch  && python scripts/run_all.py      # 暗调腕表：16 页 + 长图 1200×25192
cd examples/nanzhi && python scripts/build_pages.py && python scripts/build_final.py
                                                     # 亮调香水：11 页（从旧电商页改造）
```

两个示例都带**素材 + 脚本 + config.json**，换台机器跑一遍能出同样的页面。
改色板/字号/画布改 `config.json`；改文案改脚本（路线 1.5 的范围，见各示例 README 的"已知限制"）。

---

## 快速开始

```bash
# 1. 自检（缺什么会直接说）
python scripts/preflight.py --out-dir ./out

# 2. 生成一张合规底页（边距 72 / 字号 72-26-16-12 / 12 列栅格）
python templates/page-skeleton.py -o base.png --title "产品名"

# 3. 统一调色（让不同时间生成的图看起来像一次棚拍）
python scripts/grade.py ./assets -o ./assets_graded

# 4. 合成连续背景长图（透明页 → 一张长图 → 切回单页）
python scripts/compose_long.py ./pages

# 5. 扫文案里的禁用词
python scripts/checkcopy.py ./src --ext .py,.md

# 6. 改过脚本后跑冒烟测试
python scripts/selftest.py
```

**依赖**：Python 3.9+ / Pillow / numpy / 一个中文字体（思源宋体优先）。
找不到字体会**报错退出**，不会静默降级出方块字。

---

## 核心主张

```
先定结构，再做图；先把素材拉到同一个光下，再谈排版。
```

```
阶段 ⑥（统一收口）是分界线：
做完，整套像一个品牌；
跳过，前面五步只是"排得整齐"。
```

**两个裁判**：主张（文案/数字）归证据管；外观（图/色/字）归主人的眼睛管。两边不许互相否决。

---

## 不适用

```
✗ 1–3 张单图          直接排版，别上系统
✗ 有真实产品 + 专业摄影/3D 渲染   素材已经赢了，重点不是调色
✗ 平台主图（严格白底/尺寸/文字限制）  走平台规范
✗ 需要产品多角度一致     这是 3D 建模的活，排版救不了
```

---

## 许可

MIT，见 `LICENSE`。

案例中的品牌（观时 GUĀNSHÍ / 南枝 NÁNZHÍ）均为虚构，用于演示流程，
不对应任何真实商品；文中参数均为方案设定值，非实测。
