# 素材生成与溯源

本文件说明素材从提示词到入库的完整链路：数据结构、批量执行、质量裁决、与排版阶段的接口。

---

## 1. 为什么需要溯源

排版阶段可复现，但素材不可复现时，整条链路仍然断裂：
同一页换了素材，版式一致也会得出不同成品。

因此每一张素材都需记录三项：出自哪条提示词、服务哪一页、人工裁决结果。

---

## 2. 数据结构

`examples/<case>/prompts.jsonl`，一行一条 JSON：

```json
{
  "asset": "N1-瓶身亮调",
  "page": "01-封面",
  "prompt": "身份锁：… 场景锁：… 创意锁：…",
  "aspect": "3:4",
  "n": 1,
  "granularity": "asset",
  "verdict": "pending",
  "note": "",
  "files": []
}
```

| 字段 | 取值 | 说明 |
|---|---|---|
| `asset` | 字符串 | 素材标识，与 `assets/` 文件名对应 |
| `page` | 页面名或空 | 目标页面；与 `config.json` 的页面清单一致 |
| `prompt` | 字符串 | 三段式：身份锁 / 场景锁 / 创意锁 |
| `aspect` | `3:4` 等 | 图像比例 |
| `n` | 1–4 | 单条生成的图像数量 |
| `granularity` | `asset` / `category` | `asset` 为逐张记录；`category` 为按类补录，无法逐张重生成 |
| `verdict` | `pending` / `accepted` / `rejected` | 人工裁决结果 |
| `note` | 字符串 | 裁决理由 |
| `files` | 路径数组 | 生成后回写 |

历史素材（观时案例）无逐张提示词，按 `granularity: category` 如实标注，不伪造逐张记录。

---

## 3. 执行

```bash
# 1) 结构校验（不发请求）
python scripts/gen_batch.py --case watch --dry-run

# 2) 生成指定页
python scripts/gen_batch.py --case nanzhi --only 01-封面

# 3) 全量（跳过 verdict=accepted）
python scripts/gen_batch.py --case nanzhi

# 4) 人工裁决
python scripts/gen_batch.py --case nanzhi --mark N1-瓶身亮调 accepted --note "无虚构文本，瓶型一致"
```

行为约定：

- 每生成一条即写回 `prompts.jsonl`，支持中断续跑。
- 产出落在 `examples/<case>/assets/gen/`，文件名以 `asset` 开头，便于对应。
- 每次调用追加一行到 `prompts.calls.jsonl`，含完整提示词与实际产出文件名。
- 未配置 `MINIMAX_API_KEY` 时自动转入结构校验，不发起请求。

---

## 4. 质量裁决标准

裁决由人工执行，判据固定为四项：

| 判据 | 通过条件 | 失败处理 |
|---|---|---|
| 虚构文本 | 画面内无品牌名、无数字、无日历窗 | 裁切规避或弃用 |
| 瓶型/壳型一致 | 与同系列其他素材轮廓一致 | 弃用（模型无法保证多角度一致） |
| 材质与光影 | 高光方向与目标统一光向接近 | 交由统一色彩校正，可接受 |
| 构图可用性 | 主体完整、背景可去背或可承载文本 | 重新生成 |

裁决结果写入 `verdict` 与 `note`，不删除失败记录。失败记录本身是素材生成限制的证据。

---

## 5. 与排版阶段的接口

```
prompts.jsonl（verdict=accepted）
      ↓  文件名
examples/<case>/assets/gen/
      ↓  人工挑选移入
examples/<case>/assets/
      ↓  scripts/grade.py 统一色彩
assets_graded/
      ↓  页面脚本引用
out/*.jpg → out/*.png → 长图
```

`config.json` 的 `paths.assets` 指向素材目录；生成目录与入库目录分离，
避免未裁决的素材被页面脚本误引用。

---

## 6. 已记录的实测结果

| 项 | 结果 |
|---|---|
| 单条生成 | 成功，输出 864×1152，87 KB |
| 负向约束 | 生效：标签区为空白，无虚构文本 |
| 一致性 | 未通过：瓶型与既有系列不同，裁决 `rejected` |
| 结论 | 素材生成可用；同一产品的多角度一致性仍属结构性限制（见 `SKILL.md` 第十二节） |
