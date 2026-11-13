#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""交付闸门：只检查无争议的机械项，不检查题量与题型配比。

用法：
    python check_lesson.py lessons/0037-contiguous-memory.html \
        --workspace ../teach-v2

检查项：
  1. 每题选项数 >= --min-options（默认 4）
  2. 同题选项字符数极差 <= --spread（默认 0）
  3. 课内答案位置分布卡方 p > 0.05
  4. 最长选项命中率 < --max-longest（默认 0.40）
  5. 至少 1 个 block-produce 且标注 data-answer="hidden"
  6. 8 个固定块齐全（block-exam/prereq/scene/derive/trap/produce/remember/source）
  7. 外链 >= --min-links（默认 3），且来源块含 PPT/教材锚点
  8. 「下一课」链接存在，或 <body data-route-end="true">
  9. REVIEW-QUEUE.md 已登记本课 ID

退出码：0 全部通过；1 有失败项；2 输入错误。
"""
from __future__ import annotations

import argparse
import math
import os
import re
import sys
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")

QUESTION_RE = re.compile(r"opts:\s*\[(.*?)\]\s*,\s*ans:\s*(\d)", re.S)
OPTION_RE = re.compile(r'"([^"]*)"')
LESSON_ID_RE = re.compile(r"(\d{4})")
LESSON_LINK_RE = re.compile(r'href="(\d{4})-[^"]+\.html"')
BLOCKS_LESSON = [
    "block-exam",
    "block-prereq",
    "block-scene",
    "block-derive",
    "block-trap",
    "block-produce",
    "block-remember",
    "block-source",
]
BLOCKS_DRILL = [
    "block-exam",
    "block-derive",
    "block-produce",
    "block-trap",
    "block-remember",
    "block-source",
]


def _gamma_series(a: float, x: float) -> float:
    """正则化下不完全伽马 P(a,x)，级数展开。"""
    total = 1.0 / a
    term = total
    ap = a
    for _ in range(300):
        ap += 1
        term *= x / ap
        total += term
        if abs(term) < abs(total) * 1e-12:
            break
    return total * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gamma_cf(a: float, x: float) -> float:
    """正则化上不完全伽马 Q(a,x)，连分式。"""
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 300):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def chi2_sf(x: float, df: int) -> float:
    """卡方分布生存函数 P(X > x)。"""
    if x <= 0:
        return 1.0
    a = df / 2.0
    xx = x / 2.0
    if xx < a + 1.0:
        return 1.0 - _gamma_series(a, xx)
    return _gamma_cf(a, xx)


def main_length(html: str) -> int:
    """返回 <main> 去标签后的字符数（含标点与数字，不含内联 JS）。"""
    match = re.search(r"<main>(.*?)</main>", html, re.S)
    body = match.group(1) if match else html
    body = re.sub(r"<[^>]+>", "", body)
    return len(re.sub(r"\s+", "", body))


def parse_questions(html: str) -> list[tuple[list[str], int]]:
    out: list[tuple[list[str], int]] = []
    for match in QUESTION_RE.finditer(html):
        opts = OPTION_RE.findall(match.group(1))
        ans = int(match.group(2))
        if len(opts) >= 2 and ans < len(opts):
            out.append((opts, ans))
    return out


def check(html: str, lesson_id: str, workspace: str, args: argparse.Namespace) -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []
    questions = parse_questions(html)

    if not questions:
        results.append((False, "没有解析到任何测验题（opts/ans 对）"))
    else:
        too_few = [i + 1 for i, (opts, _) in enumerate(questions) if len(opts) < args.min_options]
        results.append(
            (not too_few, f"选项数 >= {args.min_options}" + (f"（第 {too_few} 题不足）" if too_few else ""))
        )

        spreads = []
        for index, (opts, _) in enumerate(questions, start=1):
            lens = [len(o) for o in opts]
            spread = max(lens) - min(lens)
            if spread > args.spread:
                spreads.append((index, spread, lens))
        results.append(
            (
                not spreads,
                f"选项等长（极差 <= {args.spread}）"
                + (f"（违规：{[(i, s, l) for i, s, l in spreads]}）" if spreads else ""),
            )
        )

        n = len(questions)
        choices = max(len(opts) for opts, _ in questions)
        positions = [0] * choices
        for _, ans in questions:
            positions[ans] += 1
        expected = n / float(choices)
        chi2 = sum((value - expected) ** 2 / expected for value in positions)
        p_value = chi2_sf(chi2, choices - 1)
        results.append((p_value > 0.05, f"答案位置分布 p={p_value:.3g} > 0.05（{positions}）"))

        longest = 0
        for opts, ans in questions:
            lens = [len(o) for o in opts]
            if lens[ans] == max(lens) and lens.count(max(lens)) == 1:
                longest += 1
        rate = longest / n
        results.append((rate < args.max_longest, f"最长项命中率 {rate:.1%} < {args.max_longest:.0%}"))

    results.append(
        (
            'class="block-produce"' in html and 'data-answer="hidden"' in html,
            "产出型练习存在且未直接给答案（block-produce + data-answer=hidden）",
        )
    )

    required_blocks = BLOCKS_DRILL if args.kind == "drill" else BLOCKS_LESSON
    missing = [block for block in required_blocks if block not in html]
    results.append(
        (
            not missing,
            f"{len(required_blocks)} 个固定块齐全" + (f"（缺 {missing}）" if missing else ""),
        )
    )

    links = len(re.findall(r'href="https?://', html))
    has_anchor = ("PPT" in html or "教材" in html) and "block-source" in html
    results.append((links >= args.min_links and has_anchor, f"外链 {links} >= {args.min_links} 且来源块含 PPT/教材锚点"))

    route_end = 'data-route-end="true"' in html
    planned_next = "data-next-planned=" in html
    if args.kind == "drill":
        next_link = bool(re.search(r'href="[^"]+\.html"', html))
    else:
        linked_ids = [int(value) for value in LESSON_LINK_RE.findall(html)]
        next_link = any(value > int(lesson_id) for value in linked_ids)
    results.append(
        (
            route_end or next_link or planned_next,
            "下一课链接存在（或标注路线结束 / data-next-planned）",
        )
    )

    queue_path = os.path.join(workspace, "REVIEW-QUEUE.md")
    registered = False
    if os.path.isfile(queue_path):
        registered = lesson_id in open(queue_path, encoding="utf-8", errors="replace").read()
    results.append((registered, f"REVIEW-QUEUE.md 已登记 {lesson_id}"))

    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("lesson")
    parser.add_argument("--workspace", default=os.getcwd())
    parser.add_argument("--min-options", type=int, default=4)
    parser.add_argument("--spread", type=int, default=0)
    parser.add_argument("--max-longest", type=float, default=0.40)
    parser.add_argument("--min-links", type=int, default=3)
    parser.add_argument("--kind", choices=["lesson", "drill"], default="lesson")
    parser.add_argument("--min-chars", type=int, default=4000)
    parser.add_argument("--max-chars", type=int, default=8000)
    args = parser.parse_args()

    if not os.path.isfile(args.lesson):
        print(f"[错误] 找不到 lesson：{args.lesson}")
        return 2

    html = open(args.lesson, encoding="utf-8", errors="replace").read()
    if args.kind == "drill":
        lesson_id = os.path.splitext(os.path.basename(args.lesson))[0]
    else:
        match = LESSON_ID_RE.search(os.path.basename(args.lesson))
        if not match:
            print("[错误] 文件名里找不到四位课次，如 0037-xxx.html")
            return 2
        lesson_id = match.group(1)

    print("=" * 60)
    print(f"check_lesson: {os.path.basename(args.lesson)}")
    print("=" * 60)
    results = check(html, lesson_id, os.path.abspath(args.workspace), args)
    failed = 0
    for ok, message in results:
        print(("PASS  " if ok else "FAIL  ") + message)
        if not ok:
            failed += 1

    if args.kind == "lesson":
        length = main_length(html)
        if length < args.min_chars:
            print(f"WARN  正文 {length} 字符，低于 {args.min_chars}：补推导/算例，或在 COVERAGE 记录为何从简")
        elif length > args.max_chars:
            print(f"WARN  正文 {length} 字符，高于 {args.max_chars}：拆课，或删掉与考点无关的枝节")

    print("-" * 60)
    print(f"{len(results) - failed}/{len(results)} 通过")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
