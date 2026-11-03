"""Special judges for problems with more than one correct answer.

Most CodeArena problems have a single correct output, and those are
checked by exact (whitespace-normalised) comparison in judge/runner.py.

A few problems are different: several outputs are all genuinely
correct. For those, exact comparison would wrongly reject a correct
program, so a validator function checks *validity* instead: given the
test input and the program's output, is this output a correct answer?

Validators live only on the server. They are never sent to the browser,
so they reveal no hidden test data — only the validity rule, which is
also stated in the problem statement.
"""


def _ints(text):
    return list(map(int, text.split()))


def validate_two_sum(test_input, output):
    """Any pair of indices i < j with arr[i] + arr[j] == target."""
    try:
        lines = test_input.strip().splitlines()
        n = int(lines[0].strip())
        arr = _ints(lines[1])
        target = int(lines[2].strip())
        i, j = _ints(output.strip())
    except (ValueError, IndexError):
        return False
    if len(arr) != n or not (0 <= i < j < n):
        return False
    return arr[i] + arr[j] == target


def validate_binary_search(test_input, output):
    """Any index holding the target, or -1 when it is absent."""
    try:
        lines = test_input.strip().splitlines()
        arr = _ints(lines[1])
        target = int(lines[2].strip())
        k = int(output.strip())
    except (ValueError, IndexError):
        return False
    if target in arr:
        return 0 <= k < len(arr) and arr[k] == target
    return k == -1


def validate_longest_word(test_input, output):
    """Any word of maximum length in the sentence."""
    words = test_input.split()
    word = output.strip()
    if not words or " " in word:
        return False
    return word in words and len(word) == max(len(w) for w in words)


def validate_most_frequent(test_input, output):
    """Any value whose frequency is maximal."""
    try:
        lines = test_input.strip().splitlines()
        arr = _ints(lines[1])
        value = int(output.strip())
    except (ValueError, IndexError):
        return False
    if value not in arr:
        return False
    return arr.count(value) == max(arr.count(x) for x in set(arr))


VALIDATORS = {
    "two-sum-indices": validate_two_sum,
    "binary-search-index": validate_binary_search,
    "longest-word": validate_longest_word,
    "most-frequent": validate_most_frequent,
}


def get_validator(problem_id):
    """Return the special judge for a problem, or None for exact match."""
    return VALIDATORS.get(problem_id)
