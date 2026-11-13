#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""L2 抽取：对渲染后的页面 PNG 做 OCR，输出文本与置信度。

依赖 rapidocr_onnxruntime。本机可用解释器：
    <venv>/Scripts/python.exe

用法：
    python ocr_pages.py <pages_dir> [-o out.md] [--json] [--low 0.80]

输出：
    ## p.3  [L2]  平均置信度 0.94 / 最低 0.71
    ...
    低于阈值的页会标 needs_review。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")

LOW_CONFIDENCE = 0.80


def page_number(path: str) -> int:
    match = re.search(r"p(\d+)", os.path.basename(path))
    return int(match.group(1)) if match else 0


def ocr_image(engine: Any, path: str) -> dict[str, Any]:
    result, _ = engine(path)
    items = result or []
    lines = [item[1] for item in items]
    scores = [float(item[2]) for item in items]
    return {
        "text": "\n".join(lines),
        "avg_score": round(sum(scores) / len(scores), 3) if scores else 0.0,
        "min_score": round(min(scores), 3) if scores else 0.0,
        "lines": len(lines),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pages_dir")
    parser.add_argument("-o", "--out")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--low", type=float, default=LOW_CONFIDENCE)
    args = parser.parse_args()

    images = sorted(glob.glob(os.path.join(args.pages_dir, "*.png")))
    if not images:
        print(f"[错误] 目录里没有 PNG：{args.pages_dir}")
        return 2

    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        print("[错误] 缺少 rapidocr_onnxruntime。请用上面注释里的 venv 解释器运行。")
        return 3

    engine = RapidOCR()
    pages: list[dict[str, Any]] = []
    for path in images:
        info = ocr_image(engine, path)
        info["page"] = page_number(path)
        info["needs_review"] = info["min_score"] < args.low
        pages.append(info)
        print(f"  p.{info['page']:03d}  行数 {info['lines']:3d}  "
              f"平均 {info['avg_score']:.2f}  最低 {info['min_score']:.2f}"
              + ("  <- needs_review" if info["needs_review"] else ""))

    if args.json:
        body = json.dumps(pages, ensure_ascii=False, indent=2)
    else:
        blocks = []
        for page in sorted(pages, key=lambda p: p["page"]):
            flag = " needs_review" if page["needs_review"] else ""
            blocks.append(
                f"## p.{page['page']}  [L2]{flag}  "
                f"平均置信度 {page['avg_score']:.2f} / 最低 {page['min_score']:.2f}\n\n"
                f"{page['text']}"
            )
        body = "\n\n".join(blocks)

    if args.out:
        open(args.out, "w", encoding="utf-8").write(body)
        print(f"已写入 {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
