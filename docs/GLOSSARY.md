# 术语对照表

本仓库正文一律使用「专业术语」列。日常表述仅允许出现在本文件与 `docs/STYLE.md` 的举例中。
`scripts/checkregister.py` 对「日常表述」列做机器校验。

---

## 1. 图像与素材

| 日常表述 | 专业术语 | 英文 |
|---|---|---|
| 抠图 | 去背 | background removal |
| 抠出来的图 | 去背素材 | cut-out asset |
| 拼图 / 拼一起 | 图像合成 | image compositing |
| 白底图 | 纯白背景素材 | white-seamless asset |
| 换个底 | 更换背景 | background replacement |
| 贴图 / 贴上去 | 图像贴附 | image placement |
| 底色 | 基色 | base color |
| 背景虚化 / 背景模糊 | 背景虚化 | defocus blur |
| 糊成一片 | 细节损失 | loss of detail |
| 图里的字 | 图像内文本 | in-image text |
| 一张图裁多次 | 单张素材多次裁切 | multiple crops from one asset |
| 张数 | 页面数量 | page count |
| 图位 | 图像位 | image slot |
| 素材库 | 素材集 | asset set |

## 2. 版式

| 日常表述 | 专业术语 | 英文 |
|---|---|---|
| 排版 | 版式设计 | typesetting / layout |
| 空的地方 / 空区 | 负空间 | negative space |
| 留白 | 负空间 / 版边距 | white space / margin |
| 边距 | 版边距 | margin |
| 安全边距 | 安全区 | safe area |
| 页边 | 版边 | page edge |
| 网格 | 栅格 | grid |
| 字号档 | 字号级 | type scale |
| 字大小 | 字号 | type size |
| 行距 | 行高 | leading |
| 字间距 | 字距 | tracking |
| 一行字 | 单行文本 | single text line |
| 文字块 | 文本块 | text block |
| 标题 | 主标题 | headline |
| 副标题 | 副标题 | subhead |
| 角标 | 页脚标记 | folio marker |
| 文字压图 | 文本覆盖图像 | text over image |
| 文字放暗处 | 文本置于暗部 | text on shadow area |
| 一页塞两种类型 | 单页承载两种类型 | two archetypes on one page |
| 页间距 | 页间隙 | page gap |
| 出血 | 出血 | bleed |
| 版心 | 版心 | type area |

## 3. 颜色与影调

| 日常表述 | 专业术语 | 英文 |
|---|---|---|
| 亮调 / 暗调 | 高调 / 低调 | high key / low key |
| 亮部 / 暗部 | 高光 / 暗部 | highlight / shadow |
| 压暗 | 降低明度 | reduce luminance |
| 发灰 | 灰雾度上升 | veiling glare increase |
| 色温 | 色温 | color temperature |
| 冷暖 | 冷暖倾向 | warm-cool bias |
| 统一调色 | 色彩统一 | color grading |
| 脏 | 色偏与灰雾 | color cast and haze |
| 看着还行 | 未作测量 | unmeasured |
| 对比 | 对比度 | contrast |

## 4. 流程与工程

| 日常表述 | 专业术语 | 英文 |
|---|---|---|
| 自检 | 校验 | validation |
| 质检 | 质量检查 | quality check |
| 闸门 | 提交前校验 | pre-commit gate |
| 对不上 | 不一致 | mismatch |
| 少一页 | 页面数量不符 | page count mismatch |
| 跑一遍 | 执行 | execute |
| 跑得通 | 通过 | pass |
| 改坏了 | 回归失败 | regression failure |
| 基准 | 基准 | baseline |
| 容差 | 容差 | tolerance |
| 定稿 | 定稿 | final release |
| 素材生成 | 素材生成 | asset generation |
| 概念演绎 | 概念演绎 | conceptual staging |
| 假字 | 虚构文本 | fabricated text |
| 硬限制 | 结构性限制 | structural limitation |

---

## 5. 使用方式

```bash
python scripts/checkregister.py .     # 命中日常表述即失败
```

新增术语时，先在本表登记，再加入 `scripts/checkregister.py` 的 `TERMINOLOGY` 表，
最后执行 `python scripts/precommit.py` 确认全绿。
