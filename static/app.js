let problems = [];
let current = null;
let filter = "All";
let searchQuery = "";
let answerShown = false;

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function verdictClass(v) {
  if (v === "Accepted") return "Accepted";
  if (v === "Time Limit Exceeded") return "Time";
  return v.replace(/ /g, "");
}

// ---------- Pages: header menu ----------
function showPage(page) {
  document.querySelectorAll(".page").forEach((p) => { p.hidden = p.id !== `page-${page}`; });
  document.querySelectorAll(".nav-btn").forEach((b) => b.classList.toggle("active", b.dataset.page === page));
  if (page === "leaderboard") { refreshLeaderboard(); refreshSubmissions(); }
  window.scrollTo(0, 0);
}
document.querySelectorAll(".nav-btn").forEach((b) => {
  b.addEventListener("click", () => showPage(b.dataset.page));
});

// ---------- Problems page: search (no dropdown) + difficulty filter ----------
function visibleProblems() {
  const q = searchQuery.trim().toLowerCase();
  return problems.filter((p) =>
    (filter === "All" || p.difficulty === filter) &&
    (q === "" || p.title.toLowerCase().includes(q) || p.id.toLowerCase().includes(q))
  );
}

function renderProblemList() {
  const shown = visibleProblems();
  document.getElementById("problem-count").textContent = `Showing ${shown.length} of ${problems.length} problems`;
  document.getElementById("problem-list").innerHTML = shown.length ? shown.map((p) => `
    <button class="problem-btn" data-id="${p.id}">${esc(p.title)}<span class="diff">${esc(p.difficulty)}</span></button>
  `).join("") : `<p class="muted">No problems match your search.</p>`;
  document.querySelectorAll("#problem-list .problem-btn").forEach((btn) => {
    btn.classList.toggle("active", current && btn.dataset.id === current.id);
    btn.addEventListener("click", () => selectProblem(btn.dataset.id, true));
  });
  document.querySelectorAll(".filter-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.filter === filter);
    b.onclick = () => { filter = b.dataset.filter; renderProblemList(); };
  });
}

document.getElementById("problem-search").addEventListener("input", (e) => {
  searchQuery = e.target.value;
  renderProblemList();
});

// ---------- Practice page: mini search to pick a problem ----------
document.getElementById("practice-search").addEventListener("input", (e) => {
  const q = e.target.value.trim().toLowerCase();
  const box = document.getElementById("practice-results");
  if (q === "") { box.innerHTML = ""; return; }
  const matches = problems.filter((p) =>
    p.title.toLowerCase().includes(q) || p.id.toLowerCase().includes(q)).slice(0, 8);
  box.innerHTML = matches.length ? matches.map((p) => `
    <button class="problem-btn" data-id="${p.id}">${esc(p.title)}<span class="diff">${esc(p.difficulty)}</span></button>
  `).join("") : `<p class="muted">No problems match your search.</p>`;
  box.querySelectorAll(".problem-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.getElementById("practice-search").value = "";
      box.innerHTML = "";
      selectProblem(btn.dataset.id, true);
    });
  });
});

async function loadProblems() {
  const res = await fetch("/api/problems");
  problems = await res.json();
  renderProblemList();
  // Load the first problem into Practice, but stay on the Problems page.
  if (problems.length) selectProblem(problems[0].id, false);
  refreshLeaderboard();
  refreshSubmissions();
}

async function selectProblem(id, goToPractice) {
  const res = await fetch(`/api/problems/${id}`);
  current = await res.json();
  document.querySelectorAll("#problem-list .problem-btn").forEach((b) => b.classList.toggle("active", b.dataset.id === id));
  document.getElementById("problem-title").textContent = current.title;
  document.getElementById("problem-difficulty").textContent = current.difficulty;
  document.getElementById("problem-statement").textContent = current.statement;
  document.getElementById("problem-input").textContent = current.input_format;
  document.getElementById("problem-output").textContent = current.output_format;
  document.getElementById("problem-constraints").textContent = current.constraints;
  document.getElementById("problem-samples").innerHTML = current.samples.map((s, i) => `
    <div class="test-row"><b>Sample ${i + 1}</b><br>Input:<pre>${esc(s.input)}</pre>Output:<pre>${esc(s.output)}</pre></div>
  `).join("");
  // The answer stays hidden: the editor starts blank so the user
  // writes their own solution first. Show Answer fills it on demand.
  document.getElementById("code").value = "";
  answerShown = false;
  document.getElementById("show-answer-btn").textContent = "Show Answer";
  document.getElementById("verdict").hidden = true;
  document.getElementById("test-results").innerHTML = "";
  // Selecting a problem takes you straight to the writing area —
  // the Practice page opens scrolled to the editor itself, so a new
  // user is not left scrolling past the statement to find it.
  if (goToPractice) {
    showPage("practice");
    document.getElementById("code").scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function showVerdict(data, testsHtml) {
  const el = document.getElementById("verdict");
  el.hidden = false;
  el.className = "verdict " + verdictClass(data.verdict);
  el.textContent = `${data.verdict} — ${data.passed}/${data.total} tests passed`;
  document.getElementById("test-results").innerHTML = testsHtml;
}

function testsHtml(tests, label) {
  if (!tests || !tests.length) return "";
  return `<h3>${label}</h3>` + tests.map((t) => `
    <div class="test-row">
      <span class="${t.passed ? "pass" : "fail"}">${t.passed ? "✓ Passed" : "✗ " + esc(t.verdict)}</span>
      ${t.input !== undefined ? `<br>Input:<pre>${esc(t.input)}</pre>Expected:<pre>${esc(t.expected)}</pre>Your output:<pre>${esc(t.output || "")}</pre>` : ""}
      ${t.detail ? `<br><span class="muted">${esc(t.detail)}</span>` : ""}
    </div>
  `).join("");
}

async function postJson(url, body) {
  const res = await fetch(url, { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body) });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Request failed.");
  return data;
}

document.getElementById("run-btn").addEventListener("click", async () => {
  if (!current) return;
  try {
    const data = await postJson("/api/run-sample", { problem_id: current.id, code: document.getElementById("code").value });
    showVerdict(data, testsHtml(data.tests, "Sample tests"));
  } catch (e) { alert(e.message); }
});

// Show Answer <-> Hide Answer toggle.
document.getElementById("show-answer-btn").addEventListener("click", async () => {
  if (!current) return;
  const editor = document.getElementById("code");
  const btn = document.getElementById("show-answer-btn");
  if (answerShown) {
    editor.value = "";
    answerShown = false;
    btn.textContent = "Show Answer";
    editor.focus();
    return;
  }
  try {
    const res = await fetch(`/api/problems/${current.id}/answer`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not load the answer.");
    if (editor.value.trim() !== "" && editor.value !== data.starter_code &&
        !confirm("Replace your code with the perfect solution? Your current code will be lost.")) return;
    editor.value = data.starter_code || "";
    answerShown = true;
    btn.textContent = "Hide Answer";
    editor.focus();
  } catch (e) { alert(e.message); }
});

document.getElementById("submit-btn").addEventListener("click", async () => {
  if (!current) return;
  const handle = document.getElementById("handle").value.trim();
  if (!handle) { alert("Enter a handle first."); return; }
  try {
    const data = await postJson("/api/submit", { handle, problem_id: current.id, code: document.getElementById("code").value });
    showVerdict(data, testsHtml(data.sample_tests, "Sample tests") + testsHtml(data.hidden_tests, "Hidden tests (inputs hidden)"));
    // Use the snapshot from the submit response, not a fresh fetch:
    // a fresh fetch can hit a different serverless instance that
    // does not have this submission in memory yet.
    if (data.leaderboard) renderLeaderboard(data.leaderboard);
    if (data.submissions) renderSubmissions(data.submissions);
  } catch (e) { alert(e.message); }
});

function renderLeaderboard(rows) {
  document.getElementById("leaderboard").innerHTML = rows.length ? `
    <table><tr><th>#</th><th>Handle</th><th>Solved</th><th>Submissions</th></tr>
    ${rows.map((r) => `<tr><td>${r.rank}</td><td>${esc(r.handle)}</td><td>${r.solved}</td><td>${r.submissions}</td></tr>`).join("")}
    </table>` : `<p class="muted">No submissions yet. Be the first.</p>`;
}

async function refreshLeaderboard() {
  const res = await fetch("/api/leaderboard");
  renderLeaderboard(await res.json());
}

function renderSubmissions(rows) {
  document.getElementById("submissions").innerHTML = rows.length ? rows.map((r) => `
    <div class="test-row"><b>${esc(r.handle)}</b> — ${esc(r.problem_id)} — <span class="${r.verdict === "Accepted" ? "pass" : "fail"}">${esc(r.verdict)}</span> (${r.passed}/${r.total})</div>
  `).join("") : `<p class="muted">No submissions yet.</p>`;
}

async function refreshSubmissions() {
  const res = await fetch("/api/submissions");
  renderSubmissions(await res.json());
}

loadProblems();
