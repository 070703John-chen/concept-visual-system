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

## 6. 实测结果（6 条提示词，真实调用）

| 素材 | 目标页 | 裁决 | 依据 |
|---|---|---|---|
| N1-瓶身亮调 | 01-封面 | rejected | 瓶型与既有系列不同；标签空白，无虚构文本 |
| N2-玻璃微距 | 08-冰晶 | rejected | 瓶型为红酒瓶（圆肩、软木塞）；影调为低调暖光；出现完整瓶型，三项均不符 |
| N3-金属盖内侧 | 03-材料 | **accepted** | 螺纹结构清晰；无虚构文本；无完整瓶型 |
| N4-纸盒平面 | 03-材料 | rejected | 同框出现软管（护肤品类），破坏品类一致性 |
| N5-手持喷洒 | 04-信息 | rejected | 品类为啤酒瓶；标签出现虚构文本；手部结构异常 |
| N6-橱窗场景 | 07-冷调002 | rejected | 瓶型为白色圆柱瓶；石台与冷调背景可裁切作背景 |

**通过率：1 / 6（16.7%）**

失败原因分布：

| 原因 | 条数 | 说明 |
|---|---|---|
| 瓶型漂移 | 4 | 同一产品无法跨生成批次保持一致，与提示词的"身份锁"描述无关 |
| 品类错误 | 2 | 出现啤酒瓶、软管等非同品类物件 |
| 虚构文本 | 1 | 一条标签生成伪文字（与负向约束并存时仍出现） |
| 影调不符 | 1 | 高调要求下产出低调暖光 |

**结论**

1. 素材生成的**可用产率约 1/6**，流程必须预设人工裁决与重生成预算。
2. 瓶型漂移是主导失败原因，与提示词精度无关；同一产品的多角度一致性需 3D 建模，
   与 `SKILL.md` 第十二节的判断一致。
3. 负向约束可降低虚构文本概率，但无法归零：6 条中仍有 1 条出现伪文字。

**数据说明**

- 模型：MiniMax `image-01`，`aspect_ratio 3:4`，`n=1`，`prompt_optimizer=true`
- 每条一次调用，无重试；两次 DNS 解析失败（`getaddrinfo failed`）为网络瞬断，补跑后成功
- 生成物位于 `examples/nanzhi/assets/gen/`（不入库）；裁决结果写入 `examples/nanzhi/prompts.jsonl`
