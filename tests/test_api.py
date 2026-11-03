import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app

client = app.test_client()


def test_problems_hide_hidden():
    data = client.get("/api/problems").get_json()
    assert len(data) == 5
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


def test_run_sample():
    res = client.post("/api/run-sample", json={
        "handle": "x",
        "problem_id": "even-odd",
        "code": "n = int(input())\nprint('Even' if n % 2 == 0 else 'Odd')\n",
    })
    data = res.get_json()
    assert data["verdict"] == "Accepted" and data["passed"] == 2
