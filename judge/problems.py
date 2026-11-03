"""Seeded problems for CodeArena.

Hidden tests are server-only. The public API never returns them:
problems.py keeps them here, and app.py strips them before responding.
Each problem's starter code uses only input()/print(), so it passes
the runner's safety check.
"""

PROBLEMS = [
    {
        "id": "sum-two",
        "title": "Sum of Two Numbers",
        "difficulty": "Easy",
        "statement": "Read two integers separated by a space and print their sum.",
        "input_format": "A single line with two integers a and b.",
        "output_format": "A single integer, a + b.",
        "constraints": "-1000 <= a, b <= 1000",
        "starter_code": "a, b = map(int, input().split())\nprint(a + b)\n",
        "samples": [
            {"input": "3 4", "output": "7"},
            {"input": "10 -3", "output": "7"},
        ],
        "hidden": [
            {"input": "0 0", "output": "0"},
            {"input": "100 200", "output": "300"},
            {"input": "-5 -7", "output": "-12"},
        ],
    },
    {
        "id": "even-odd",
        "title": "Even or Odd",
        "difficulty": "Easy",
        "statement": "Read one integer and print 'Even' if it is even, otherwise 'Odd'.",
        "input_format": "A single integer n.",
        "output_format": "Even or Odd, exactly as shown.",
        "constraints": "-10000 <= n <= 10000",
        "starter_code": "n = int(input())\nprint('Even' if n % 2 == 0 else 'Odd')\n",
        "samples": [
            {"input": "4", "output": "Even"},
            {"input": "7", "output": "Odd"},
        ],
        "hidden": [
            {"input": "0", "output": "Even"},
            {"input": "-3", "output": "Odd"},
            {"input": "100", "output": "Even"},
        ],
    },
    {
        "id": "reverse-string",
        "title": "Reverse a String",
        "difficulty": "Easy",
        "statement": "Read one line of text and print it reversed.",
        "input_format": "A single line of text (may contain spaces).",
        "output_format": "The same text, reversed.",
        "constraints": "1 <= length <= 1000",
        "starter_code": "s = input()\nprint(s[::-1])\n",
        "samples": [
            {"input": "hello", "output": "olleh"},
            {"input": "Code", "output": "edoC"},
        ],
        "hidden": [
            {"input": "a", "output": "a"},
            {"input": "racecar", "output": "racecar"},
            {"input": "hello world", "output": "dlrow olleh"},
        ],
    },
    {
        "id": "sum-array",
        "title": "Sum of an Array",
        "difficulty": "Medium",
        "statement": "The first line has n, the number of elements. The second line has n integers. Print their sum.",
        "input_format": "Line 1: n. Line 2: n integers separated by spaces.",
        "output_format": "A single integer, the sum.",
        "constraints": "1 <= n <= 1000, each value between -1000 and 1000",
        "starter_code": "n = int(input())\narr = list(map(int, input().split()))\nprint(sum(arr))\n",
        "samples": [
            {"input": "3\n1 2 3", "output": "6"},
            {"input": "4\n-1 5 0 2", "output": "6"},
        ],
        "hidden": [
            {"input": "1\n42", "output": "42"},
            {"input": "5\n10 20 30 40 50", "output": "150"},
            {"input": "3\n-5 -5 10", "output": "0"},
        ],
    },
    {
        "id": "prime-check",
        "title": "Prime Check",
        "difficulty": "Medium",
        "statement": "Read one integer and print 'Prime' if it is a prime number, otherwise 'Not Prime'. Note: 1 is not prime.",
        "input_format": "A single integer n.",
        "output_format": "Prime or Not Prime, exactly as shown.",
        "constraints": "1 <= n <= 10000",
        "starter_code": (
            "n = int(input())\n"
            "is_prime = n > 1\n"
            "i = 2\n"
            "while i * i <= n:\n"
            "    if n % i == 0:\n"
            "        is_prime = False\n"
            "        break\n"
            "    i += 1\n"
            "print('Prime' if is_prime else 'Not Prime')\n"
        ),
        "samples": [
            {"input": "7", "output": "Prime"},
            {"input": "8", "output": "Not Prime"},
        ],
        "hidden": [
            {"input": "1", "output": "Not Prime"},
            {"input": "2", "output": "Prime"},
            {"input": "97", "output": "Prime"},
            {"input": "100", "output": "Not Prime"},
        ],
    },
]


def get_problem(problem_id):
    for problem in PROBLEMS:
        if problem["id"] == problem_id:
            return problem
    return None


def public_problem(problem):
    """Problem as sent to the browser: samples only, never hidden tests."""
    return {key: value for key, value in problem.items() if key != "hidden"}


def public_problems():
    return [public_problem(p) for p in PROBLEMS]
