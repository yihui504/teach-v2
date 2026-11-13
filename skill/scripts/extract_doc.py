#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""L1 抽取：把旧版 .doc（Word 97-2003 / WPS）转成 UTF-8 文本。

优先用 antiword（必须带 -m UTF-8.txt，否则中文会变成 ?）；
antiword 不可用时回退到 UTF-16LE 粗解码，并给出警告。

用法：
    python extract_doc.py <file.doc> [-o out.md]

注意：antiword 打不开中文路径，所以脚本会先复制到 ASCII 临时目录。
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")


def via_antiword(path: str) -> str | None:
    if shutil.which("antiword") is None:
        return None
    with tempfile.TemporaryDirectory() as tmpdir:
        target = os.path.join(tmpdir, "input.doc")
        shutil.copyfile(path, target)
        proc = subprocess.run(
            ["antiword", "-m", "UTF-8.txt", target],
            capture_output=True,
            check=False,
        )
    if proc.returncode != 0:
        return None
    text = proc.stdout.decode("utf-8", errors="ignore").strip()
    return text or None


def via_utf16(path: str) -> str:
    data = open(path, "rb").read()
    text = data.decode("utf-16-le", errors="ignore").replace("\x00", "")
    runs = re.findall(r"[^\x00-\x08\x0b\x0c\x0e-\x1f]{2,}", text)
    kept: list[str] = []
    for run in runs:
        value = run.strip()
        has_cjk = bool(re.search(r"[一-鿿]", value))
        has_struct = bool(re.search(r"\d+\s*(题|分|个空)", value))
        if (has_cjk or has_struct) and len(value) >= 4 and value not in kept:
            kept.append(value)
    return "\n".join(kept)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("doc")
    parser.add_argument("-o", "--out")
    args = parser.parse_args()

    if not os.path.isfile(args.doc):
        print(f"[错误] 找不到文件：{args.doc}")
        return 2

    text = via_antiword(args.doc)
    source = "antiword -m UTF-8.txt"
    if text is None:
        text = via_utf16(args.doc)
        source = "UTF-16LE 粗解码（可能有元数据噪声，请人工核对）"

    body = f"# {os.path.basename(args.doc)}\n\n> 抽取方式：{source}\n\n{text}\n"
    if args.out:
        open(args.out, "w", encoding="utf-8").write(body)
        print(f"已写入 {args.out}（{len(text)} 字符，{source}）")
    else:
        print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
