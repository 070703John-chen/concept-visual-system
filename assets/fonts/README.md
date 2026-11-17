# 字体目录

字体**不入库**（思源宋体约 24 MB，且各家授权条款不同）。这里放的是解析规则与校验清单。

## 解析顺序（kit.py / page-skeleton.py / bootstrap_fonts.py 共用）

```
1. 环境变量 CVS_FONT 指向的文件
2. 本目录下任意 .otf / .ttf / .ttc（按 NotoSerifSC-VF > NotoSerifCJKsc > SourceHanSerifSC 优先）
3. 系统常见路径（Windows / macOS / Linux）
4. 都没有 → 报错退出，不静默降级
```

## 拿到字体

```bash
python scripts/bootstrap_fonts.py                  # 先看本机有没有
python scripts/bootstrap_fonts.py --allow-download  # 没有就下到本目录
python scripts/bootstrap_fonts.py --print-sha256    # 拿 SHA-256
```

拿到 SHA-256 后写进本目录的 `SHA256SUMS`，之后下载会自动比对：

```
<64位 sha256>  NotoSerifCJKsc-Regular.otf
```

## 版本锁定的必要性

同一句文案，字体不同 → 字宽不同 → 折行不同 → 整页版式错位。
`layout-specs.md` 的像素规格全部基于思源宋体推导，换字体即失效。
