# CONFIG-FORMAT — 软策略配置格式

`CONFIG.md` 是工作区里**唯一允许用户随意改**的文件。skill 每次开课前读它，不得擅自覆盖。

## 必含字段

```yaml
source_priority:
  scope: teacher_keypoints      # 范围：考什么
  format: past_papers           # 题型：怎么考
  content: ppt                  # 正文：怎么讲
  supplement: textbook          # 补充

review_cadence: every_5_lessons # 或 time_based
# review_cadence_time_based: [1, 3, 7, 14]

lesson_defaults:                # 建议值，不是硬性
  concept_lesson: {mc: 2, fill: 2, calc: 0}
  calc_lesson:    {mc: 1, fill: 1, calc: 1}

quiz_options: 4
pace: user_controlled
delivery: file_link_then_ide_preview

vision:
  model: current_session
  dpi: 200
  force_vision_keywords: [知识图, 图, 表, 流程, 结构]
  low_confidence_threshold: 0.80

paths:
  course_root: "..."
  ppt: "课程PPT"
  textbook: "教材电子版"
  past_papers: "往年材料"
  ocr_python: "..."
```

## 取值说明

| 字段 | 允许值 | 默认 |
|---|---|---|
| `source_priority.*` | `teacher_keypoints` / `past_papers` / `ppt` / `textbook` | 见上 |
| `review_cadence` | `every_N_lessons` / `time_based` | `every_5_lessons` |
| `pace` | `user_controlled` / `max_2_per_session` / `one_chapter` | `user_controlled` |
| `delivery` | `file_link_then_ide_preview` / `browser` / `chat_summary_only` | 第一种 |

## 规则

- 用户改了就生效；不要"建议"用户改回去。
- 每次改动追加到「修改记录」表：日期 / 改动 / 原因。
- 路径类配置必须能在本机解析；解析失败时明确报错，不要静默回退。
- 视觉模型若接外部服务，密钥走环境变量，**不得写进本文件**。
