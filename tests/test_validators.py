"""Tests for the special judges (multi-answer problems)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from judge.runner import judge
from judge.validators import get_validator


def _verdict(code, tests, problem_id):
    verdict, passed, total, _ = judge(
        code, tests, reveal_details=True, validator=get_validator(problem_id)
    )
    return verdict, passed, total


# Two-sum: the hidden case 4 / -1 0 1 2 / target 1 has TWO valid pairs,
# "0 3" (-1 + 2) and "1 2" (0 + 1). Both must be accepted now.
TWO_SUM_TESTS = [{"input": "4\n-1 0 1 2\n1", "output": "0 3"}]
ALT_PAIR_CODE = (
    "n = int(input())\narr = list(map(int, input().split()))\n"
    "target = int(input())\n"
    "for i in range(n - 1, -1, -1):\n"
    "    for j in range(i + 1, n):\n"
    "        if arr[i] + arr[j] == target:\n"
    "            print(i, j)\n            raise SystemExit\n"
)
WRONG_PAIR_CODE = "print('0 1')\n"


def test_two_sum_alternative_pair_accepted():
    assert _verdict(ALT_PAIR_CODE, TWO_SUM_TESTS, "two-sum-indices") == ("Accepted", 1, 1)


def test_two_sum_wrong_pair_rejected():
    verdict, passed, _ = _verdict(WRONG_PAIR_CODE, TWO_SUM_TESTS, "two-sum-indices")
    assert verdict == "Wrong Answer" and passed == 0


def test_binary_search_duplicate_index_accepted():
    tests = [{"input": "5\n2 2 2 5 9\n2", "output": "0"}]
    assert _verdict("print(2)\n", tests, "binary-search-index") == ("Accepted", 1, 1)
    assert _verdict("print(-1)\n", tests, "binary-search-index")[0] == "Wrong Answer"


def test_binary_search_absent_returns_minus_one():
    tests = [{"input": "4\n2 4 6 8\n5", "output": "-1"}]
    assert _verdict("print(-1)\n", tests, "binary-search-index") == ("Accepted", 1, 1)


def test_longest_word_any_tied_word_accepted():
    tests = [{"input": "the quick brown fox", "output": "quick"}]
    assert _verdict("print('brown')\n", tests, "longest-word") == ("Accepted", 1, 1)
    assert _verdict("print('the')\n", tests, "longest-word")[0] == "Wrong Answer"


def test_most_frequent_any_tied_value_accepted():
    tests = [{"input": "4\n4 4 1 1", "output": "1"}]
    assert _verdict("print(4)\n", tests, "most-frequent") == ("Accepted", 1, 1)
    assert _verdict("print(9)\n", tests, "most-frequent")[0] == "Wrong Answer"


def test_no_validator_for_single_answer_problem():
    assert get_validator("sum-two") is None
    assert get_validator("climbing-stairs") is None
