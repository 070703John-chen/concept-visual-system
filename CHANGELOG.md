# 变更记录（CHANGELOG）

> 每条写清"改了什么、为什么改"。没有这一页，三个月后没人知道当初为什么这么定。

---

## 1.3.0 — 2026-11-18

**修断点一：基线错了**
- `examples/watch` 对齐定稿 v6：16 页 → **17 页**（补 `00-cover` 作品集封面），长图 25192 → **25438**
- 新增 `alpha_pages.py`：RGB 画布 → RGBA、jpg → png（阶段 ⑥ 第一步，之前整段缺）
- 新增 `build_long.py`：定稿级合成（渐变 + 四道柔光带 + 侧向明暗 + 噪点 + 0.6px 模糊，页距 20）
- 08/12 两页在定稿里是**整幅不透明页**（不裁不羽化）；把它们当透明页裁边会正好差 100 px —— 这是本次最隐蔽的一处
- `examples/nanzhi` 补 `build_long.py`：11 页、长图 **17800**、网页版 760×11273

**修断点二：没有效果标尺**
- `examples/*/reference/` 入库：定稿成品 32 个文件（17 页 + 长图 / 11 页 + 长图，16.6 MB）
- 新增 `scripts/reproduce.py --case watch|nanzhi`：重跑 → 逐页比高度与像素差 → PASS/FAIL
- 实测：手表 17 页差 0.00–3.76、香水 11 页差 0.15–0.81，长图尺寸完全一致

**修断点三：机器指纹**
- 字体改为解析式：`CVS_FONT` → `assets/fonts/` → 系统路径 → **报错退出**
- 新增 `scripts/bootstrap_fonts.py`：固定来源下载 + 大小校验 + 支持 `SHA256SUMS` 钉版本
- `requirements.txt` 钉死 `Pillow==9.5.0` / `numpy==1.26.4`；README 写明 Python 3.11.9

**能力迁移：生图段**
- 新增 `scripts/gen_images.py`（MiniMax image-01）；无 key 时 `--no-gen` 只列清单
- `examples/*/prompts/`：身份锁 / 场景锁 / 创意锁 三段式提示词
- `.env.example`；`.env` 进 `.gitignore`
- SKILL.md 新增第十二节「AI 硬限制」：正面表盘必编假字、多角度无法一致、标签文字必编、光向会漂、尺寸不可当数据
- `reference/style-anchor/` 5 张风格锚点图

**验收（从远端全新 clone 实测）**
```
python scripts/preflight.py --out-dir .        → 全部通过
python scripts/bootstrap_fonts.py              → 字体就绪
python scripts/reproduce.py --case watch       → PASS（17 页 + 25438）
python scripts/reproduce.py --case nanzhi      → PASS（11 页 + 17800）
python scripts/selftest.py                     → 全部通过
```

---

## 1.2.1 — 2026-11-18

**新增**
- `examples/watch` 暗调腕表 16 页：脚本 10 个 + 素材 41 张 + config + `run_all.py` 一键复现
- `examples/nanzhi` 亮调香水 11 页：两段流程（9 页 → 11 页），含"旧页面改造"
- 脚本内绝对路径全部改为 `cfg.py` + `config.json` 读取

**验证**
- 手表：`run_all.py` 跑通，16 页 + 长图 1200×25192
- 香水：`build_pages.py` → 9 页；`build_final.py` → 11 页
- 远端 127 个文件与本地逐条比对一致，SKILL.md / checkcopy.py / run_all.py 哈希一致

**为什么补**
- 1.2.0 只有方法与通用脚本，换台机器跑不出成品
- 补上示例后，"另一台机器能复现同样效果"这句话才成立


## 1.2.0 — 2026-11-12

**新增**
- `scripts/preflight.py` 开工前自检：Python / Pillow / numpy / 中文字体 / 输出目录可写 / 磁盘剩余
- `scripts/selftest.py` 冒烟测试：14 项检查跑通三个脚本（合成样图，不依赖真实素材）
- `templates/矩阵-观时17页.csv` 填好的图位矩阵样例
- `templates/pitfall-template.md` 踩坑入库格式（症状/原因/处理/验证 四段）
- `reference/样例-输入契约-观时.md` 填好的输入契约
- SKILL.md 新增「十一、依赖与自检」；开工顺序前插 preflight

**修改**
- `templates/page-skeleton.py`：找不到中文字体改为**报错退出（退出码 3）**，不再静默降级。
  理由：静默降级会生成一张"字体全错"的图，比直接报错更浪费时间。

**为什么改**
- 上一版缺"机器自检"，报错会出现在第 3 页而不是开工第一分钟
- 上一版只有空模板，新项目仍要现编；补两份填好的样例降低起步成本

**自测**
- preflight：本机全过（Python 3.11 / Pillow 9.5 / numpy 1.26 / Noto Serif SC / 58.7GB）
- setflest：14 项全过
- checkcopy：skill 自检 0 命中；故意违规 3 命中；真项目 25 文件 0 命中

---

## 1.1.0 — 2026-11-12

**新增**
- `templates/forbidden-claims.txt` 禁用词表（分五类：空形容词 / 大词 / 促销话术 / 假装权威 / 编造数据）
- `templates/allowlist.txt` 白名单（如"第一辑""第一版"，避免词组被误判）
- `scripts/checkcopy.py` 文案扫描器：可扫目录/文件，命中即退出码 1，支持 `--warn-only`
- `reference/case-nanzhi.md` 南枝案例（亮调 + 旧图新装）
- `templates/矩阵.csv` 图位矩阵模板
- `templates/page-skeleton.py` 页面骨架（可跑，输出一张空白版式页）

**修改**
- SKILL.md 补三节：三种失败模式 / 两个裁判 / 阶段门禁（每阶段怎样算通过）

**为什么改**
- 原文只有流程和清单，缺少"机器能查"的环节；误判与漏判全靠肉眼
- 只有一个案例（手表），无法说明"亮调怎么办、旧页面怎么救"

---

## 1.0.0 — 2026-11-11

**首次成文**（观时 17 页交付后整理）

- 六阶段流程、五种页面类型、四档字号、统一调色参数、连续背景长图
- `reference/`：输入契约 / 页面类型 / 版式规格 / 文案公式 / 踩坑库 / 手表案例
- `scripts/`：`grade.py`（统一调色）、`compose_long.py`（连续背景长图）、`make_transparent.md`

**当时的判断**
- 阶段 ⑥（统一收口）是这套方法与"一叠各自为政的图"的分界，必须单列成阶段
- 踩坑库优先于技巧库：18 条都是真发生过的，不是推演的

---

## 待办（下一版候选）

```
□ 完整验证器（对标 brandcheck：对比度、字号阶、栅格、安全边距自动量）
□ 两套色系（暗调 / 亮调）的调色预设分离
□ 长图分段与网页渲染的自动化（当前手工确认 16384 px 上限）
```
