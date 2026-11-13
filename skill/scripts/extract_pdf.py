#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""L1 抽取：把文本型 PDF 转成带页码锚点的 Markdown，并标出需要 OCR 的页。

用法：
    python extract_pdf.py <file.pdf> [-o out.md] [--min-chars 50] [--json]

输出：
    ## p.3  [L1]
    正文...

    ## p.7  [L2/L3 needed]  可提取文本 0 字符
    (本页可能是扫描件或纯图，需 OCR / 视觉解析)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import fitz  # PyMuPDF

sys.stdout.reconfigure(encoding="utf-8")


def extract(path: str, min_chars: int) -> dict[str, Any]:
    doc = fitz.open(path)
    pages: list[dict[str, Any]] = []
    for index, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        images = len(page.get_images())
        route = "L1" if len(text) >= min_chars else ("L2/L3" if images else "L2")
        pages.append(
            {
                "page": index,
                "chars": len(text),
                "images": images,
                "route": route,
                "text": text,
            }
        )
    return {"file": os.path.basename(path), "pages": pages}


def to_markdown(data: dict[str, Any], min_chars: int) -> str:
    lines = [f"# {data['file']}", ""]
    for page in data["pages"]:
        if page["route"] == "L1":
            lines.append(f"## p.{page['page']}  [L1]")
            lines.append(page["text"])
        else:
            lines.append(
                f"## p.{page['page']}  [{page['route']} needed]  "
                f"可提取文本 {page['chars']} 字符 / 图片 {page['images']} 张"
            )
            lines.append("(本页需要 OCR 或视觉解析)")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("-o", "--out")
    parser.add_argument("--min-chars", type=int, default=50)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not os.path.isfile(args.pdf):
        print(f"[错误] 找不到文件：{args.pdf}")
        return 2

    data = extract(args.pdf, args.min_chars)
    body = (
        json.dumps(data, ensure_ascii=False, indent=2)
        if args.json
        else to_markdown(data, args.min_chars)
    )
    if args.out:
        open(args.out, "w", encoding="utf-8").write(body)
        need = sum(1 for p in data["pages"] if p["route"] != "L1")
        print(f"已写入 {args.out}（{len(data['pages'])} 页，其中 {need} 页需 OCR/视觉）")
    else:
        print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
