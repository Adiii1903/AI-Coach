"""
End-to-end test for the Task Manager API.
Run from the backend/ directory:  python test_tasks.py
"""
import urllib.request
import urllib.error
import json
import time

BASE = "http://localhost:8000/api/v1"
EMAIL = f"tester_{int(time.time())}@aicoach.com"
PASS = "Test1234"
RESULTS = []
ERRORS = []


def req(method, path, body=None, token=None):
    url = BASE + path
    # Always encode a body so Content-Length is set correctly
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


# ── 1. Signup ──────────────────────────────────────────────────────────────────
code, body = req("POST", "/auth/signup", {"email": EMAIL, "password": PASS, "name": "API Tester"})
check("Signup", code, 201, body, body.get("message", str(body)))

# ── 2. Login ───────────────────────────────────────────────────────────────────
code, body = req("POST", "/auth/login", {"email": EMAIL, "password": PASS})
# login returns TokenResponse directly at root (not wrapped in success_response)
token = body.get("access_token", "") or body.get("data", {}).get("access_token", "")
check("Login", code, 200, body, f"token={'ok' if token else 'MISSING'}")

# ── 3. Create task ─────────────────────────────────────────────────────────────
code, body = req("POST", "/tasks", {"title": "Buy milk", "description": "Whole milk 2L", "priority": "high"}, token)
task = body.get("data", {})
tid = task.get("id", "")
check("Create task", code, 201, body,
      f"id={tid[:8]}... title={task.get('title')} priority={task.get('priority')} is_completed={task.get('is_completed')}")

# ── 4. GET all tasks ───────────────────────────────────────────────────────────
code, body = req("GET", "/tasks", token=token)
tasks = body.get("data", [])
check("Get tasks", code, 200, body, f"count={len(tasks)} first_title={tasks[0]['title'] if tasks else 'none'}")

# ── 5. Update task ─────────────────────────────────────────────────────────────
code, body = req("PUT", f"/tasks/{tid}", {"title": "Buy milk (updated)", "priority": "low"}, token)
ud = body.get("data", {})
check("Update task", code, 200, body, f"title={ud.get('title')} priority={ud.get('priority')}")

# ── 6. Complete task ───────────────────────────────────────────────────────────
code, body = req("PATCH", f"/tasks/{tid}/complete", token=token)
pd = body.get("data", {})
check("Complete task", code, 200, body, f"is_completed={pd.get('is_completed')}")

# ── 7. Ownership enforcement (different user should get 403) ──────────────────
EMAIL2 = f"other_{int(time.time())}@aicoach.com"
req("POST", "/auth/signup", {"email": EMAIL2, "password": PASS, "name": "Other"})
_, b2 = req("POST", "/auth/login", {"email": EMAIL2, "password": PASS})
tok2 = b2.get("access_token", "") or b2.get("data", {}).get("access_token", "")
code, body = req("DELETE", f"/tasks/{tid}", token=tok2)
check("Ownership 403", code, 403, body, f"error={body.get('error', str(body))[:50]}")

# ── 8. Delete task (correct owner) ────────────────────────────────────────────
code, body = req("DELETE", f"/tasks/{tid}", token=token)
check("Delete task", code, 200, body, f"message={body.get('message', '')}")

# ── 9. Verify task list is empty ───────────────────────────────────────────────
code, body = req("GET", "/tasks", token=token)
remaining = len(body.get("data", []))
check("Verify empty", code, 200, body, f"tasks_remaining={remaining} (expected 0)")

# ── Report ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"  AI COACH — Task Manager API Test Results")
print("=" * 60)
for status, label, code, expected, extra in RESULTS:
    icon = "[OK]" if status == "PASS" else "[FAIL]"
    print(f"  {icon} {label:<22} HTTP {code}  {extra}")
print("=" * 60)
passed = sum(1 for s, *_ in RESULTS if s == "PASS")
total = len(RESULTS)
print(f"  {passed}/{total} tests passed")
if ERRORS:
    print("\nFAILURES:")
    for e in ERRORS:
        print(f"  - {e}")
print("=" * 60)
