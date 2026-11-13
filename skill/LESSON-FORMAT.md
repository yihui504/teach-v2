# LESSON-FORMAT — 教学线课程格式

一课一个文件：`lessons/NNNN-<slug>.html`，编号四位递增。
一课最多 **2 个新概念**；超过就拆课。

## 8 个固定块（缺一块即不合格）

| # | class | 作用 | 必须包含 |
|---|---|---|---|
| 1 | `block-exam` | 考点定位 | 对应蓝图考点 ID、题型、分值、常见问法；**分值必须标注来源年份/卷次**，当前学期以老师划重点为准 |
| 2 | `block-prereq` | 前置检查 | 2–3 道口答题；不过则先补地基，不进入正课 |
| 3 | `block-scene` | 画面先行 | 见下方 5 步 |
| 4 | `block-derive` | 推导/算例 | 完整演算一遍，不能只给结论 |
| 5 | `block-trap` | 易错点 | 错误做法 + 为什么错 + 正确姿势 |
| 6 | `block-produce` | 产出型练习 | ≥1 道填空/计算/书写，`data-answer="hidden"`，先不给答案 |
| 7 | `block-remember` | 三句话记住 | 3 条，可背诵、可迁移 |
| 8 | `block-source` | 来源 | PPT 文件名 + 页码、教材章节、≥3 个可点击链接 |

## 画面先行 5 步（`block-scene` 内）

1. **一句话场景**：谁、在哪、做什么。
2. **映射表**：现实物 ↔ 代码变量/数据结构。
3. **推演两种情形**：按规则走一遍，包含一个边界情形。
4. **才给形式定义/代码**。
5. **反例与失效条件**：什么时候这个画面不成立。

> 依据：三次「首版未懂 → 重讲」都靠这一步解决（0019 水管/邮箱/白板、0021 自习室+举牌+小黑板、0024 一个窗口的营业厅）。

## HTML 骨架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>课程标题</title>
  <link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<main>
  <div class="kicker">0037 · 13-contiguous-memory-allocation</div>
  <h1>课程标题</h1>

  <section class="block-exam"><h2>一、本课考点</h2>…</section>
  <section class="block-prereq"><h2>二、开课前 3 题</h2>…</section>
  <section class="block-scene"><h2>三、先看画面</h2>…</section>
  <section class="block-derive"><h2>四、推导与算例</h2>…</section>
  <section class="block-trap"><h2>五、易错点</h2>…</section>
  <section class="block-produce" data-answer="hidden">
    <h2>六、你来算（先别看答案）</h2>
    …题目…
    <details><summary>做完再看</summary>…</details>
  </section>
  <section class="block-remember"><h2>七、三句话记住</h2>…</section>
  <section class="block-source"><h2>八、来源</h2>…</section>

  <h2>九、检索练习</h2>
  <div class="quiz" id="quiz" data-lesson="0037"></div>

  <div class="lesson-nav">
    <span>上一课：<a href="0036-...html">0036</a></span>
    <span>下一课：<a href="0038-...html">0038</a></span>
  </div>
</main>
<script src="../assets/quiz.js"></script>
<script>
renderQuiz("#quiz", [
  { id: "0037-Q1", q: "题干", opts: ["…", "…", "…", "…"], ans: 2,
    why: "解析", tags: ["连续分配"] },
]);
</script>
</body>
</html>
```

- 路线最后一课用 `<body data-route-end="true">`，否则必须有指向更大课次的链接。
- **下一课尚未创建时，不要写 `<a href>` 指向不存在的文件**；写成
  `<span data-next-planned="0040">下一课：0040（待建）</span>`，
  并在 `COVERAGE.md` 的「断链」里登记。`check_lesson.py` 认这个标记为合格，`check_workspace.py` 会把它列为待产出，不算断链。

## 测验规范

- 默认 4 个选项（`CONFIG.md` 的 `quiz_options`）。
- **同一题内选项字符数必须完全相等**；标点也算。
- 正确答案位置要分散；`check_lesson.py` 用卡方检验。
- 每题有稳定 ID：`NNNN-Q1`；带 `tags`，用于复习队列与错题本。
- 不写「以上都对/都不对」这类长度天然不等的选项。

## 交付前

```bash
python ~/.claude/skills/teach-exam/scripts/check_lesson.py lessons/0037-xxx.html --workspace .
```

9 项全过才算完成。**不要口头声称"检查过了"——把命令输出贴出来。**

## 长度

- 度量：`<main>` 去标签后的字符数（含标点与数字，**不含**内联 JS）。
- 目标 4,000–8,000 字符；`check_lesson.py` 低于 4,000 或高于 8,000 会打 `WARN`。
- 超过 2 个新概念 → 拆课；WARN 出现时，要么补推导/算例，要么在 `COVERAGE.md` 记录为什么从简。
