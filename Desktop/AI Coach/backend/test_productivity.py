"""
End-to-end test for the Productivity Score Engine API.
Run from the backend/ directory:  python test_productivity.py
"""
import urllib.request
import urllib.error
import json
import time
from datetime import date

BASE = "http://localhost:8000/api/v1"
EMAIL = f"prod_tester_{int(time.time())}@aicoach.com"
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

# ── 1. Create User & Login ───────────────────────────────────────────────
req("POST", "/auth/signup", {"email": EMAIL, "password": PASS, "name": "Prod Tester"})
_, b = req("POST", "/auth/login", {"email": EMAIL, "password": PASS})
token = b.get("access_token", "") or b.get("data", {}).get("access_token", "")
check("Setup Auth", 200 if token else 401, 200, b, f"token={'ok' if token else 'fail'}")

# ── 2. Create and Complete Tasks (3 tasks = 30 points) ───────────────────
for i in range(3):
    _, t_resp = req("POST", "/tasks", {"title": f"Task {i}", "priority": "medium"}, token)
    tid = t_resp.get("data", {}).get("id")
    req("PATCH", f"/tasks/{tid}/complete", token=token)

check("Created and completed 3 tasks", 200, 200, {}, "Expected +30 points")

# ── 3. Create and Log Habits (2 habits = 20 points) ──────────────────────
for i in range(2):
    _, h_resp = req("POST", "/habits", {"name": f"Habit {i}", "target_frequency": "daily"}, token)
    hid = h_resp.get("data", {}).get("id")
    req("POST", f"/habits/{hid}/log", token=token)
    
check("Created and logged 2 habits", 200, 200, {}, "Expected +20 points")

# ── 4. Create Study Sessions (120 minutes = 2 hours = 20 points) ─────────
req("POST", "/study-sessions", {"subject": "Math", "duration_minutes": 120}, token)
check("Logged 2 hours of study time", 200, 200, {}, "Expected +20 points")

# ── 5. Fetch Productivity Score ──────────────────────────────────────────
code, p_resp = req("GET", "/productivity/score", token=token)
p_data = p_resp.get("data", {})
score = p_data.get("productivity_score")
tasks_completed = p_data.get("tasks_completed_today")
study_hours = p_data.get("study_hours_today")
habits_completed = p_data.get("habits_completed_today")

check("Productivity Score Calculation", code, 200, p_resp, f"score={score} tasks={tasks_completed} study={study_hours}h habits={habits_completed}")

if score != 70:
    ERRORS.append(f"Expected productivity_score=70, got {score}")
if tasks_completed != 3:
    ERRORS.append(f"Expected tasks_completed=3, got {tasks_completed}")
if study_hours != 2.0:
    ERRORS.append(f"Expected study_hours=2.0, got {study_hours}")
if habits_completed != 2:
    ERRORS.append(f"Expected habits_completed=2, got {habits_completed}")

# ── 6. Fetch Dashboard Stats (Ensure integration works) ──────────────────
code, d_resp = req("GET", "/dashboard", token=token)
d_data = d_resp.get("data", {})
d_score = d_data.get("productivity_score")
check("Dashboard Score Integration", code, 200, d_resp, f"dashboard_score={d_score}")

if d_score != 70:
    ERRORS.append(f"Expected dashboard productivity_score=70, got {d_score}")

# ── Report ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"  AI COACH — Productivity Score API Test Results")
print("=" * 60)
for status, label, code, expected, extra in RESULTS:
    icon = "[OK]" if status == "PASS" else "[FAIL]"
    print(f"  {icon} {label:<35} HTTP {code}  {extra}")
print("=" * 60)
passed = sum(1 for s, *_ in RESULTS if s == "PASS")
total_tests = len(RESULTS)
print(f"  {passed}/{total_tests} tests passed")
if ERRORS:
    print("\nFAILURES:")
    for e in ERRORS:
        print(f"  - {e}")
print("=" * 60)
