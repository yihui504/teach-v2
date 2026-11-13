#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""L3 前置：把 PDF 每页渲染成 PNG，供视觉模型逐页解析。

用法：
    python render_pdf_pages.py <file.pdf> [-o outdir] [--dpi 200] [--pages 1-6]

输出：
    outdir/p001.png, p002.png, ...
"""
from __future__ import annotations

import argparse
import os
import sys

import fitz  # PyMuPDF

sys.stdout.reconfigure(encoding="utf-8")


def parse_pages(spec: str | None, total: int) -> list[int]:
    if not spec:
        return list(range(1, total + 1))
    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            pages.update(range(int(start), int(end) + 1))
        elif part:
            pages.add(int(part))
    return sorted(p for p in pages if 1 <= p <= total)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("-o", "--outdir")
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--pages", help="如 1-6 或 3,7,9")
    args = parser.parse_args()

    if not os.path.isfile(args.pdf):
        print(f"[错误] 找不到文件：{args.pdf}")
        return 2

    outdir = args.outdir or os.path.splitext(args.pdf)[0] + "_pages"
    os.makedirs(outdir, exist_ok=True)

    doc = fitz.open(args.pdf)
    targets = parse_pages(args.pages, len(doc))
    zoom = args.dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    for page_no in targets:
        page = doc[page_no - 1]
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        path = os.path.join(outdir, f"p{page_no:03d}.png")
        pix.save(path)
    print(f"已渲染 {len(targets)} 页到 {outdir}（{args.dpi} DPI）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
