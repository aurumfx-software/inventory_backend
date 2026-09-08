import sys
import os
import json
import urllib.request
import urllib.error

def verify_users():
    test_credentials = [
        {"role": "Super Administrator", "email": "inventory.test.admin@gmail.com", "code": "EMP001", "name": "System Admin"},
        {"role": "Employee / Requester", "email": "inventory.test.employee@gmail.com", "code": "EMP002", "name": "Rahul Employee"},
        {"role": "Department Manager", "email": "inventory.test.manager@gmail.com", "code": "EMP003", "name": "Arun Department Manager"},
        {"role": "Store Manager", "email": "inventory.test.store@gmail.com", "code": "EMP004", "name": "Suresh Store Manager"},
        {"role": "Purchase Manager", "email": "inventory.test.purchase@gmail.com", "code": "EMP005", "name": "Vishnu Purchase Manager"},
        {"role": "Finance User", "email": "inventory.test.finance@gmail.com", "code": "EMP006", "name": "Anjali Finance"},
        {"role": "Auditor", "email": "inventory.test.auditor@gmail.com", "code": "EMP007", "name": "Audit User"},
        {"role": "Director / High-Level Approver", "email": "inventory.test.director@gmail.com", "code": "EMP008", "name": "Rajesh Director"}
    ]

    print("\n========================================================")
    print("VERIFYING 8 TEST USERS & AUTHENTICATION IN POSTGRESQL")
    print("========================================================\n")

    url = "http://127.0.0.1:8000/api/auth/login"
    password = "Test@123"

    all_passed = True
    for cred in test_credentials:
        payload = json.dumps({"email": cred["email"], "password": password}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})

        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode("utf-8"))
                if res.get("success") and res.get("user"):
                    u = res["user"]
                    print(f"[OK] PASSED LOGIN: {cred['role']}")
                    print(f"   - Name: {u.get('name')} | Email: {u.get('email')}")
                    print(f"   - Code: {u.get('emp_code')} | Role: {u.get('role')} ({u.get('role_id')})")
                    print(f"   - Token: {res.get('token')[:25]}...\n")
                else:
                    print(f"[FAIL] FAILED LOGIN: {cred['email']} - Invalid Response")
                    all_passed = False
        except Exception as e:
            print(f"[FAIL] ERROR LOGIN: {cred['email']} - {e}")
            all_passed = False

    if all_passed:
        print("[SUCCESS] ALL 8 TEST USERS VERIFIED SUCCESSFULLY IN POSTGRESQL DATABASE!\n")
    else:
        print("⚠️ SOME TEST USER VERIFICATIONS FAILED.\n")

if __name__ == "__main__":
    verify_users()
