# 交付说明 · v1.3.0

| 项 | 值 |
|---|---|
| 仓库 | `github.com/070703John-chen/concept-visual-system` |
| 版本 | v1.3.0（commit `88df798`，tag `v1.3.0`） |
| 交付日期 | 2026-11-18 |
| 基线 | `发布包\定稿\2026-11-12_观时-定稿-v6`、`发布包\定稿\2026-11-12_南枝-定稿-v3` |
| 验收口径 | 新设备 clone → `reproduce.py --case <case>` → PASS |
| 仓库规模 | 194 个文件；clone 后 30.1 MB（不含 `examples/*/out/` 产物） |

---

## 1. 变更范围

上一版（v1.2.1）满足"结构完整"，但不满足"可复现"：示例产出的成品与定稿不一致，
且排版链缺透明化、生图、字体解析三段。本版按四个断点逐项修复。

### 1.1 基线对齐（断点一）

| 指标 | v1.2.1 | v1.3.0 | 基线 |
|---|---|---|---|
| 手表示例页数 | 16 | **17** | 17 |
| 手表长图 | 1200×25192 | **1200×25438** | 1200×25438 |
| 香水长图 | 无 | **1200×17800** | 1200×17800 |
| 香水网页版 | 无 | **760×11273** | 760×11273 |

新增脚本：

- `examples/watch/scripts/alpha_pages.py`：RGB 画布 → RGBA，jpg → png（阶段 ⑥ 第一步）
- `examples/watch/scripts/build_long.py`：定稿级合成（渐变 + 四道柔光带 + 侧向明暗 + 噪点 + 0.6 px 模糊，页距 20 px）
- `examples/watch/scripts/build_cover_book.py`：`00-cover` 作品集封面
- `examples/nanzhi/scripts/build_long.py`：米色三段渐变 + 斜向柔光 + 90 px 羽化

### 1.2 效果标尺（断点二）

- `examples/watch/reference/`：17 页 + 长图 + manifest（11.2 MB）
- `examples/nanzhi/reference/`：11 页 + 长图 + manifest（5.5 MB）
- `scripts/reproduce.py --case watch|nanzhi`：重跑后逐页比对高度与平均像素差，容差 6/255

### 1.3 机器指纹（断点三）

| 项 | v1.2.1 | v1.3.0 |
|---|---|---|
| 字体 | 硬编码 `C:\Windows\Fonts\NotoSerifSC-VF.ttf`（6 处） | `CVS_FONT` → `assets/fonts/` → 系统路径 → 报错退出 |
| 字体获取 | 无 | `scripts/bootstrap_fonts.py`（固定 URL + 大小区间校验 + 可选 `SHA256SUMS`） |
| 依赖 | `Pillow>=9.5` / `numpy>=1.24` | `Pillow==9.5.0` / `numpy==1.26.4` |

### 1.4 生图段（能力迁移）

- `scripts/gen_images.py`：MiniMax `image-01`，`--check` / `--no-gen` 两条无密钥退路
- `examples/watch/prompts/README.txt`、`examples/nanzhi/prompts/README.txt`：身份锁 / 场景锁 / 创意锁三段式
- `.env.example`；`.env` 已入 `.gitignore`
- `SKILL.md` 第十二节「AI 硬限制」：五条结构性限制与判定顺序
- `reference/style-anchor/`：5 张风格锚点图

---

## 2. 验收证据

环境：Windows 11 / Python 3.11.9 / Pillow 9.5.0 / numpy 1.26.4 / 思源宋体（系统）

### 2.1 全新 clone 实测

```
git clone --depth 1 <repo>      → 194 files / 30.1 MB
preflight.py --out-dir .        → 退出码 0
bootstrap_fonts.py              → 退出码 0（系统字体 NotoSerifSC-VF.ttf）
reproduce.py --case watch       → 退出码 0，PASS
reproduce.py --case nanzhi      → 退出码 0，PASS
selftest.py                     → 退出码 0（15 项）
checkcopy.py                    → 退出码 0（50 文件 0 命中）
```

### 2.2 逐页比对结果

手表（17 页，高度全等）：

| 页 | 高度 | 像素差 |
|---|---|---|
| 00-cover | 1466 | 0.00 |
| 01-hero | 1600 | 3.76 |
| 02-feature | 1600 | 0.58 |
| 03-hero | 1600 | 0.65 |
| 04-grid | 1048 | 0.62 |
| 05-spec | 1527 | 0.27 |
| 06-hero | 1600 | 0.95 |
| 07-spec | 1184 | 0.59 |
| 08-feature | 1600 | 1.41 |
| 09-spec | 1527 | 0.00 |
| 10-grid | 1537 | 0.28 |
| 11-feature | 1600 | 0.00 |
| 12-brand | 1600 | 0.62 |
| 13-hero | 1537 | 0.80 |
| 14-doc | 1133 | 0.00 |
| 15-mono | 1422 | 2.75 |
| 17-doc | 1537 | 0.00 |
| 长图 | 25438 | 尺寸一致 |

香水（11 页，高度全等，像素差 0.15–0.81，长图 17800 一致）。

像素差来源：JPEG 重编码（示例素材压至 1200 宽 / q85，定稿为原始质量）。版式差异为 0。

---

## 3. 已知限制

| 编号 | 限制 | 影响 | 处理 |
|---|---|---|---|
| L1 | 文案仍为脚本字面量，`config.json` 的 `copy` 未接线 | 改文案需改 Python | 有意为之：保住"定稿即此代码产出"的可验证性 |
| L2 | 字体不入库（授权与体积） | 新设备需 `bootstrap_fonts.py` 或自备 | 已提供下载与 SHA-256 校验 |
| L3 | CI 未启用 | 无自动化绿灯 | `.github/workflows` 需 `workflow` scope，token 不具备 |
| L4 | 生图需 `MINIMAX_API_KEY` | 无密钥只能排版 | `--no-gen` 退路已实现 |
| L5 | 未发布在线 Demo | 访客只能看 `reference/长图.jpg` | GitHub Pages 属展示层，未纳入本版范围 |

---

## 4. 未完成项

| 项 | 阻塞条件 | 责任 |
|---|---|---|
| 启用 CI | `gh auth refresh -s workflow` 后把 `ci/selftest.yml` 移入 `.github/workflows/` | 需账户授权方操作 |
| 在线 Demo | 需要 Pages 开启决策 | 待定 |
| 文案外置（L1 解除） | 需重构页面函数为配置驱动 | 延后至第三个品类出现时 |

---

## 5. 回滚

```
git checkout v1.2.1
```

v1.2.1 为结构完整但基线不符的版本；回滚后 `reproduce.py` 不存在，示例产 16 页。
