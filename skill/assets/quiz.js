/* 可复用测验组件 v2
 *
 * 与 v1 的差别：
 *   1. 选项在渲染时随机打乱，答案位置不再固定；
 *   2. 每题带稳定 ID，结果可复制成 JSON 交给 agent 记入 MISTAKES/REVIEW-QUEUE；
 *   3. 答对后可勾选「蒙对/排除法」，蒙对按未掌握处理；
 *   4. 答错可「再做一次」，重做不会刷分；
 *   5. 运行时检查选项字数极差，>0 时在控制台告警（最终以 check_lesson.py 为准）。
 *
 * 用法：
 *   renderQuiz("#quiz", [
 *     { id: "0023-Q1", q: "题干", opts: ["...", "...", "...", "..."], ans: 2,
 *       why: "解析", tags: ["信号量"] },
 *   ]);
 */
(function () {
  "use strict";

  function shuffle(list) {
    const out = list.slice();
    for (let i = out.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [out[i], out[j]] = [out[j], out[i]];
    }
    return out;
  }

  function lengthSpread(opts) {
    const lens = opts.map((o) => [...o].length);
    return Math.max(...lens) - Math.min(...lens);
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function renderQuiz(containerSel, questions) {
    const root = document.querySelector(containerSel);
    if (!root) return;

    const state = { answered: 0, correct: 0, guessed: 0, results: [] };
    const total = questions.length;

    const score = el("div", "q-score");
    score.style.display = "none";

    function refresh() {
      const effective = state.correct - state.guessed;
      score.style.display = "block";
      score.textContent =
        "得分：" + state.correct + " / " + total +
        "（蒙对 " + state.guessed + "，按掌握计 " + effective + "）" +
        (state.answered === total
          ? state.correct === total && state.guessed === 0
            ? "　全部掌握，可以进入下一课。"
            : "　蒙对或错题已进复习队列。"
          : "");
    }

    function collect() {
      const payload = { lesson: root.dataset.lesson || "", results: state.results };
      const text = JSON.stringify(payload, null, 2);
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(
          () => (copyBtn.textContent = "已复制"),
          () => window.prompt("复制下面的结果：", text)
        );
      } else {
        window.prompt("复制下面的结果：", text);
      }
    }

    const copyBtn = el("button", "q-copy", "复制结果（交给 agent 记错题）");
    copyBtn.type = "button";
    copyBtn.addEventListener("click", collect);

    questions.forEach((item, qi) => {
      const card = el("div", "q-card");
      card.dataset.qid = item.id || "Q" + (qi + 1);

      const spread = lengthSpread(item.opts);
      if (spread > 0) {
        console.warn("[quiz] " + card.dataset.qid + " 选项字数极差 " + spread + "，违反等长规则");
        card.dataset.spread = String(spread);
      }

      const order = shuffle(item.opts.map((_, i) => i));
      const opts = order.map((i) => item.opts[i]);
      const ans = order.indexOf(item.ans);

      const text = el("div", "q-text", (qi + 1) + ". " + item.q);
      card.appendChild(text);

      const optsBox = el("div", "q-opts");
      const buttons = opts.map((value, oi) => {
        const btn = el("button", "q-opt", String.fromCharCode(65 + oi) + "　" + value);
        btn.type = "button";
        btn.addEventListener("click", () => onPick(oi));
        return btn;
      });
      buttons.forEach((b) => optsBox.appendChild(b));
      card.appendChild(optsBox);

      const explain = el("p", "q-explain");
      explain.style.display = "none";
      card.appendChild(explain);

      const guessBox = el("label", "q-guess");
      guessBox.style.display = "none";
      const guess = document.createElement("input");
      guess.type = "checkbox";
      guess.addEventListener("change", () => {
        const was = card.dataset.guessed === "1";
        if (guess.checked && !was) {
          card.dataset.guessed = "1";
          state.guessed += 1;
        } else if (!guess.checked && was) {
          card.dataset.guessed = "0";
          state.guessed -= 1;
        }
        syncResult();
        refresh();
      });
      guessBox.appendChild(guess);
      guessBox.appendChild(document.createTextNode(" 这题是蒙对/排除法（按未掌握处理）"));
      card.appendChild(guessBox);

      const retry = el("button", "q-retry", "再做一次");
      retry.type = "button";
      retry.style.display = "none";
      retry.addEventListener("click", () => {
        if (card.dataset.result === "correct") state.correct -= 1;
        else if (card.dataset.result === "wrong") state.answered -= 1;
        card.dataset.result = "";
        card.dataset.guessed = "0";
        lastResult = null;
        buttons.forEach((b) => {
          b.disabled = false;
          b.classList.remove("correct", "wrong");
        });
        explain.style.display = "none";
        guessBox.style.display = "none";
        guess.checked = false;
        retry.style.display = "none";
        syncResult();
        refresh();
      });
      card.appendChild(retry);

      let lastResult = null;

      function onPick(oi) {
        if (card.dataset.result) return;
        const right = oi === ans;
        card.dataset.result = right ? "correct" : "wrong";
        if (right) state.correct += 1;
        state.answered += 1;
        lastResult = { right: right, picked: oi, answer: ans };

        buttons.forEach((btn, bi) => {
          btn.disabled = true;
          if (bi === ans) btn.classList.add("correct");
          else if (bi === oi) btn.classList.add("wrong");
        });
        explain.textContent = (right ? "✓ 正确。" : "✗ 不对。") + (item.why || "");
        explain.style.display = "block";
        if (right) guessBox.style.display = "block";
        retry.style.display = right ? "none" : "inline-block";
        syncResult();
        refresh();
      }

      function syncResult() {
        if (!lastResult) return;
        const qid = card.dataset.qid;
        const entry = {
          id: qid,
          correct: lastResult.right,
          guessed: card.dataset.guessed === "1",
          tags: item.tags || [],
        };
        state.results = state.results.filter((r) => r.id !== qid);
        state.results.push(entry);
      }

      root.appendChild(card);
    });

    root.appendChild(score);
    root.appendChild(copyBtn);
  }

  window.renderQuiz = renderQuiz;
})();
