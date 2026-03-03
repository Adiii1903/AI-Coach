"""
End-to-end test for the AI Study Planner Engine API.
Run from the backend/ directory:  python test_study_plan.py
"""
import urllib.request
import urllib.error
import json
import time

BASE = "http://localhost:8000/api/v1"
EMAIL = f"planner_tester_{int(time.time())}@aicoach.com"
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
req("POST", "/auth/signup", {"email": EMAIL, "password": PASS, "name": "Planner Tester"})
_, b = req("POST", "/auth/login", {"email": EMAIL, "password": PASS})
token = b.get("access_token", "") or b.get("data", {}).get("access_token", "")
check("Setup Auth", 200 if token else 401, 200, b, f"token={'ok' if token else 'fail'}")

# ── 2. Create tasks/habits for score context ─────────────────────────────
_, t_resp = req("POST", "/tasks", {"title": "Test Planner Task"}, token)
tid = t_resp.get("data", {}).get("id")
req("PATCH", f"/tasks/{tid}/complete", token=token)
check("Generate productivity data", 200, 200, {}, "Completed 1 task for score baseline")

# ── 3. Generate initial study plan ───────────────────────────────────────
code, body = req("POST", "/study-plan/generate", token=token)
plan = body.get("data", {})
check("Generate Study Plan", code, 201, body, f"length={len(plan.get('plan_text', ''))}")

if not plan.get('plan_text'):
    ERRORS.append("Expected a plan_text to be generated")

# ── 4. Get Today's Plan ──────────────────────────────────────────────────
code, body = req("GET", "/study-plan/today", token=token)
today_plan = body.get("data", {})
check("Get Today's Plan", code, 200, body, f"id={today_plan.get('id')}")

if today_plan.get("id") != plan.get("id"):
    ERRORS.append("Today's fetched plan does not match the one just generated.")

# ── 5. Generate multiple for history limit check ─────────────────────────
req("POST", "/study-plan/generate", token=token)

code, body = req("GET", "/study-plan/history", token=token)
history = body.get("data", [])
check("Get Study Plan History", code, 200, body, f"history_len={len(history)}")

if len(history) != 2:
    ERRORS.append(f"Expected 2 history items (multi generate), got {len(history)}")

# ── Report ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"  AI COACH — AI Study Planner API Test Results")
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
