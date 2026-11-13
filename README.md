# teach-v2

An **exam-oriented teaching skill** for Claude Code / Codex-style agents.
Adapted from [`mattpocock/skills → teach`](https://github.com/mattpocock/skills/tree/main/skills/productivity/teach) (MIT), with the gaps found in real use closed.

> 中文简介：把通用教学 skill 改造成「零基础 + 课件/教材/往年题 + 考试高分」的版本。
> 教学线、考点练习线、模考线分开；机械卫生过闸门，教学判断可配置。

---

## Why this exists

A 36-lesson course was produced with the original `teach` skill in two days. The lessons were good, but the artifacts showed four structural gaps:

| Gap | Evidence |
|---|---|
| No exam dimension | Past paper was 80/100 non-multiple-choice; practice covered 0 of it |
| Quiz can be gamed | 63% of 147 answers sat at position B; the longest option was correct 67.3% of the time |
| No spaced review | 36 lessons in 2 days; only 5 mentions of review/spacing across all lessons |
| Rules without gates | The agent wrote `not critical` and skipped the skill's own quiz rules |

The full diagnosis, RED baseline, and GREEN verification are in [`docs/`](docs/).

The key lesson: **the agent could follow the rules when asked; it skipped them under batch pressure.** So this version makes the right path the default and adds a mechanical gate before delivery.

---

## What's inside

```
skill/                    # the skill itself (install this)
├── SKILL.md
├── *-FORMAT.md           # lesson / drill / blueprint / coverage / review / mistakes / config
├── assets/               # quiz.js, style.css
└── scripts/              # extract_pptx/pdf/doc, render_pdf_pages, ocr_pages,
                          # check_lesson, check_workspace

docs/
├── DIAGNOSIS.md          # 14 findings with reproducible evidence
├── RED-baseline.md       # 6 pressure scenarios against the original skill
├── GREEN-results.md      # 3 scenarios against this skill + independent gate output
└── PIPELINE-NOTES.md     # L1/L2/L3 source extraction, tested on real slides & scans

tools/
└── verify_metrics.py     # reproduces the diagnosis numbers
```

---

## Design

### Three lines, separate but linked

| Directory | Purpose | Format |
|---|---|---|
| `lessons/` | teach one concept cluster | `LESSON-FORMAT.md` |
| `drills/` | drill one exam topic, independent of lesson order | `DRILL-FORMAT.md` |
| `exams/` | full-paper mock, per-paper structure | `EXAM-BLUEPRINT-FORMAT.md` |

### Hard gates vs soft config

- **Hard gates** — mechanical, no teaching judgment: equal-length options, answer-position distribution, at least one production exercise, required blocks, source links, route integrity. Run before delivery; paste the output.
- **Soft config** — teaching judgment: source priority, review cadence, question mix, pace. Lives in `CONFIG.md`; the skill reads it and never overrides it.

### Source pipeline

`L1` text (pptx/pdf/doc) → `L2` OCR (scanned pages) → `L3` vision (diagrams, knowledge maps).
Low-confidence OCR pages are marked `needs_review` and cannot enter the question bank directly.

### Answer provenance

Every answer in a drill/exam is labeled `标准答案` / `考生作答` / `AI 推导`.
Handwritten answers from a scanned paper are **not** standard answers.

---

## Install

Copy `skill/` into your agent's skills directory:

```bash
# Claude Code
cp -r skill ~/.claude/skills/teach-exam
```

On Windows (Git Bash):

```bash
cp -r skill "$USERPROFILE/.claude/skills/teach-exam"
```

The skill is user-invoked (`disable-model-invocation: true`), so call it explicitly:

```
/teach-exam
```

First run creates `CONFIG.md`, `EXAM-BLUEPRINT.md`, `COVERAGE.md`, `REVIEW-QUEUE.md`, `MISTAKES.md`, `GLOSSARY.md` from the FORMAT files.

---

## Verify

```bash
# per lesson / drill (9 checks)
python skill/scripts/check_lesson.py lessons/0037-xxx.html --workspace . [--kind drill]

# workspace consistency: blueprint ↔ coverage ↔ files ↔ review queue
python skill/scripts/check_workspace.py .

# reproduce the diagnosis numbers against an existing workspace
python tools/verify_metrics.py <workspace>
```

`check_lesson.py` exits 1 on failure. Do not ship a lesson that fails; fix and rerun.

---

## Status

- Tested on a real OS course (36 legacy lessons + 3 new lessons + 3 drills).
- New lessons/drills pass 9/9; the gate caught and fixed a real option-length violation during GREEN.
- Legacy lessons predate the gate and are tracked as "gate debt" — their old quiz scores are **not** treated as mastery evidence.
- Remaining work: parse the rest of the scanned past papers, add more topic drills, and keep the blueprint in sync with the teacher's key points.

---

## Attribution & license

- Adapted from [`mattpocock/skills`](https://github.com/mattpocock/skills) → `skills/productivity/teach`, MIT.
- Original ideas retained: MISSION, learning records, fluency vs storage strength, ZPD, reference documents.
- Added here: exam blueprint, drills/exams lines, review queue, mistake log, source pipeline, mechanical gate, delivery protocol, `data-next-planned` routing.
- This repository is MIT licensed; see [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).
