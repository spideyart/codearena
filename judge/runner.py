"""Safe-enough Python runner for a student demo judge.

This is NOT production-grade isolation (that needs containers or a
sandbox like gVisor/Firecracker). For a demo it combines three layers:

1. Static check: the code is parsed with ast, and dangerous constructs
   are rejected before anything runs — no imports except math, no
   open/eval/exec/__import__/getattr, no private/dunder attribute access.
2. Isolated interpreter: code runs as a separate process with
   `python -I -s` (isolated, no user site-packages) from a temp file
   that is deleted after the run.
3. Timeout: 2 seconds per test case. A loop that never ends becomes
   "Time Limit Exceeded", not a hung server.

Verdicts: Accepted, Wrong Answer, Runtime Error, Time Limit Exceeded,
Compilation Error, Blocked.
"""

import ast
import subprocess
import sys
import tempfile

MAX_CODE_CHARS = 10000
TIMEOUT_SECONDS = 2
ALLOWED_IMPORTS = {"math"}
BANNED_NAMES = {
    "open", "eval", "exec", "__import__", "compile", "globals", "locals",
    "vars", "getattr", "setattr", "delattr", "breakpoint", "help",
    "exit", "quit", "input",  # input is re-allowed below; see check()
}
# input() is required for stdin problems, so it is allowed explicitly.
BANNED_NAMES.discard("input")


class BlockedError(Exception):
    pass


def check_code(code):
    """Raise BlockedError or SyntaxError for unsafe / unparsable code."""
    if len(code) > MAX_CODE_CHARS:
        raise BlockedError(f"Code is too long (max {MAX_CODE_CHARS} characters).")
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise exc
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = []
            if isinstance(node, ast.Import):
                modules = [a.name for a in node.names]
            elif node.module:
                modules = [node.module]
            for module in modules:
                root = module.split(".")[0]
                if root not in ALLOWED_IMPORTS:
                    raise BlockedError(f"Import not allowed: {module}")
        if isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            raise BlockedError(f"Not allowed: {node.id}")
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            raise BlockedError(f"Private attribute access not allowed: {node.attr}")


def _normalise(text):
    """Compare outputs ignoring trailing spaces and final newlines."""
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def run_test(code, test_input, expected_output):
    """Run one test case. Returns dict with passed, verdict, output, detail."""
    try:
        check_code(code)
    except SyntaxError as exc:
        return {
            "passed": False,
            "verdict": "Compilation Error",
            "output": "",
            "detail": f"Syntax error, line {exc.lineno}: {exc.msg}",
        }
    except BlockedError as exc:
        return {
            "passed": False,
            "verdict": "Blocked",
            "output": "",
            "detail": str(exc),
        }
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-s", tmp_path],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "verdict": "Time Limit Exceeded",
            "output": "",
            "detail": "Code ran longer than 2 seconds on this test.",
        }
    finally:
        import os

        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    if result.returncode != 0:
        return {
            "passed": False,
            "verdict": "Runtime Error",
            "output": result.stdout,
            "detail": (result.stderr or "Runtime error").strip()[-500:],
        }
    passed = _normalise(result.stdout) == _normalise(expected_output)
    return {
        "passed": passed,
        "verdict": "Accepted" if passed else "Wrong Answer",
        "output": result.stdout,
        "detail": "" if passed else "Output did not match the expected output.",
    }


def judge(code, tests, reveal_details=True):
    """Run all tests. Returns (verdict, passed, total, per_test list).

    If reveal_details is False (hidden tests), per-test entries carry
    only passed/verdict, never the hidden input or expected output.
    """
    per_test = []
    passed_count = 0
    verdict = "Accepted"
    for i, test in enumerate(tests):
        result = run_test(code, test["input"], test["output"])
        if result["passed"]:
            passed_count += 1
        elif verdict == "Accepted":
            verdict = result["verdict"]
        entry = {"index": i, "passed": result["passed"], "verdict": result["verdict"]}
        if reveal_details:
            entry["input"] = test["input"]
            entry["expected"] = test["output"]
            entry["output"] = result["output"]
            entry["detail"] = result["detail"]
        else:
            entry["detail"] = result["detail"] if result["verdict"] in ("Runtime Error", "Time Limit Exceeded", "Blocked", "Compilation Error") else ""
        per_test.append(entry)
    return verdict, passed_count, len(tests), per_test
