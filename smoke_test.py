"""Quick smoke test for EAM-AI backend key endpoints"""
import os
import requests, json, sys
from urllib.parse import urlparse

BASE = os.getenv("EAM_API_BASE", "http://localhost:8000")
if urlparse(BASE).hostname not in {"localhost", "127.0.0.1"}:
    raise SystemExit("Refusing to run smoke tests against non-localhost EAM_API_BASE")

def test(method, desc, path, data=None, token=None):
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    try:
        if method == 'GET':
            r = requests.get(f'{BASE}{path}', headers=headers, timeout=30)
        else:
            r = requests.post(f'{BASE}{path}', json=data, headers=headers, timeout=60)
        result = 'OK' if r.status_code == 200 else f'FAIL({r.status_code})'
        body = json.dumps(r.json(), ensure_ascii=False)[:80]
        print(f'  [{result}] {desc} -> {body}')
        return r.status_code == 200
    except Exception as e:
        print(f'  [ERROR] {desc} -> {e}')
        return False

all_ok = True

# Login
tokens = {}
login_users = [
    ("admin", os.getenv("EAM_ADMIN_PASSWORD", "")),
    ("supervisor01", os.getenv("EAM_SUPERVISOR_PASSWORD", "")),
    ("engineer01", os.getenv("EAM_ENGINEER_PASSWORD", "")),
    ("purchaser01", os.getenv("EAM_PURCHASER_PASSWORD", "")),
    ("leader01", os.getenv("EAM_LEADER_PASSWORD", "")),
]
for u,p in login_users:
    if not p:
        print(f'[SKIP] Login {u}: password env var is not set')
        all_ok = False
        continue
    r = requests.post(f'{BASE}/api/v1/common/auth/login', json={'username':u,'password':p}, timeout=10)
    if r.status_code == 200:
        tokens[u] = r.json()['data']['access_token']
        print(f'[OK] Login {u}')
    else:
        print(f'[FAIL] Login {u}: {r.status_code}')
        all_ok = False

# Admin
all_ok &= test('GET', 'Admin: users list', '/api/v1/common/auth/users', token=tokens.get('admin'))
all_ok &= test('POST', 'Admin: assign role', '/api/v1/common/auth/assign-role', {'user_id':2,'role':'engineer'}, tokens.get('admin'))

# Supervisor
sup = tokens.get('supervisor01')
all_ok &= test('GET', 'Supervisor: dispatch list', '/api/v1/supervisor/dispatch/list', token=sup)
all_ok &= test('GET', 'Supervisor: dispatch engineers', '/api/v1/supervisor/dispatch/engineers', token=sup)
all_ok &= test('POST', 'Supervisor: dispatch recommend', '/api/v1/supervisor/dispatch/recommend', {'location':'2号车间','engineers':[{'id':1,'name':'张工','skills':{'电气':80,'机械':70},'distance':5}]}, sup)

# Engineer
eng = tokens.get('engineer01')
all_ok &= test('POST', 'Engineer: exam start', '/api/v1/engineer/exam/start', {'exam_type':'virtual_fault'}, eng)

# Leader
lea = tokens.get('leader01')
all_ok &= test('GET', 'Leader: approval list', '/api/v1/leader/dashboard/approval-list', token=lea)
all_ok &= test('GET', 'Leader: metrics', '/api/v1/leader/dashboard/metrics', token=lea)
all_ok &= test('POST', 'Leader: approval action', '/api/v1/leader/dashboard/approval-action', {'approval_id':'REQ-001','action':'approve','comment':'同意'}, lea)

# Purchaser
pur = tokens.get('purchaser01')
all_ok &= test('POST', 'Purchaser: quotation compare', '/api/v1/purchaser/quotation/compare', {'spare_part_name':'轴承','quotations':[{'supplier':'A','price':100}]}, pur)
all_ok &= test('POST', 'Purchaser: contract review', '/api/v1/purchaser/contract/review', {'contract_text':'甲方采购设备合同','contract_type':'purchase'}, pur)
all_ok &= test('POST', 'Purchaser: risk check', '/api/v1/purchaser/supplier/risk-check', {'supplier_id':1,'supplier':{'name':'XX公司','credit':'A'}}, pur)

print(f'\n{"="*40}')
print(f'ALL TESTS {"PASSED" if all_ok else "HAD FAILURES"}')
sys.exit(0 if all_ok else 1)