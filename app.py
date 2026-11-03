"""CodeArena — Mini Online Judge.

Python only, no API key, no signup, no database.
Problems are seeded in judge/problems.py; hidden tests never leave
the server (see public_problem in that module).
"""

from flask import Flask, jsonify, render_template, request

from judge.problems import get_problem, public_problem, public_problems
from judge.runner import judge
from judge.store import add_submission, leaderboard, recent_submissions

app = Flask(__name__)
MAX_CODE_CHARS = 10000


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/problems")
def api_problems():
    return jsonify(public_problems())


@app.route("/api/problems/<problem_id>")
def api_problem(problem_id):
    problem = get_problem(problem_id)
    if not problem:
        return jsonify({"error": "Problem not found."}), 404
    return jsonify(public_problem(problem))


@app.route("/api/run-sample", methods=["POST"])
def api_run_sample():
    data = request.get_json(silent=True) or {}
    problem = get_problem(data.get("problem_id", ""))
    code = data.get("code", "")
    if not problem:
        return jsonify({"error": "Problem not found."}), 404
    if not code.strip():
        return jsonify({"error": "Code is empty."}), 400
    if len(code) > MAX_CODE_CHARS:
        return jsonify({"error": "Code is too long."}), 400
    verdict, passed, total, per_test = judge(code, problem["samples"], reveal_details=True)
    return jsonify({"verdict": verdict, "passed": passed, "total": total, "tests": per_test})


@app.route("/api/submit", methods=["POST"])
def api_submit():
    data = request.get_json(silent=True) or {}
    handle = (data.get("handle") or "").strip()[:30]
    problem = get_problem(data.get("problem_id", ""))
    code = data.get("code", "")
    if not handle:
        return jsonify({"error": "Enter a handle (username) first."}), 400
    if not problem:
        return jsonify({"error": "Problem not found."}), 404
    if not code.strip():
        return jsonify({"error": "Code is empty."}), 400
    if len(code) > MAX_CODE_CHARS:
        return jsonify({"error": "Code is too long."}), 400
    sample_verdict, sample_passed, sample_total, sample_tests = judge(
        code, problem["samples"], reveal_details=True
    )
    hidden_verdict, hidden_passed, hidden_total, hidden_tests = judge(
        code, problem["hidden"], reveal_details=False
    )
    total = sample_total + hidden_total
    passed = sample_passed + hidden_passed
    if sample_verdict != "Accepted":
        verdict = sample_verdict
    else:
        verdict = hidden_verdict
    submission = add_submission(handle, problem["id"], verdict, passed, total, code)
    # Return the leaderboard and recent submissions from THIS instance
    # in the same response. On serverless hosting, a separate fetch
    # afterwards can hit a different, fresh instance whose in-memory
    # state does not have this submission yet, which made the recent
    # submissions list look empty even though the leaderboard updated.
    recent = recent_submissions()
    return jsonify(
        {
            "submission_id": submission["id"],
            "verdict": verdict,
            "passed": passed,
            "total": total,
            "sample_tests": sample_tests,
            "hidden_tests": hidden_tests,
            "leaderboard": leaderboard(),
            "submissions": [
                {k: v for k, v in s.items() if k != "code"} for s in recent
            ],
        }
    )


@app.route("/api/leaderboard")
def api_leaderboard():
    return jsonify(leaderboard())


@app.route("/api/submissions")
def api_submissions():
    handle = request.args.get("handle", "").strip()
    items = recent_submissions(handle=handle or None)
    return jsonify(
        [
            {k: v for k, v in s.items() if k != "code"}
            for s in items
        ]
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
