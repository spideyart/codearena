"""In-memory submissions and leaderboard.

Kept in memory on purpose for the demo, like a judge's session state:
no database, no signup, no cost. A server restart (or a cold start on
serverless hosting) clears submissions — the problems themselves are
static and always available.
"""

import datetime

SUBMISSIONS = []
_NEXT_ID = 1


def add_submission(handle, problem_id, verdict, passed, total, code):
    global _NEXT_ID
    submission = {
        "id": _NEXT_ID,
        "handle": handle,
        "problem_id": problem_id,
        "verdict": verdict,
        "passed": passed,
        "total": total,
        "code": code,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    _NEXT_ID += 1
    SUBMISSIONS.append(submission)
    return submission


def leaderboard():
    """Ranked by problems solved, then fewest submissions."""
    by_handle = {}
    for sub in SUBMISSIONS:
        entry = by_handle.setdefault(
            sub["handle"], {"handle": sub["handle"], "solved": set(), "submissions": 0, "accepted": 0}
        )
        entry["submissions"] += 1
        if sub["verdict"] == "Accepted":
            entry["solved"].add(sub["problem_id"])
            entry["accepted"] += 1
    rows = [
        {
            "handle": e["handle"],
            "solved": len(e["solved"]),
            "submissions": e["submissions"],
            "accepted": e["accepted"],
        }
        for e in by_handle.values()
    ]
    rows.sort(key=lambda r: (-r["solved"], r["submissions"]))
    for i, row in enumerate(rows, start=1):
        row["rank"] = i
    return rows


def recent_submissions(handle=None, limit=20):
    items = SUBMISSIONS
    if handle:
        items = [s for s in items if s["handle"] == handle]
    return list(reversed(items[-limit:]))
