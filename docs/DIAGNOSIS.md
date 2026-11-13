# teach skill 诊断报告

**评估对象**：`https://github.com/mattpocock/skills/tree/main/skills/productivity/teach`
**评估现场**：`teach/`（36 节课 / 36 条学习记录）+ `interaction logs.md`（105 轮 / 7182 行）
**评估日期**：2026-11-13
**目标**：零基础学生，用 PPT / 整理材料 / 电子教材 / 往年试题，做到概念讲透 + 考试高分

---

## 0. 先说结论

这个 skill 不是"讲得不好"。它在**讲**这件事上已经做得不错：每课有类比、有推导、有"三句话记住"、有即时反馈，36/36 节课都带 primary source。

问题在于它只优化了两件事：**讲** 和 **当场懂**。你的目标里有另外两件事它完全没有机制：

| 你的目标 | skill 的机制 | 结果 |
|---|---|---|
| 讲透概念 | 有（lesson + quiz） | 基本达成，但首讲常需重讲 |
| 考试高分 | **无** | 真题 80/100 分非选择题，练习覆盖 0 |
| 隔天还记得 | 只写在哲学里 | 36 课 2 天完成，spacing 未落地 |
| 用往年试题 | **无** | 全库 0 次提及 |

下面 14 条，每条都附**可复核的证据**与**复现方式**。

---

## 1. 如何复核

```bash
cd "<evaluation-dir>"
python verify_metrics.py            # 文本报告
python verify_metrics.py --json     # 机器可读，便于前后对比
```

脚本只读，不改任何文件。所有数字都来自 `teach/lessons/*.html` 与 `learning-records/*.md` 的实际内容。

---

## 2. 诊断清单

### P0 — 直接决定考试得分

---

#### F1. skill 完全没有"考试"这一维

**结论**：原 skill 是 mission 驱动的通用掌握式学习，不含考纲、真题、分值、题型任何概念。

**证据**
- 原 `SKILL.md` 全文无 past papers / exam / score / syllabus；且明确要求 `Avoid abstract framings like "to understand X"`。
- 36 节课中「往年/试卷/真题」出现 **0 次**（`verify_metrics.py` → `往年/试卷/真题: 0 次`）。
- 「期末」全库仅 1 次：`teach/lessons/0014-process-switch-queues.html:65` —「这个换算题期末很可能考。」
- `<course>/往年材料/` 实际有 4 份可用材料，skill 从未要求读取：

| 文件 | 页数 | 可提取文本 | 处理方式 |
|---|---:|---:|---|
| `操作系统试卷.pdf` | 56 | 14,388 字符 | 直接抽取 |
| `操作系统18-19卷.pdf` | 6 | 0 | 需 OCR |
| `操作系统知识图.pdf` | 26 | 0 | 需 OCR + 视觉解析 |
| `操作系统+杨武杰老师画的重点++cwx.doc` | 1 | — | 需转文本 |

**真题实测结构**（`操作系统试卷.pdf`，2006–2007 学年度第二学期）：

| 题型 | 分值 | 现有练习覆盖 |
|---|---:|---|
| 一、单项选择题（20 题） | 20 | ✅ 147 道全在此题型 |
| 二、填空题（10 空） | 20 | ❌ 0 |
| 三、判断题（10 题） | 10 | ❌ 0 |
| 四、程序与算法 | 10 | ❌ 0 |
| 五、问答题（银行家算法） | 16 | ❌ 0 |
| 六、计算题（页表/置换） | 24 | ❌ 0 |

→ **非选择题占 80/100 分，现有练习形式覆盖率 1/6。**

**注意：不同年份卷面结构不同。** 2018–2019 A 卷实测为「单选 20 题 × 2 分 = 40 分」，与 2006–2007 的「20 题 × 1 分」差异显著。蓝图必须按套记录结构，不能写死一套配比。

**复现**
```bash
cd "<workspace>/lessons"
grep -roE "往年|试卷|真题" *.html | wc -l     # 0
grep -roE "期末" *.html                       # 仅 0014:65
```

---

#### F2. 测验机制违反 skill 自己定的规则，且可被应试技巧刷分

**结论**：这是整份产出里最严重的单点缺陷。所有 "4/4" 都不具备独立证据力。

**证据一：规则原文 × 实际数字**

skill 原文要求：
> each answer should be exactly the same number of words
> Vary which position holds the correct answer across questions
> Don't give the user any clues about the answer through formatting or order

实测 147 道题：

| 指标 | 实测 | 随机基线 | 说明 |
|---|---|---|---|
| 答案位置分布 | A=45 / **B=93** / C=9 | 各 49 | B 位 63%，χ²=72.49，p=1.82e-16 |
| 最长选项=正确答案 | **99/147 = 67.3%** | ≈33% | 只选最长项即可得 67 分 |
| 最短选项=正确答案 | 9/147 = 6.1% | ≈33% | 长度是强提示 |
| 选项字数极差 >0 | 140/147 | 0 | 直接违反规则 |
| 选项字数极差 >8 字 | 71/147 | 0 | 典型 test-wiseness 泄漏 |
| 选项个数 | 全部 3 个 | — | 单题猜对率 33% |

极端样例：`teach/lessons/0017-exceptions-signals.html` 第 2 题，正确项 42 字，另两项 10 / 12 字。
归档线 `teach/lessons/archive-lab-line/0005-sync-when-locks-needed.html` 第 92/96/100/104 行的四道题**全部 `ans: 1`**。

**证据二：agent 自己发现了，却主动放弃**

`interaction logs.md:166-169`：
> Actually to preserve spacing/retrieval, and per the skill "answers exactly same number of words", **not critical**.
> Original order: in Q1 correct is B, Q2 B, Q3 B, Q4 B — **all B! That's a formatting clue. I should shuffle order** when presenting.

它识别出"答案全是 B"，也打算打乱，但最终写进 HTML 的仍是 `ans: 1`。
→ **散文规则会被 agent 当场判定为"不重要"并绕过**，这是必须做机械闸门的直接理由。

**证据三：反馈回路已退化成盖章**

105 轮用户发言里：
- **42 轮**是「全对 / 满分」
- **36 轮**是「开下一课」
- 只有 4 轮出现「没看懂 / 太难懂 / 不够明白」

用户自己的记录也印证：`teach/learning-records/0002-recalibration.md` —「测验第 2 题（malloc parameters）是**排除法做对的**，并不理解」「**满分不可信（排除法、即时性），fluency ≠ 掌握**」。

**证据四：答完不能重做**

`teach/assets/quiz.js` 用 `card.dataset.done` 锁死作答；只记总分，不记题目 ID、不记错题。

**复现**：`python verify_metrics.py`，看 `[F2] 测验卫生` 一节。

---

#### F3. "间隔复习"只写在哲学里，没有落地机制

**证据**
- skill 把 spacing 列为 desirable difficulty 三件套之一，但没有到期日、题库 ID、回炉课规范任何字段。
- 全库「复习/重测/间隔重复/遗忘/回炉」合计 **5 次**。
- `teach/learning-records/0037-scheduling-chapter-done.md:36`：「0032 的 SRTF 计算题只在正文出现，**未让学员独立算过**；冲刺阶段补一道。」
- 5/36 条学习记录带「遗留」，但没有机制保证这些遗留被排进未来课程。

---

#### F4. 只有选择题，没有独立计算/推导/书写练习

**证据**
- 147 道题全部是 3 选 1 选择题（`verify_metrics.py` → `选项数分布: {3: 147}`）。
- 36 节课里只有 8 节出现「例题/计算」字样。
- 真题非选择题 80 分（填空 20 / 判断 10 / 程序 10 / 问答 16 / 计算 24），**练习覆盖为 0**。
- 17/36 条记录靠「口头追问」补，说明口头说理才是实际主力考核方式，但 skill 从未定义它。
- `learning-records/0037` 的遗留项直接承认：「SRTF 未独立算过」。

---

#### F5. 没有"考—教—练"覆盖率的账本，已发生过真实事故

**证据**：`teach/learning-records/0024-reteach-0010-0011-scope.md`
> 两课原版的知识点本身没错，错在**考了课内没有的内容**
> 同时两课**漏教了课件里有的内容**，却拿去考或干脆跳过
> **想考就要先教**：任何出现在测验或追问里的点，必须在课内正文有明确讲解

日志第 3101 轮用户原话：「重做0010、0011。记住想考就要先教。」

同类隐蔽案例：`teach/lessons/0016-processes-vs-threads.html:56-60` 讲"线程私有栈/寄存器"，探查判定为**课件未明确展开的推断内容**——没被考，但已作为事实写进正文。

→ 这条规则现在只躺在 `NOTES.md` 里，skill 没有任何检查点能发现"考了没教"或"教漏了"。

---

### P1 — 决定概念是否讲透

---

#### F6. 认知负荷超限，违反用户自定的"每课 ≤2 新概念"

**证据**
- `teach/NOTES.md:12`：「每课 ≤2 个新概念」。
- 实测平均 **4.4 个内容小节/课**，**31/36 课超过 2 节**。
- `teach/lessons/0018-interrupts-idt.html`：7 节，含"概念一 IDT / 概念二 五个步骤"。
- `teach/lessons/0023-semaphore.html`：6 节，含"概念一 P/V / 概念二 三种初值"+三个坑。
- `teach/lessons/0036-multiprocessor-linux-windows.html`：五个大主题（SMP 队列、超线程、负载均衡、亲和性、CFS+Windows）。
- 日志第 404 行 agent 自认：「0006 我讲得太满了：一节课里塞进了 EOF、shutdown、mmap 页对齐和信号量四个点……超出了'每课不超过 2 个新概念'的规则。」
- 三次「首版未懂」的重讲课（0019 IPC、0021 Peterson、0024 管程）都是高小节数课。

---

#### F7. 零基础前置检查缺失，真实起点靠"翻车后校准"才发现

**证据**
- `teach/learning-records/0002-recalibration.md`：
  > 真实起点：**C 语言指针/malloc/struct 不熟 + 内核/用户态概念缺失**
  > 之前"逐段讲设计"的粒度太粗，需要下降到"逐行读代码 + 概念类比"粒度
- 这是在**上了两节课、发现学员答不出之后**才校准的。
- 日志第 7 轮用户直说：「我编程不好当前0006看不懂」。
- skill 没有"开课前前置诊断"这一关。

---

#### F8. 首讲质量不稳定，类比是唯一有效手段但未被协议化

**证据**
- `teach/NOTES.md:42` 0019：「原版 4/4 但学员反馈"不够明白"；**当日重讲**（水管/邮箱/白板三画面）」
- `teach/NOTES.md:44` 0021：「首版代码讲法未懂；改用"自习室 + 举牌 + 小黑板"重讲」
- `teach/NOTES.md:47` 0024：「首版抽象未懂；改用"一个窗口的营业厅"重讲」
- 日志第 84 轮「0021没看懂」、第 90 轮「重做0024，太难懂了」。
- 全库只有 3 节课出现「零基础/好比/就像」这类类比标记。

→ skill 只说 lesson 要 "beautiful / short"，没有规定**首讲必须先给画面、再给形式定义**。

---

#### F9. 材料抽取管线不在 skill 内，用户自己写了三个脚本

**证据**
- `<course>/AI教学工作区/extract_pptx.py`（45 行，抽 pptx 每页文本/表格/备注）
- `<course>/AI教学工作区/extract_pdf_toc.py`（40 行，抽 PDF 书签与目录页）
- `<course>/AI教学工作区/ocr_toc.py`（39 行，OCR 扫描版教材目录）
- 用户已手工做出 skill 本该提供的产物：`<course>/课堂讲义/_extract/b1_quotes.txt` 是「PPT 页 → 教材 § → 英文原句 → 中文对照」的三源锚点表，`b1_figs.txt` 是逐页图片描述。但只覆盖讲义 01–05，且不在 skill 规范内。

---

#### F10. 课程交付通道不可靠，退化成"聊天里讲课"

**证据**
- 日志第 11–13 轮，用户连续说「没开啊」「没开啊」「没用」；agent 反复尝试 `Start-Process` / Firefox / Edge 均失败。全文出现 `Start-Process` 9 次、`浏览器` 20 次。
- 失败后 agent 把整节课贴进聊天：「## 内容精简版」出现 3 次；第 678 行「## 三题（答完把答案发我）」。于是 HTML 与 `assets/quiz.js` 被绕过，题目退化为聊天里的 3 选 1。
- 第 83 轮用户再问「有lesson文件吗？我怎么没看到」，agent 承认（`interaction logs.md:5237-5241`）：「上一课我只在聊天里发送了内容，**没有保存成 lesson 文件**，现在补上。」

→ skill 只说 "If possible, open the lesson file by running a CLI command"，没有跨平台交付协议，也没有降级规则。

---

#### F11. 没有学习节奏约束，36 节课在 2 天内"全部通过"

**证据**
- 课程文件生成时间：`2026-11-12` 生成 8 节，`2026-11-13` 生成 **28 节**；学习记录同日 17 条 / 15 条。
- 一天内完成并"4/4 通过"约 28 节课、112 道题——与 spacing 原则物理上不可能同时成立。
- `learning-records/0037` 仍在同一天总结"六课全部通过"。

---

#### F12. 跨课承诺与路线完整性无人校验

**证据**
- `teach/lessons/0036-multiprocessor-linux-windows.html:105` 写「下一课：0037 内存：连续分配」，但**只是纯文本、没有链接**（`verify_metrics.py` → `0036 链接到 0037: False`）。
- `lessons/0037–0047` 在整个工作区**从未产出**；导出副本与线上副本 89 个文件 SHA-256 全部一致，排除导出遗漏。
- `teach/lessons/0033-rr-priority.html:91` 承诺给甘特图，`0034` 并未兑现。
- `teach/MISSION.md:17-21` 四条成功标准**一条都没勾**，其中「能独立完成 PV、银行家、调度、页表、页面置换计算题」与真题 24 分计算题直接相关。

---

### P2 — 工程质量

---

#### F13. skill 自身规则大面积未被遵守，说明缺少交付前验收闸门

| skill 原文要求 | 实际 | 证据 |
|---|---|---|
| Lessons "littered with citations - links to external resources" | 36 节课 **0 个外链** | `verify_metrics.py` → `外链总数: 0` |
| "Glossaries… an essential reference" | **无 GLOSSARY.md** | 文件不存在 |
| "reference documents will be revisited" | 36 节课只产出 **1 份** reference，且是 10-27 转型前生成 | `teach/reference/os-lab-cheatsheet.html` |
| "reminder to ask followup questions" | **2/36** | `verify_metrics.py` → `带追问提醒的课: 2/36` |
| 测验选项等长 / 答案位置变化 | 见 F2 | — |

→ 纯 Markdown 规则没有 checklist / 脚本闸门时，模型会稳定漏做。

---

#### F14. MISSION 改了，RESOURCES 没跟着改

**证据**
- `teach/MISSION.md:11-14`（2026-11-12）：「以教师 PPT 为唯一知识主线」「顺序跟课件走」；素材锚点列出 `课程PPT/`、`教材电子版/2024王道`。
- `teach/RESOURCES.md` 仍停留在实验线：OSTEP / Silberschatz / APUE / man7 / MapReduce，**无 PPT、无王道、无往年题、无课堂讲义**。
- skill 没有"mission 变更 → resources 重审"的联动检查。

---

## 3. 十四条一览

| # | 严重度 | 一句话 | 核心证据 |
|---|---|---|---|
| F1 | P0 | 无考试维度 | 真题非选择 80 分，练习覆盖 0 |
| F2 | P0 | 测验可被刷分 | B 位 63%；最长项命中 67.3%；极差>0 140/147 |
| F3 | P0 | 无间隔复习 | 关键词仅 5 次；0037 遗留未排期 |
| F4 | P0 | 无产出型练习 | 147 题全选择；计算题从未独立做 |
| F5 | P0 | 无覆盖账本 | 0024 记录"考了没教 / 教漏了" |
| F6 | P1 | 认知超载 | 平均 4.4 节；31/36 课 >2 节 |
| F7 | P1 | 无前置检查 | 0002 记录"翻车后才校准" |
| F8 | P1 | 首讲无协议 | 3 次首版未懂；类比标记仅 3 课 |
| F9 | P1 | 无抽取管线 | 用户自写 3 个脚本 |
| F10 | P1 | 交付不可靠 | 3 轮"没开啊"；1 节课只在聊天里 |
| F11 | P1 | 无节奏约束 | 2 天 36 课 / 112 题 |
| F12 | P1 | 路线断链 | 0036 无链接；0037–0047 不存在 |
| F13 | P2 | 规则无闸门 | 0 外链 / 无术语表 / 1 份参考 |
| F14 | P2 | 资源漂移 | MISSION 改了，RESOURCES 没改 |

---

## 4. 边界

- 本报告只评估**产出物与日志**，不评估模型能力本身。
- 后续 RED 基线（`_red/RED-baseline.md`）显示：在 6 个隔离场景下，原 skill **都能做对**。失败集中在**批量生产、交付压力、无机械闸门、自报验证**——所以本报告的结论是"生产流程失败"，不是"模型不会"。
- 所有"课件未展开"的判断基于 PPT 文本与课堂讲义，不排除教师口头补充的内容。
- 日志只覆盖 2026-11-11 至 11-13（105 轮），10-27 至 11-11 的早期使用未在日志中。
- 报告不做改进设计，改进方案见本仓库 `README.md` 的「设计」一节。
