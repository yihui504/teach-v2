#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""teach 工作区诊断指标复现脚本（无第三方依赖）。

用法：
    python verify_metrics.py                 # 默认检查 ../teach
    python verify_metrics.py <workspace>     # 指定工作区
    python verify_metrics.py <workspace> --json

输出每一项都对应 DIAGNOSIS.md 里的一条证据，便于逐条复核。
"""
from __future__ import annotations

import argparse
import collections
import datetime
import glob
import json
import math
import os
import re
import sys
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")

REVIEW_WORDS = re.compile(r"复习|重测|间隔重复|遗忘|回炉")
TRAP_WORDS = re.compile(r"易错|陷阱|常见错误|错因")
EXAM_WORDS = re.compile(r"往年|试卷|真题")
FINAL_WORDS = re.compile(r"期末")
FOLLOWUP_WORDS = re.compile(r"随时问|追问|不懂就问|可以问")
SECTION_SKIP = re.compile(r"三句话|检索练习|练习")
QUESTION_RE = re.compile(r"opts:\s*\[(.*?)\]\s*,\s*ans:\s*(\d)", re.S)
OPTION_RE = re.compile(r'"([^"]*)"')
H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.S)
TAG_RE = re.compile(r"<[^>]+>")


def parse_questions(html: str) -> list[tuple[list[str], int]]:
    """严格解析 renderQuiz 里的 opts/ans 对。"""
    out: list[tuple[list[str], int]] = []
    for match in QUESTION_RE.finditer(html):
        opts = OPTION_RE.findall(match.group(1))
        ans = int(match.group(2))
        if len(opts) >= 2 and ans < len(opts):
            out.append((opts, ans))
    return out


def chi_square_df2(observed: list[int], expected: float) -> float:
    return sum((value - expected) ** 2 / expected for value in observed)


def is_unique_max(opts: list[str], ans: int) -> bool:
    lengths = [len(opt) for opt in opts]
    return lengths[ans] == max(lengths) and lengths.count(max(lengths)) == 1


def is_unique_min(opts: list[str], ans: int) -> bool:
    lengths = [len(opt) for opt in opts]
    return lengths[ans] == min(lengths) and lengths.count(min(lengths)) == 1


def collect(ws: str) -> dict[str, Any]:
    lessons_dir = os.path.join(ws, "lessons")
    files = sorted(glob.glob(os.path.join(lessons_dir, "*.html")))
    questions: list[tuple[str, list[str], int]] = []
    links = review_hits = trap_hits = exam_hits = final_hits = followup = 0
    section_counts: list[int] = []
    mtimes: collections.Counter[str] = collections.Counter()

    for path in files:
        html = open(path, encoding="utf-8", errors="replace").read()
        for opts, ans in parse_questions(html):
            questions.append((os.path.basename(path), opts, ans))
        links += len(re.findall(r'href="https?://', html))
        review_hits += len(REVIEW_WORDS.findall(html))
        trap_hits += len(TRAP_WORDS.findall(html))
        exam_hits += len(EXAM_WORDS.findall(html))
        final_hits += len(FINAL_WORDS.findall(html))
        if FOLLOWUP_WORDS.search(html):
            followup += 1
        headings = [TAG_RE.sub("", raw).strip() for raw in H2_RE.findall(html)]
        section_counts.append(sum(1 for h in headings if not SECTION_SKIP.search(h)))
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        mtimes[mtime.strftime("%Y-%m-%d")] += 1

    total = len(questions)
    positions = collections.Counter(ans for _, _, ans in questions)
    expected = total / 3.0 if total else 0.0
    chi2 = chi_square_df2([positions.get(i, 0) for i in range(3)], expected) if total else 0.0
    p_value = math.exp(-chi2 / 2.0) if total else 1.0
    longest = sum(1 for _, opts, ans in questions if is_unique_max(opts, ans))
    shortest = sum(1 for _, opts, ans in questions if is_unique_min(opts, ans))
    spreads = [max(map(len, opts)) - min(map(len, opts)) for _, opts, _ in questions]

    records = sorted(glob.glob(os.path.join(ws, "learning-records", "*.md")))
    leftover = sum(
        1 for record in records
        if "遗留" in open(record, encoding="utf-8", errors="replace").read()
    )
    refs = glob.glob(os.path.join(ws, "reference", "*"))
    lesson_36 = os.path.join(lessons_dir, "0036-multiprocessor-linux-windows.html")
    link_0037 = False
    if os.path.exists(lesson_36):
        link_0037 = bool(
            re.search(r'href="0037', open(lesson_36, encoding="utf-8", errors="replace").read())
        )

    return {
        "workspace": ws,
        "lessons": len(files),
        "questions": total,
        "options_per_question": dict(collections.Counter(len(o) for _, o, _ in questions)),
        "answer_positions": {chr(65 + k): v for k, v in sorted(positions.items())},
        "chi2": round(chi2, 2),
        "p_value": p_value,
        "longest_is_answer": longest,
        "longest_is_answer_pct": round(100.0 * longest / total, 1) if total else 0.0,
        "shortest_is_answer": shortest,
        "shortest_is_answer_pct": round(100.0 * shortest / total, 1) if total else 0.0,
        "option_len_spread_gt0": sum(1 for value in spreads if value > 0),
        "option_len_spread_gt8": sum(1 for value in spreads if value > 8),
        "external_links": links,
        "review_keyword_mentions": review_hits,
        "trap_keyword_mentions": trap_hits,
        "exam_keyword_mentions": exam_hits,
        "final_keyword_mentions": final_hits,
        "followup_reminder_lessons": followup,
        "content_sections_avg": round(sum(section_counts) / len(section_counts), 1) if section_counts else 0.0,
        "content_sections_gt2": sum(1 for value in section_counts if value > 2),
        "glossary_exists": os.path.exists(os.path.join(ws, "GLOSSARY.md")),
        "reference_docs": len(refs),
        "learning_records": len(records),
        "records_with_leftover": leftover,
        "lessons_by_mtime": dict(sorted(mtimes.items())),
        "lesson_0037_exists": os.path.exists(os.path.join(lessons_dir, "0037-contiguous-memory.html")),
        "lesson_0036_links_0037": link_0037,
    }


def render(data: dict[str, Any]) -> None:
    total = data["questions"]
    print("=" * 62)
    print("teach 工作区诊断指标")
    print("=" * 62)
    print(f"工作区            : {data['workspace']}")
    print(f"课程数            : {data['lessons']}    学习记录: {data['learning_records']}")
    print(f"测验题数          : {total}    选项数分布: {data['options_per_question']}")
    print("-" * 62)
    print("[F2] 测验卫生")
    print(f"  答案位置分布    : {data['answer_positions']}   (随机基线各 1/3)")
    print(f"  卡方 / p 值     : {data['chi2']} / {data['p_value']:.3g}   (p<0.05 即非随机)")
    print(f"  最长项=正确答案 : {data['longest_is_answer']}/{total} = {data['longest_is_answer_pct']}%  (随机≈33%)")
    print(f"  最短项=正确答案 : {data['shortest_is_answer']}/{total} = {data['shortest_is_answer_pct']}%")
    print(f"  选项字数极差>0  : {data['option_len_spread_gt0']}/{total}")
    print(f"  选项字数极差>8  : {data['option_len_spread_gt8']}/{total}")
    print("-" * 62)
    print("[F3/F4] 复习与考试覆盖")
    print(f"  复习类关键词    : {data['review_keyword_mentions']} 次")
    print(f"  易错类关键词    : {data['trap_keyword_mentions']} 次")
    print(f"  往年/试卷/真题  : {data['exam_keyword_mentions']} 次")
    print(f"  期末            : {data['final_keyword_mentions']} 次")
    print("-" * 62)
    print("[F6] 认知负荷")
    print(f"  平均内容小节    : {data['content_sections_avg']}")
    print(f"  超过 2 节的课   : {data['content_sections_gt2']}/{data['lessons']}")
    print("-" * 62)
    print("[F12/F13/F14] 工程质量")
    print(f"  外链总数        : {data['external_links']}  (skill 要求 lessons littered with citations)")
    print(f"  GLOSSARY.md     : {data['glossary_exists']}")
    print(f"  reference 文档  : {data['reference_docs']}")
    print(f"  带追问提醒的课  : {data['followup_reminder_lessons']}/{data['lessons']}")
    print(f"  带「遗留」的记录: {data['records_with_leftover']}/{data['learning_records']}")
    print(f"  0037 文件存在   : {data['lesson_0037_exists']}")
    print(f"  0036 链接到 0037: {data['lesson_0036_links_0037']}")
    print(f"  课程生成日期    : {data['lessons_by_mtime']}")
    print("=" * 62)


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    default_ws = os.path.normpath(os.path.join(here, "..", "teach"))
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", nargs="?", default=default_ws)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    ws = os.path.abspath(args.workspace)

    if not os.path.isdir(os.path.join(ws, "lessons")):
        print(f"[错误] 找不到课程目录：{os.path.join(ws, 'lessons')}")
        return 2

    data = collect(ws)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        render(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
