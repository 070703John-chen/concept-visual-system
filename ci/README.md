# CI 说明

`selftest.yml` 是 GitHub Actions 工作流，但**不能放在 `.github/workflows/` 下由脚本推送**
—— GitHub 要求 OAuth token 带 `workflow` 权限，普通仓库 token 没有。

## 启用方式（二选一）

**① 网页添加（30 秒）**

```
GitHub 仓库页 → Add file → Create new file
文件名：.github/workflows/selftest.yml
内容：复制 ci/selftest.yml 全文 → Commit
```

**② 给 gh 加 workflow 权限后由脚本推**

```bash
gh auth refresh -s workflow
git mv ci/selftest.yml .github/workflows/selftest.yml
git commit -m "ci: enable selftest workflow" && git push
```

## 这个工作流做什么

```
Windows runner → 装 Python 3.11 + 依赖 + 思源宋体
              → preflight（环境/字体/目录自检）
              → selftest（15 项冒烟）
              → checkcopy（禁用词扫描）
三条命令本地已预演，退出码均为 0
```
