#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""L1 抽取：把 PPTX 每页的文本、表格、备注转成带页码锚点的 Markdown。

用法：
    python extract_pptx.py <file.pptx> [-o out.md] [--json]

输出格式：
    ## p.12
    [文本框] ...
    [表格]
    | ... |
    [备注] ...
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Iterator

from pptx import Presentation

sys.stdout.reconfigure(encoding="utf-8")


def iter_shapes(shapes: Any) -> Iterator[Any]:
    for shape in shapes:
        yield shape
        if getattr(shape, "shape_type", None) == 6:  # GROUP
            yield from iter_shapes(shape.shapes)


def shape_text(shape: Any) -> list[str]:
    texts: list[str] = []
    if getattr(shape, "has_text_frame", False):
        value = shape.text_frame.text.strip()
        if value:
            texts.append(f"[文本框] {value}")
    if getattr(shape, "has_table", False):
        rows = []
        for row in shape.table.rows:
            cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            rows.append("| " + " | ".join(cells) + " |")
        if rows:
            texts.append("[表格]\n" + "\n".join(rows))
    return texts


def slide_notes(slide: Any) -> str:
    try:
        if slide.has_notes_slide:
            return slide.notes_slide.notes_text_frame.text.strip()
    except Exception:
        return ""
    return ""


def extract(path: str) -> dict[str, Any]:
    prs = Presentation(path)
    slides: list[dict[str, Any]] = []
    for index, slide in enumerate(prs.slides, start=1):
        blocks: list[str] = []
        for shape in iter_shapes(slide.shapes):
            blocks.extend(shape_text(shape))
        notes = slide_notes(slide)
        if notes:
            blocks.append(f"[备注] {notes}")
        slides.append({"page": index, "blocks": blocks})
    return {"file": os.path.basename(path), "slides": slides}


def to_markdown(data: dict[str, Any]) -> str:
    lines = [f"# {data['file']}", ""]
    for slide in data["slides"]:
        lines.append(f"## p.{slide['page']}")
        lines.extend(slide["blocks"] or ["(本页无可提取文本，走 L2/L3)"])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pptx")
    parser.add_argument("-o", "--out")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not os.path.isfile(args.pptx):
        print(f"[错误] 找不到文件：{args.pptx}")
        return 2

    data = extract(args.pptx)
    body = json.dumps(data, ensure_ascii=False, indent=2) if args.json else to_markdown(data)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(body)
        print(f"已写入 {args.out}（{len(data['slides'])} 页）")
    else:
        print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
