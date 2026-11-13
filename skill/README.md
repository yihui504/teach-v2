# teach-exam

基于 [mattpocock/skills → teach](https://github.com/mattpocock/skills/tree/main/skills/productivity/teach)（MIT）改造的**应试强化版**教学 skill。

## 它解决什么问题

上游 `teach` 把「讲懂」做得很好，但没有三件事：

1. **考试对齐**：不知道真题考什么题型、多少分；
2. **间隔复习**：spacing 只写在哲学里，没有队列；
3. **交付闸门**：规则是散文，批量生产时会被判为「不重要」跳过。

`teach-exam` 保留上游的工作区范式（MISSION / lessons / learning-records / assets），新增：

- `EXAM-BLUEPRINT.md`：考点 × PPT 页 × 教材章节 × 题型 × 分值 × 掌握状态
- `drills/`：按考点刷题，独立于课程进度
- `exams/`：按真题卷面结构组卷
- `REVIEW-QUEUE.md` + `MISTAKES.md`：错题、蒙对、到期复习
- `scripts/check_lesson.py`：交付前机械闸门
- `scripts/extract_*.py` + `ocr_pages.py`：PPT / PDF / 扫描件分层抽取

## 用法

在课程目录下（工作区根目录）输入：

```
/teach-exam
```

首次使用会自动按 FORMAT 文件创建 `CONFIG.md`、`EXAM-BLUEPRINT.md`、`COVERAGE.md` 等。

## 三条线

| 目录 | 作用 | 格式 |
|---|---|---|
| `lessons/` | 讲懂概念，8 个固定块 | `LESSON-FORMAT.md` |
| `drills/` | 按考点刷真题 + 变式 | `DRILL-FORMAT.md` |
| `exams/` | 整卷模拟，按每套卷结构 | `EXAM-BLUEPRINT-FORMAT.md` |

## 交付闸门

```bash
python ~/.claude/skills/teach-exam/scripts/check_lesson.py <file> --workspace . [--kind drill]
```

9 项检查：选项数、选项等长、答案位置分布、最长项命中率、产出型练习、固定块、外链与来源锚点、下一课链接、复习队列登记。

**必须把输出贴出来**，不接受「我检查过了」。

每章结束再跑一次工作区一致性检查：

```bash
python ~/.claude/skills/teach-exam/scripts/check_workspace.py .
```

它会报出：蓝图有但 COVERAGE 缺的考点、断链、复习队列指向不存在的文件。

## 材料抽取

```bash
# PPT
python scripts/extract_pptx.py <file.pptx> -o sources/xxx.md
# 文本 PDF
python scripts/extract_pdf.py <file.pdf> -o sources/xxx.md
# 旧版 .doc（老师划重点）
python scripts/extract_doc.py <file.doc> -o sources/xxx.md
# 扫描 PDF → PNG → OCR（OCR 需要带 rapidocr 的解释器）
python scripts/render_pdf_pages.py <file.pdf> -o sources/pages --dpi 200
python scripts/ocr_pages.py sources/pages -o sources/xxx.md
```

低置信页会标 `needs_review`；图、表、知识图用支持视觉输入的模型读 PNG。

## 与上游的差异

| 上游 | teach-exam |
|---|---|
| 一个 lesson 单元 | lessons + drills + exams 三条线 |
| quiz 规则写在正文 | quiz 规则 + 机械闸门 |
| 无考试概念 | 考点蓝图，按套记录卷面结构 |
| spacing 仅原则 | REVIEW-QUEUE + 周期小结 |
| 无错题本 | MISTAKES + 四类错因 |
| 无材料抽取 | pptx/pdf/OCR/视觉 分层 |
| 交付靠 `if possible` | 交付协议 + 降级规则 |

## 已知限制

- `check_lesson.py` 只检查机械项；超纲、讲得透不透仍是人工判断。
- OCR 对扫描件有错字，关键页必须视觉复核。
- `考生作答`（卷面手写）不是标准答案，不能直接进题库。
- skill 是 user-invoked（`disable-model-invocation: true`），不会被模型自动触发。
