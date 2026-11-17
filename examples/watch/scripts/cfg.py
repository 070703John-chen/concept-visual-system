# -*- coding: utf-8 -*-
"""读取同目录 config.json，给出素材目录与输出目录"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
_CFG_PATH = os.path.join(_ROOT, "config.json")

with open(_CFG_PATH, encoding="utf-8") as f:
    CFG = json.load(f)

ASSETS = os.environ.get("CVS_ASSETS") or os.path.join(_ROOT, CFG.get("paths", {}).get("assets", "assets"))
OUT = os.environ.get("CVS_OUT") or os.path.join(_ROOT, CFG.get("paths", {}).get("out", "out"))
os.makedirs(OUT, exist_ok=True)

PALETTE = CFG.get("palette", {})
TYPE = CFG.get("type", {})
