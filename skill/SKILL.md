---
name: teach-exam
description: Use when teaching or learning a course across multiple sessions from slides, textbooks, organized notes, or past exam papers, and the learner needs both conceptual understanding and exam performance. 中文触发：考试复习、课件、PPT、往年题、真题、教材、刷题、模考、讲义。
disable-model-invocation: true
argument-hint: "What course are we working on?"
---

# Teach for Exams

## Overview

A stateful teaching workspace with two goals held at once: **讲透概念** and **考试得分**。
Most teaching skills optimize only the first. This one keeps three lines separate but linked:

- `lessons/` — 讲懂
- `drills/` — 按考点刷题
- `exams/` — 整卷模拟

**Core principle:** 教学判断可配置，机械卫生必须过闸门。

## Workspace state

Read these before every session. If missing, create from the matching FORMAT file.

| File | Purpose |
|---|---|
| `CONFIG.md` | 软策略：来源优先级、复习周期、题量默认值、交付方式（用户可改） |
| `MISSION.md` | 为什么学、成功标准 |
| `EXAM-BLUEPRINT.md` | 考点矩阵：考点 × 来源锚点 × 题型 × 分值 × 状态 |
| `COVERAGE.md` | 路线账本：计划 / 已教 / 已练 / 已掌握 / 欠账 / 断链 |
| `REVIEW-QUEUE.md` | 到期复习与错题队列 |
| `MISTAKES.md` | 错题、错因、复发次数 |
| `GLOSSARY.md` | 规范术语 |
| `lessons/` `drills/` `exams/` | 三条产出线 |
| `learning-records/` | ZPD 依据 |
| `sources/` | 带页码锚点的抽取文本 |
| `assets/` | `quiz.js`、`style.css` |

## Before every session

1. Read `CONFIG.md`, `COVERAGE.md`, `REVIEW-QUEUE.md`.
2. **先处理到期复习**：有到期项就先做小结，不引入新内容。
3. 从 `learning-records/` + `MISSION.md` 算 ZPD。
4. 选择产出类型：
   - 新概念 → 教学课；
   - 计算/易错考点 → 专题；
   - 多个考点已学 → 套卷。
5. 在 `COVERAGE.md` 登记本次计划。

## Teaching line

Follow `LESSON-FORMAT.md` exactly. 8 blocks, ≤2 new concepts, 画面先行 5 步。
- 每个测验题必须能在正文找到依据（考教一致）。
- 至少 1 道产出型练习，答案用 `<details>` 隐藏。
- 正文按 `<main>` 去标签字符数计，目标 4,000–8,000；低于/高于会 WARN。超过 2 个新概念 → 拆课。

## Practice line

Follow `DRILL-FORMAT.md`.
- 专题按考点组织，不按课次；课没上完也能刷已教考点。
- 套卷按 `EXAM-BLUEPRINT.md` 里**每套卷自己的结构**组卷，不写死配比。
- 答案必须标来源：`标准答案` / `考生作答` / `AI 推导`。

## Review loop

- 答错、蒙对、口头不过 → 写入 `REVIEW-QUEUE.md`。
- 错因四分类写入 `MISTAKES.md`：概念混淆 / 算错 / 审题 / 蒙对。
- 节奏读 `CONFIG.md`，默认每 5 课一次小结。
- 小结课只讲队列里的概念，不引入新内容。

## Hard gates — do not skip

```bash
python ~/.claude/skills/teach-exam/scripts/check_lesson.py <file> --workspace . [--kind drill]
```

检查 9 项：选项数、选项等长、答案位置分布、最长项命中率、产出型练习、固定块、外链与来源锚点、下一课链接、复习队列登记。

- **必须把命令输出贴出来**，不要说"我检查过了"。
- 不通过就改，改完重跑；不要带着失败项交付。

每章结束或每 5 课，再跑一次工作区一致性检查：

```bash
python ~/.claude/skills/teach-exam/scripts/check_workspace.py .
```

检查蓝图 ↔ COVERAGE ↔ 实际文件 ↔ 复习队列是否对得上；断链、欠账、队列指向不存在的文件都会报出来。

## Delivery protocol

- 给出 `file:///` 可点击路径 + IDE 预览方式。
- 浏览器拉不起来时，**最多尝试 1 次**，然后改用 IDE 预览。
- **禁止把整节课贴进聊天**。降级只能贴摘要，HTML 仍是唯一做题入口。
- 交付后自检：文件存在、路径可点、题目来自 HTML 里的 `quiz.js`。

## Source pipeline

- L1 文本（pptx/pdf）→ L2 OCR（扫描页）→ L3 视觉（图、表、知识图）。
- 每课/专题引用：PPT 文件名 + 页码、教材章节、≥3 个可点击链接。
- OCR 低于阈值的页标 `needs_review`，不得直接进题库。

## Red flags — STOP

- "not critical" / "先发出去，下次再改" → 现在就跑闸门。
- "all B，展示时再打乱" → 存下来的 HTML 才是交付物，出题时就要打乱。
- "4/4 全对，可以下一课" → 要产出型证据；排除法满分不算掌握。
- "PPT 没讲但很重要" → 进加餐，不计分、不考。
- "今天把 13–26 全部做完" → 按 `CONFIG.md` 的节奏，排复习。
- "我检查过了" → 贴闸门输出，否则视为未检查。
- "先把课贴给你，文件回头补" → 文件先建，再交付。

## Rationalization table

| Excuse | Reality |
|---|---|
| "选项等长不重要" | 实测 147 题里 67.3% 的正确答案是最长项；只选最长项就能得 67 分。闸门会拦。 |
| "答案全是 B，展示时打乱就行" | 学员拿到的是 HTML 文件，不是你的展示顺序。必须写进文件时就打乱。 |
| "浏览器打不开，先贴聊天里" | 聊天会绕过 `quiz.js`，没有记录、没有错题、没有复习队列。 |
| "4/4 就是会了" | 有记录在案的"排除法满分"；只认填空/计算/口头说理。 |
| "课件没讲，但考试可能考" | 没有出处就不是考点；进加餐，不计分。 |
| "一天能学完一章" | 36 节课曾在 2 天内完成，结果是没有间隔复习。按 CONFIG 的节奏走。 |
| "我检查过了" | 贴输出。没有输出就是没检查。 |

## Common mistakes

- 把 `drills/` 当成第二套课：专题只刷考点，不重新讲概念。
- 用一套卷的配比套所有年份：每套卷结构不同，按套记录；**引用分值必须标年份/卷次**，当前学期以老师划重点为准。
- 把 `考生作答` 当标准答案：2018-19 卷面手写答案可能错。
- 复习队列只登记不执行：到期项必须先做。
- 术语表当词典：只收录学员已能用对的词。

## Files

- `LESSON-FORMAT.md` `DRILL-FORMAT.md`
- `EXAM-BLUEPRINT-FORMAT.md` `COVERAGE-FORMAT.md` `CONFIG-FORMAT.md`
- `MISSION-FORMAT.md` `LEARNING-RECORD-FORMAT.md` `RESOURCES-FORMAT.md` `GLOSSARY-FORMAT.md`
- `assets/quiz.js` `assets/style.css`
- `scripts/extract_pptx.py` `extract_pdf.py` `extract_doc.py` `render_pdf_pages.py` `ocr_pages.py` `check_lesson.py` `check_workspace.py`

## Attribution

Adapted from `mattpocock/skills` → `skills/productivity/teach` (MIT).
Original ideas: MISSION, learning records, fluency vs storage strength, ZPD, reference documents.
Added here: exam blueprint, drills/exams lines, review queue, mistake log, source pipeline, mechanical gate, delivery protocol.
