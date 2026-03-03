"""
End-to-end test for the Habit Tracker API.
Run from the backend/ directory:  python test_habits.py
"""
import urllib.request
import urllib.error
import json
import time
from datetime import date

BASE = "http://localhost:8000/api/v1"
EMAIL = f"habit_tester_{int(time.time())}@aicoach.com"
PASS = "Test1234"
RESULTS = []
ERRORS = []


def req(method, path, body=None, token=None):
    url = BASE + path
    if body is not None:
        data = json.dumps(body).encode()
    elif method in ("PATCH", "PUT", "POST"):
        data = b"{}"
    else:
        data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        return e.code, json.loads(raw) if raw else {}


def check(label, code, expected, body, extra=""):
    ok = code == expected
    status = "PASS" if ok else "FAIL"
    RESULTS.append((status, label, code, expected, extra))
    if not ok:
        ERRORS.append(f"{label}: got {code}, expected {expected}. body={body}")
    return ok


# ── 1. Create User & Login ─────────────────────────────────────────────────────
req("POST", "/auth/signup", {"email": EMAIL, "password": PASS, "name": "Habit Tester"})
_, b = req("POST", "/auth/login", {"email": EMAIL, "password": PASS})
token = b.get("access_token", "") or b.get("data", {}).get("access_token", "")
check("Setup Auth", 200 if token else 401, 200, b, f"token={'ok' if token else 'fail'}")

# ── 2. Create Habit ────────────────────────────────────────────────────────────
code, body = req("POST", "/habits", {"name": "Read book", "description": "10 pages daily", "target_frequency": "daily"}, token)
habit = body.get("data", {})
hid = habit.get("id", "")
check("Create habit", code, 201, body, f"name={habit.get('name')} streak={habit.get('current_streak')}")

# ── 3. GET all habits ──────────────────────────────────────────────────────────
code, body = req("GET", "/habits", token=token)
habits = body.get("data", [])
check("Get habits", code, 200, body, f"count={len(habits)}")

# ── 4. Log habit today (streak should be 1) ────────────────────────────────────
code, body = req("POST", f"/habits/{hid}/log", token=token)
log_result = body.get("data", {})
streak = log_result.get("current_streak")
check("Log habit (first time)", code, 200, body, f"new_streak={streak}")
if streak != 1:
    ERRORS.append(f"Expected streak=1 after first log, got {streak}")

# ── 5. Attempt duplicate log today (should fail with 400) ──────────────────────
code, body = req("POST", f"/habits/{hid}/log", token=token)
check("Log duplicate (400)", code, 400, body, f"error={body.get('error', '')}")

# ── 6. Update habit ────────────────────────────────────────────────────────────
code, body = req("PUT", f"/habits/{hid}", {"description": "15 pages daily"}, token)
check("Update habit", code, 200, body, f"desc={body.get('data', {}).get('description')}")

# ── 7. Ownership enforcement (different user should get 403) ──────────────────
EMAIL2 = f"other_{int(time.time())}@aicoach.com"
req("POST", "/auth/signup", {"email": EMAIL2, "password": PASS, "name": "Other"})
_, b2 = req("POST", "/auth/login", {"email": EMAIL2, "password": PASS})
tok2 = b2.get("access_token", "") or b2.get("data", {}).get("access_token", "")
code, body = req("POST", f"/habits/{hid}/log", token=tok2)
check("Ownership 403", code, 403, body, f"error={body.get('error', str(body))[:50]}")

# ── 8. Delete habit (correct owner) ────────────────────────────────────────────
code, body = req("DELETE", f"/habits/{hid}", token=token)
check("Delete habit", code, 200, body, f"message={body.get('message', '')}")

# ── 9. Verify habit list is empty ──────────────────────────────────────────────
code, body = req("GET", "/habits", token=token)
remaining = len(body.get("data", []))
check("Verify empty", code, 200, body, f"habits_remaining={remaining} (expected 0)")

# ── Report ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"  AI COACH — Habit Tracker API Test Results")
print("=" * 60)
for status, label, code, expected, extra in RESULTS:
    icon = "[OK]" if status == "PASS" else "[FAIL]"
    print(f"  {icon} {label:<24} HTTP {code}  {extra}")
print("=" * 60)
passed = sum(1 for s, *_ in RESULTS if s == "PASS")
total = len(RESULTS)
print(f"  {passed}/{total} tests passed")
if ERRORS:
    print("\nFAILURES:")
    for e in ERRORS:
        print(f"  - {e}")
print("=" * 60)
