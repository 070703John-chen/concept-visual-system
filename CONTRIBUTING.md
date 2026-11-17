# 参与 / 反馈

这是个自用的流程手册，但问题和 PR 都欢迎。

## 报问题

带上三样，否则没法复现：

```
1. 你跑的完整命令
2. 完整报错原文（不接受「报错了」这类描述）
3. python --version 与 pip show pillow numpy 的输出
```

## 提交前闸门

```bash
python scripts/install_hooks.py    # 每个 clone 执行一次，安装 git pre-commit 钩子
python scripts/precommit.py        # 手动执行同一套校验
```

五项校验：文档规范、文案禁用词、脚本冒烟、watch 复现、nanzhi 复现。
任一失败即中止提交；`git commit --no-verify` 可跳过，但不应使用。

## 提 PR

```
· 改脚本后必须跑 python scripts/selftest.py，15 项全过
· 新增禁用词请说明它属于哪一类（空形容词/大词/促销话术/假装权威/编造数据）
· 新增已知问题请用 templates/pitfall-template.md 的四段格式（症状/原因/处理/验证）
· 不得新增第五档字号（字号限定四档）
```

## 不接受

```
· 把流程改成"提示词模板库"
· 引入需要 GPU / 云服务的依赖（这套要在 8 GB 内存的轻薄本上跑）
· 把案例里的虚构品牌换成真实品牌（会涉及商标与不实陈述）
```
