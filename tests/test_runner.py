import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from judge.runner import judge


def test_accepted():
    verdict, passed, total, _ = judge("print(int(input()) + 1)", [{"input": "4", "output": "5"}], reveal_details=True)
    assert verdict == "Accepted" and passed == 1 and total == 1


def test_wrong_answer():
    verdict, passed, total, _ = judge("print(0)", [{"input": "4", "output": "5"}], reveal_details=True)
    assert verdict == "Wrong Answer" and passed == 0


def test_runtime_error():
    verdict, _, _, _ = judge("print(1 / 0)", [{"input": "", "output": ""}], reveal_details=True)
    assert verdict == "Runtime Error"


def test_compilation_error():
    verdict, _, _, _ = judge("def broken(", [{"input": "", "output": ""}], reveal_details=True)
    assert verdict == "Compilation Error"


def test_blocked_import():
    verdict, _, _, tests = judge("import os\nprint(1)", [{"input": "", "output": "1"}], reveal_details=True)
    assert verdict == "Blocked"


def test_timeout():
    verdict, _, _, _ = judge("while True:\n    pass", [{"input": "", "output": ""}], reveal_details=True)
    assert verdict == "Time Limit Exceeded"


def test_hidden_details_hidden():
    _, _, _, tests = judge("print(0)", [{"input": "4", "output": "5"}], reveal_details=False)
    assert "input" not in tests[0] and "expected" not in tests[0]
