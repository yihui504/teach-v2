#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""工作区一致性检查：蓝图 ↔ 覆盖账本 ↔ 实际文件 ↔ 复习队列。

用法：
    python check_workspace.py <workspace>

检查项：
  1. 蓝图里的考点 ID 是否都在 COVERAGE 出现，反之亦然
  2. lesson 里的「下一课」链接目标是否存在
  3. REVIEW-QUEUE 里的题 ID 是否能找到对应 lesson/drill
  4. COVERAGE 里登记的课次文件是否存在
  5. 计数：lessons / drills / exams

退出码：0 通过；1 有问题；2 输入错误。
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")

ID_RE = re.compile(r"\b((?:PROC|IPC|SYNC|DEAD|SCHED|MEM|IO|FS)-\d{2})\b")
LESSON_LINK_RE = re.compile(r'href="(\d{4})-([^"]+\.html)"')
QUEUE_ID_RE = re.compile(r"\b(?:(\d{4})-Q\d+|drills-([a-z0-9-]+)-Q\d+)\b")


def read(path: str) -> str:
    return open(path, encoding="utf-8", errors="replace").read() if os.path.isfile(path) else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace")
    args = parser.parse_args()
    ws = os.path.abspath(args.workspace)
    if not os.path.isdir(ws):
        print(f"[错误] 工作区不存在：{ws}")
        return 2

    lessons_dir = os.path.join(ws, "lessons")
    drills_dir = os.path.join(ws, "drills")
    exams_dir = os.path.join(ws, "exams")
    lessons = sorted(glob.glob(os.path.join(lessons_dir, "*.html")))
    drills = sorted(glob.glob(os.path.join(drills_dir, "*.html")))
    exams = sorted(glob.glob(os.path.join(exams_dir, "*.html")))

    blueprint = read(os.path.join(ws, "EXAM-BLUEPRINT.md"))
    coverage = read(os.path.join(ws, "COVERAGE.md"))
    queue = read(os.path.join(ws, "REVIEW-QUEUE.md"))

    problems: list[str] = []
    notes: list[str] = []

    # 1. 考点 ID 双向覆盖
    bp_ids = set(ID_RE.findall(blueprint))
    cov_ids = set(ID_RE.findall(coverage))
    missing_in_cov = sorted(bp_ids - cov_ids)
    extra_in_cov = sorted(cov_ids - bp_ids)
    if missing_in_cov:
        problems.append(f"蓝图有、COVERAGE 缺：{missing_in_cov}")
    if extra_in_cov:
        problems.append(f"COVERAGE 有、蓝图缺：{extra_in_cov}")
    notes.append(f"考点 ID：蓝图 {len(bp_ids)} 个，COVERAGE {len(cov_ids)} 个")

    # 2. 下一课/下一专题链接
    lesson_names = {os.path.basename(p) for p in lessons}
    broken: list[str] = []
    for path in lessons:
        for number, name in LESSON_LINK_RE.findall(read(path)):
            target = f"{number}-{name}"
            if target not in lesson_names:
                broken.append(f"{os.path.basename(path)} -> {target}")
    if broken:
        problems.append(f"断链 {len(broken)} 处：{broken}")

    # 3. 复习队列 ID
    missing_queue_targets: list[str] = []
    for number, slug in QUEUE_ID_RE.findall(queue):
        if number:
            target = f"{number}-"
            if not any(os.path.basename(p).startswith(target) for p in lessons):
                missing_queue_targets.append(f"lesson {number}")
        elif slug:
            if not os.path.isfile(os.path.join(drills_dir, f"{slug}.html")):
                missing_queue_targets.append(f"drill {slug}")
    if missing_queue_targets:
        problems.append(f"复习队列指向不存在的文件：{sorted(set(missing_queue_targets))}")

    # 4. COVERAGE 里登记且「已产出」的四位课次文件（跳过状态为「计划」的行）
    missing_lessons: list[str] = []
    for line in coverage.splitlines():
        match = re.match(r"\|\s*(\d{4})\s*\|", line)
        if not match or "计划" in line:
            continue
        number = match.group(1)
        if not any(os.path.basename(p).startswith(f"{number}-") for p in lessons):
            missing_lessons.append(number)
    if missing_lessons:
        problems.append(f"COVERAGE 登记为非计划但文件不存在：{sorted(set(missing_lessons))}")

    # 5. 计数
    counts: dict[str, Any] = {
        "lessons": len(lessons),
        "drills": len(drills),
        "exams": len(exams),
        "sources": len(glob.glob(os.path.join(ws, "sources", "*"))),
        "learning_records": len(glob.glob(os.path.join(ws, "learning-records", "*.md"))),
    }

    print("=" * 60)
    print(f"check_workspace: {ws}")
    print("=" * 60)
    for key, value in counts.items():
        print(f"  {key:16s}: {value}")
    print("-" * 60)
    for note in notes:
        print(f"  {note}")
    if problems:
        print("-" * 60)
        for problem in problems:
            print(f"FAIL  {problem}")
        print(f"\n{len(problems)} 项问题")
        return 1
    print("PASS  蓝图 / 覆盖 / 文件 / 队列一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
