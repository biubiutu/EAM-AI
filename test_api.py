import os
import requests, json
from urllib.parse import urlparse

BASE = os.getenv("EAM_API_BASE", "http://localhost:8000")
if urlparse(BASE).hostname not in {"localhost", "127.0.0.1"}:
    raise SystemExit("Refusing to run API tests against non-localhost EAM_API_BASE")
tokens = {}

def login(u, p):
    if not p:
        print(f'LOGIN {u}: skipped, password env var is not set')
        return None
    r = requests.post(f'{BASE}/api/v1/common/auth/login', json={'username': u, 'password': p})
    d = r.json()
    if r.status_code == 200:
        tokens[u] = d['data']['access_token']
    role = d.get("data", {}).get("role", "-")
    print(f'LOGIN {u}: {r.status_code} role={role}')
    return d['data']['access_token'] if r.status_code == 200 else None

# Login all
login('admin', os.getenv("EAM_ADMIN_PASSWORD", ""))
login('supervisor01', os.getenv("EAM_SUPERVISOR_PASSWORD", ""))
login('engineer01', os.getenv("EAM_ENGINEER_PASSWORD", ""))
login('purchaser01', os.getenv("EAM_PURCHASER_PASSWORD", ""))
login('leader01', os.getenv("EAM_LEADER_PASSWORD", ""))

missing_users = {"admin", "supervisor01", "engineer01", "purchaser01", "leader01"} - set(tokens)
if missing_users:
    raise SystemExit(f"Missing login tokens for: {', '.join(sorted(missing_users))}")

def test(method, path, data=None, token=None, is_get=False):
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    if is_get:
        r = requests.get(f'{BASE}{path}', headers=headers)
    elif data is not None:
        r = requests.post(f'{BASE}{path}', json=data, headers=headers)
    else:
        r = requests.post(f'{BASE}{path}', headers=headers)
    status = r.status_code
    try:
        body = json.dumps(r.json(), ensure_ascii=False)[:300]
    except:
        body = r.text[:300]
    print(f'{method} {path}: {status} -> {body}')
    return r

print('\n========== ADMIN ==========')
test('GET', '/api/v1/common/auth/users', token=tokens['admin'], is_get=True)
test('POST', '/api/v1/common/auth/assign-role', {'user_id': 2, 'role': 'engineer'}, token=tokens['admin'])

print('\n========== SUPERVISOR ==========')
sup = tokens['supervisor01']
test('POST', '/api/v1/supervisor/equipment/check-bom', {'equipment_id': 1, 'bom_items': [], 'repair_records': []}, sup)
test('POST', '/api/v1/supervisor/requisition/analyze', {'spare_part_id': 1, 'requested_quantity': 2, 'requester_id': 1}, sup)
test('GET', '/api/v1/supervisor/dispatch/list', token=sup, is_get=True)
test('GET', '/api/v1/supervisor/dispatch/engineers', token=sup, is_get=True)
test('POST', '/api/v1/supervisor/dispatch/recommend', {'location':'2号车间','engineers':[{'id':1,'name':'张工','skills':{'电气':80,'机械':70},'distance':5}]}, sup)
test('POST', '/api/v1/supervisor/dispatch/create', {'engineer_id':2,'engineer_name':'张工','location':'2号车间','distance':5}, sup)

print('\n========== ENGINEER ==========')
eng = tokens['engineer01']
test('POST', '/api/v1/engineer/diagnosis/diagnose', {'fault_desc':'设备异响','equipment_id':1}, eng)
test('POST', '/api/v1/engineer/knowledge/search', {'question':'如何维修空压机','top_k':3}, eng)
test('POST', '/api/v1/engineer/knowledge/fault-cases/search', {'question':'电机过热','top_k':5}, eng)
test('POST', '/api/v1/engineer/knowledge/ingest-case', {'fault_desc':'电机烧毁','fault_type':'电气','resolution':'更换绕组'}, eng)
test('POST', '/api/v1/engineer/exam/start', {'exam_type':'virtual_fault'}, eng)
test('POST', '/api/v1/engineer/exam/submit', {'exam_type':'virtual_fault','answers':['检查电源','清理散热器','更换保险丝']}, eng)

print('\n========== LEADER ==========')
lea = tokens['leader01']
test('GET', '/api/v1/leader/dashboard/approval-list', token=lea, is_get=True)
test('POST', '/api/v1/leader/dashboard/approval-action', {'approval_id':'REQ-001','action':'approve','comment':'同意采购'}, lea)
test('GET', '/api/v1/leader/dashboard/metrics', token=lea, is_get=True)
test('POST', '/api/v1/leader/dashboard/query', {'question':'查询本月采购总额'}, lea)

print('\n========== PURCHASER ==========')
pur = tokens['purchaser01']
test('POST', '/api/v1/purchaser/quotation/compare', {'spare_part_name':'轴承','quotations':[{'supplier':'A公司','price':100}]}, pur)
test('POST', '/api/v1/purchaser/contract/review', {'contract_text':'甲方采购设备...','contract_type':'purchase'}, pur)
test('POST', '/api/v1/purchaser/supplier/risk-check', {'supplier_id':1,'supplier':{'name':'XX公司','credit':'A'}}, pur)
test('POST', '/api/v1/purchaser/supplier/price-trend', {'commodity_name':'铜'}, pur)
test('POST', '/api/v1/purchaser/supplier/sourcing', {'spare_part_name':'轴承','requirements':'高精度'}, pur)

print('\n========== ALL DONE ==========')