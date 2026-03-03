"""
End-to-end test for the Study Session Tracker API.
Run from the backend/ directory:  python test_study_sessions.py
"""
import urllib.request
import urllib.error
import json
import time

BASE = "http://localhost:8000/api/v1"
EMAIL = f"study_tester_{int(time.time())}@aicoach.com"
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
req("POST", "/auth/signup", {"email": EMAIL, "password": PASS, "name": "Study Tester"})
_, b = req("POST", "/auth/login", {"email": EMAIL, "password": PASS})
token = b.get("access_token", "") or b.get("data", {}).get("access_token", "")
check("Setup Auth", 200 if token else 401, 200, b, f"token={'ok' if token else 'fail'}")

# ── 2. Create Study Session ──────────────────────────────────────────────
code, body = req("POST", "/study-sessions", {
    "subject": "Data Structures",
    "topic": "Binary Trees",
    "duration_minutes": 120,
    "notes": "Learned traversals"
}, token)
session_obj = body.get("data", {})
sid = session_obj.get("id", "")
check("Create session", code, 201, body, f"subject={session_obj.get('subject')} duration={session_obj.get('duration_minutes')}")

# ── 3. Create second session for stats ───────────────────────────────────
code, body = req("POST", "/study-sessions", {
    "subject": "Algorithms",
    "duration_minutes": 30
}, token)
check("Create session 2", code, 201, body, f"duration={body.get('data', {}).get('duration_minutes')}")

# ── 4. GET all sessions ──────────────────────────────────────────────────
code, body = req("GET", "/study-sessions", token=token)
sessions = body.get("data", [])
check("Get sessions", code, 200, body, f"count={len(sessions)}")

# ── 5. Check Stats ───────────────────────────────────────────────────────
code, body = req("GET", "/study-sessions/stats", token=token)
stats = body.get("data", {})
total = stats.get("total_minutes")
today = stats.get("today_minutes")
weekly = stats.get("weekly_minutes")
check("Stats aggregations", code, 200, body, f"total={total} today={today} weekly={weekly}")
if total != 150:
    ERRORS.append(f"Expected total_minutes=150, got {total}")

# ── 6. Update session ────────────────────────────────────────────────────
code, body = req("PUT", f"/study-sessions/{sid}", {"topic": "AVL Trees", "duration_minutes": 150}, token)
updated = body.get("data", {})
check("Update session", code, 200, body, f"topic={updated.get('topic')} duration={updated.get('duration_minutes')}")

# ── 7. Ownership enforcement (different user) ────────────────────────────
EMAIL2 = f"other_{int(time.time())}@aicoach.com"
req("POST", "/auth/signup", {"email": EMAIL2, "password": PASS, "name": "Other"})
_, b2 = req("POST", "/auth/login", {"email": EMAIL2, "password": PASS})
tok2 = b2.get("access_token", "") or b2.get("data", {}).get("access_token", "")
code, body = req("DELETE", f"/study-sessions/{sid}", token=tok2)
check("Ownership 403", code, 403, body, f"error={body.get('error', str(body))[:50]}")

# ── 8. Delete session (correct owner) ───────────────────────────────────
code, body = req("DELETE", f"/study-sessions/{sid}", token=token)
check("Delete session", code, 200, body, f"message={body.get('message', '')}")

# ── Report ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"  AI COACH — Study Session API Test Results")
print("=" * 60)
for status, label, code, expected, extra in RESULTS:
    icon = "[OK]" if status == "PASS" else "[FAIL]"
    print(f"  {icon} {label:<22} HTTP {code}  {extra}")
print("=" * 60)
passed = sum(1 for s, *_ in RESULTS if s == "PASS")
total_tests = len(RESULTS)
print(f"  {passed}/{total_tests} tests passed")
if ERRORS:
    print("\nFAILURES:")
    for e in ERRORS:
        print(f"  - {e}")
print("=" * 60)
