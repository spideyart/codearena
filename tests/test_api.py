import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app

client = app.test_client()


def test_problems_hide_hidden():
    data = client.get("/api/problems").get_json()
    assert len(data) == 55
    difficulties = {}
    for p in data:
        difficulties[p["difficulty"]] = difficulties.get(p["difficulty"], 0) + 1
    assert difficulties == {"Easy": 20, "Medium": 20, "Hard": 15}
    assert all("hidden" not in p for p in data)


def test_submit_accepted_and_leaderboard():
    res = client.post("/api/submit", json={
        "handle": "tester1",
        "problem_id": "sum-two",
        "code": "a, b = map(int, input().split())\nprint(a + b)\n",
    })
    data = res.get_json()
    assert data["verdict"] == "Accepted"
    assert data["passed"] == data["total"] == 5
    board = client.get("/api/leaderboard").get_json()
    assert board[0]["handle"] == "tester1" and board[0]["solved"] >= 1


def test_submit_wrong_answer():
    res = client.post("/api/submit", json={
        "handle": "tester2",
        "problem_id": "sum-two",
        "code": "print(0)\n",
    })
    assert res.get_json()["verdict"] == "Wrong Answer"


def test_problems_hide_starter_code_too():
    # The perfect solution must not leak through the public problem list
    # or the single-problem endpoint; it only comes from /answer.
    data = client.get("/api/problems").get_json()
    assert all("starter_code" not in p for p in data)
    one = client.get("/api/problems/sum-two").get_json()
    assert "starter_code" not in one and "hidden" not in one


def test_show_answer_returns_perfect_solution():
    res = client.get("/api/problems/sum-two/answer")
    assert res.status_code == 200
    code = res.get_json()["starter_code"]
    assert "print(a + b)" in code
    # The revealed answer must itself be Accepted on its own problem.
    data = client.post("/api/submit", json={
        "handle": "answercheck",
        "problem_id": "sum-two",
        "code": code,
    }).get_json()
    assert data["verdict"] == "Accepted"
    assert client.get("/api/problems/nope/answer").status_code == 404


def test_run_sample():
    res = client.post("/api/run-sample", json={
        "handle": "x",
        "problem_id": "even-odd",
        "code": "n = int(input())\nprint('Even' if n % 2 == 0 else 'Odd')\n",
    })
    data = res.get_json()
    assert data["verdict"] == "Accepted" and data["passed"] == 2
