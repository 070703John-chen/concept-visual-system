# 工具链与许可

按阶段列出本项目实际使用的工具、许可证、以及未使用但可替代的开源方案。
「本项目」列标注该工具是否参与现有两个案例的产出；未参与的不写入结果类结论。

---

## 一、按阶段

| 阶段 | 工具 | 许可证 | 本项目 | 说明 |
|---|---|---|---|---|
| 素材生成 | 即梦 Seedream 5.0（网页版） | 商业服务 | 使用 | 需人工操作，无 API |
| 素材生成 | MiniMax image-01（API） | 商业服务 | 使用 | `scripts/gen_images.py` 单条；`scripts/gen_batch.py` 按矩阵批量并回写溯源 |
| 素材生成（替代） | ComfyUI | GPL-3.0 | 未使用 | 本地推理图形界面，需独立显卡 |
| 素材生成（替代） | Stable Diffusion WebUI (AUTOMATIC1111) | AGPL-3.0 | 未使用 | 同上；AGPL 对分发有传染性约束 |
| 素材生成（替代） | Stable Diffusion 权重 | CreativeML Open RAIL-M | 未使用 | 使用限制条款见许可原文 |
| 去背 | Pillow（BFS 漫水 + alpha 羽化） | MIT-CMU | 使用 | `scripts/` 与 `examples/nanzhi` 内实现 |
| 调色 | Pillow + numpy | MIT-CMU / BSD-3-Clause | 使用 | `scripts/grade.py` |
| 版式渲染 | Pillow（ImageDraw + TrueType） | MIT-CMU | 使用 | 全部页面脚本 |
| 字体 | Noto Serif CJK SC | SIL Open Font License 1.1 | 使用 | `scripts/bootstrap_fonts.py` 固定来源下载 |
| 长图合成 | Pillow + numpy（渐变、柔光带、噪声、模糊） | MIT-CMU / BSD-3-Clause | 使用 | `scripts/compose_long.py`、各案例 `build_long.py` |
| 文案校验 | 本项目 `checkcopy.py` | MIT | 使用 | 禁用词表见 `templates/forbidden-claims.txt` |
| 文档校验 | 本项目 `checkregister.py` | MIT | 使用 | 规范见 `docs/STYLE.md`、术语见 `docs/GLOSSARY.md` |
| 复现验收 | 本项目 `reproduce.py` | MIT | 使用 | 与 `reference/` 逐页比对 |
| 版本控制 | git | GPL-2.0 | 使用 | — |
| 托管 | GitHub | 服务条款 | 使用 | — |
| CLI | GitHub CLI（gh） | MIT | 使用 | 建仓、推送、Release |
| 运行环境 | CPython 3.11.9 | PSF-2.0 | 使用 | 见 `requirements.txt` |
| 图像压缩（可选） | oxipng | MIT | 未使用 | 无损 PNG 优化 |
| 图像处理（替代） | libvips | LGPL-2.1 | 未使用 | 大批量处理时内存占用低于 Pillow |
| 图像处理（替代） | ImageMagick | ImageMagick License | 未使用 | 命令行批处理，本项目未引入 |

许可证取值方式：GitHub API `license.spdx_id`；Pillow、numpy、git、ImageMagick 由 GitHub 标记为
`NOASSERTION`，其许可证文本位于各自仓库根目录（Pillow 为 MIT-CMU/HPND，numpy 为 BSD-3-Clause，
git 为 GPL-2.0）。

---

## 二、依赖边界

| 环节 | 是否必需 | 无该项时的退路 |
|---|---|---|
| 商业图像服务 | 生成新素材时必需 | `gen_images.py --no-gen` 仅输出提示词清单；排版与验收链路不受影响 |
| 中文字体 | 必需 | `bootstrap_fonts.py --allow-download`；缺失时脚本报错退出 |
| Pillow / numpy | 必需 | 无替代实现 |
| 图形界面工具的 3D 能力 | 多角度一致性时必需 | 标注「概念演绎 · 非产品图」 |

---

## 三、许可注意事项

1. **字体**：SIL OFL 1.1 允许随产品分发，但不得单独售卖字体文件；本项目不入库字体，仅提供下载脚本。
2. **GPL/AGPL 工具**：ComfyUI（GPL-3.0）与 A1111（AGPL-3.0）仅作为可选替代列出，本项目未使用，
   因此不产生分发义务。若改用，需评估其许可对交付物的影响。
3. **模型权重**：CreativeML Open RAIL-M 含使用限制条款，商用前需阅读原文。
4. **素材**：两个案例中的产品图由商业图像服务生成，品牌为虚构；不含第三方图库素材。
