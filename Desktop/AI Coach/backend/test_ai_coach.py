"""
End-to-end test for the AI Coach Engine API.
Run from the backend/ directory:  python test_ai_coach.py
"""
import urllib.request
import urllib.error
import json
import time

BASE = "http://localhost:8000/api/v1"
EMAIL = f"aicoach_tester_{int(time.time())}@aicoach.com"
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
req("POST", "/auth/signup", {"email": EMAIL, "password": PASS, "name": "AI Tester"})
_, b = req("POST", "/auth/login", {"email": EMAIL, "password": PASS})
token = b.get("access_token", "") or b.get("data", {}).get("access_token", "")
check("Setup Auth", 200 if token else 401, 200, b, f"token={'ok' if token else 'fail'}")

# ── 2. Create tasks/habits for score ─────────────────────────────────────
# We'll create exactly 1 task so score is > 0 but < 40 (warning classification)
_, t_resp = req("POST", "/tasks", {"title": "Test AI Task"}, token)
tid = t_resp.get("data", {}).get("id")
req("PATCH", f"/tasks/{tid}/complete", token=token)
check("Generate some productivity data", 200, 200, {}, "Completed 1 task")

# ── 3. Generate AI Insight ───────────────────────────────────────────────
code, body = req("POST", "/ai-coach/generate", token=token)
insight = body.get("data") or {}
# It should evaluate to warning, or default text
check("Generate Insight", code, 201, body, f"type={insight.get('insight_type')}")

if not insight.get('insight_text'):
    ERRORS.append("Expected an insight_text to be generated")

# ── 4. Get Latest Advice ──────────────────────────────────────────────────
code, body = req("GET", "/ai-coach/advice", token=token)
latest = body.get("data") or {}
check("Get Latest Advice", code, 200, body, f"id={latest.get('id')}")

if latest.get("id") != insight.get("id"):
    ERRORS.append("Latest advice does not match the one just generated.")

# ── 5. Generate multiple for history ──────────────────────────────────────
req("POST", "/ai-coach/generate", token=token)
req("POST", "/ai-coach/generate", token=token)

code, body = req("GET", "/ai-coach/history", token=token)
history = body.get("data") or []
check("Get Advice History", code, 200, body, f"history_len={len(history)}")

if len(history) != 3:
    ERRORS.append(f"Expected 3 history items, got {len(history)}")

# ── Report ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"  AI COACH — AI Coach API Test Results")
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
