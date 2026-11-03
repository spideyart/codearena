# CodeArena — Mini Online Judge

Write Python code in the browser, submit it, and get a verdict against
hidden test cases: Accepted, Wrong Answer, Runtime Error, Time Limit
Exceeded, Compilation Error, or Blocked.

**No API key. No signup. No database. No paid service.**

## How to run (2 commands)

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000

Try it: pick "Sum of Two Numbers", keep the starter code, enter any
handle, and click Submit. Then change the code to `print(0)` and submit
again to see a Wrong Answer. Try `import os` to see a Blocked verdict,
and `while True: pass` to see Time Limit Exceeded (2 seconds per test).

## What it does

- 55 seeded problems (20 Easy, 20 Medium, 15 Hard) with statements,
  constraints, sample tests, and starter code — filter the list by
  difficulty in the UI
- Sample run: runs only the visible samples and shows your output
- Full submit: runs samples, then hidden tests, and records a submission
- Leaderboard: ranked by problems solved, then fewest submissions
- Recent submissions list
- Royal-black UI, responsive on mobile

## How judging works

```
Code ──> AST safety check ──> isolated subprocess (python -I -s)
     │        (imports limited to math; open/eval/exec/__import__/
     │         getattr and private attributes blocked)
     ▼
Per test (2s timeout): stdin in, stdout out
     │
     ├─ timeout ──> Time Limit Exceeded
     ├─ non-zero exit ──> Runtime Error (stderr shown for samples)
     ├─ output matches after trailing-space normalisation ──> pass
     └─ otherwise ──> Wrong Answer
```

Hidden tests are never sent to the browser. The public API returns
samples only; hidden results show pass/fail per test, without the
hidden input or expected output.

## Problems handled

- **Infinite loops:** 2-second timeout per test, subprocess killed.
- **Cheating by reading tests:** hidden tests live only on the server.
- **Dangerous code:** AST check blocks os/sys/subprocess/socket,
  file access, eval/exec, and dunder access before running anything.
- **Crashes / syntax errors:** reported as Runtime Error or
  Compilation Error, never a server crash.
- **Large code:** 10,000-character limit.

## Limitations (honest)

- This sandbox is demo-grade, not production-grade isolation. A real
  judge for untrusted code needs containers or a VM sandbox
  (for example gVisor/Firecracker), plus CPU/memory limits and
  network blocking at the container level.
- Python only in this version.
- Submissions and the leaderboard are in memory only; a server restart
  (or a serverless cold start) clears them. Problems are static, so
  they are always available.
- On Vercel, serverless requests are capped at about 4.5 MB, and a
  cold start can clear the leaderboard — re-submit to rebuild it.

## Deploy on Vercel

`api/index.py` re-exports the Flask app, and `vercel.json` routes all
requests to it. Import the project in Vercel and deploy; no
environment variables or API keys are needed.

## Project structure

```
app.py                 Flask app, routes, submission handling
judge/
  problems.py          5 seeded problems, samples + hidden tests
  runner.py            AST check, isolated subprocess, verdicts
  store.py             in-memory submissions + leaderboard
templates/index.html   single page UI
static/app.js          problems, editor, verdicts, leaderboard client
static/style.css       royal-black theme
api/index.py           Vercel entry point
tests/                 runner + API tests
```

## How to test

```bash
pip install pytest
python -m pytest tests/ -v
```
