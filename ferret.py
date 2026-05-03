#!/usr/bin/env python3
# ============================================================
#  FERRET - NoSQL Injection Testing Tool
#  Author  : Juggernaut
#  GitHub  : github.com/onxerio/ferret
#  Version : 1.0.0
#  Target  : MongoDB
#  Tag     : vibecoded 
# ============================================================

import argparse
import sys
import json
from modules.detect import Detector
from modules.bypass import Bypass
from modules.extract import Extractor
from modules.blind import BlindDetector
from modules.report import Report

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    RED    = Fore.RED
    GREEN  = Fore.GREEN
    YELLOW = Fore.YELLOW
    CYAN   = Fore.CYAN
    BLUE   = Fore.BLUE
    BOLD   = Style.BRIGHT
    RESET  = Style.RESET_ALL
except ImportError:
    RED=GREEN=YELLOW=CYAN=BLUE=BOLD=RESET=""

BANNER = f"""
{RED}{BOLD}
  ███████╗███████╗██████╗ ██████╗ ███████╗████████╗
  ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝
  █████╗  █████╗  ██████╔╝██████╔╝█████╗     ██║   
  ██╔══╝  ██╔══╝  ██╔══██╗██╔══██╗██╔══╝     ██║   
  ██║     ███████╗██║  ██║██║  ██║███████╗   ██║   
  ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   
{RESET}
{CYAN}  NoSQL Injection Testing Tool v1.0.0{RESET}
{YELLOW}  Author  : Juggernaut{RESET}
{YELLOW}  GitHub  : github.com/onxerio/ferret{RESET}
{YELLOW}  Tagline : "It always finds what's buried"{RESET}
{RED}  Target  : MongoDB{RESET}
"""

def parse_args():
    parser = argparse.ArgumentParser(
        prog="ferret",
        description="Ferret — NoSQL Injection Testing Tool",
        epilog="Example: python ferret.py -u http://target.com/api/login --bypass"
    )

    # Target
    parser.add_argument(
        "-u", "--url",
        required=True,
        help="Target URL (e.g. http://target.com/api/login)"
    )

    # Parameters
    parser.add_argument(
        "-p", "--params",
        default="username:admin,password:admin",
        help="Parameters to test as key:value pairs separated by comma (default: username:admin,password:admin)"
    )

    # Method
    parser.add_argument(
        "-m", "--method",
        default="POST",
        choices=["GET", "POST"],
        help="HTTP method (default: POST)"
    )

    # Fields
    parser.add_argument(
        "--username-field",
        default="username",
        help="Username field name (default: username)"
    )
    parser.add_argument(
        "--password-field",
        default="password",
        help="Password field name (default: password)"
    )

    # Modes
    parser.add_argument(
        "--detect",
        action="store_true",
        help="Run injection point detection"
    )
    parser.add_argument(
        "--bypass",
        action="store_true",
        help="Attempt login bypass"
    )
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Extract usernames and passwords"
    )
    parser.add_argument(
        "--blind",
        action="store_true",
        help="Run blind injection detection"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all modules"
    )

    # Extra
    parser.add_argument(
        "--usernames",
        default=None,
        help="Comma separated list of usernames to test during extraction"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay threshold for blind detection in seconds (default: 2.0)"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate HTML and JSON report"
    )
    parser.add_argument(
        "--headers",
        default=None,
        help='Custom headers as JSON string (e.g. \'{"Authorization": "Bearer token"}\')'
    )

    return parser.parse_args()


def parse_params(params_str):
    """Parse key:value,key:value into dict"""
    params = {}
    try:
        for pair in params_str.split(","):
            key, value = pair.strip().split(":")
            params[key.strip()] = value.strip()
    except ValueError:
        print(f"[ERROR] Invalid params format. Use: key:value,key:value")
        sys.exit(1)
    return params


def main():
    print(BANNER)
    args = parse_args()

    # Parse params
    params = parse_params(args.params)

    # Parse custom headers
    headers = {"Content-Type": "application/json"}
    if args.headers:
        try:
            custom = json.loads(args.headers)
            headers.update(custom)
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid headers JSON format")
            sys.exit(1)

    # Parse usernames list
    usernames = None
    if args.usernames:
        usernames = [u.strip() for u in args.usernames.split(",")]

    # Report collector
    report = Report(target_url=args.url)
    ran_any = False

    # ── DETECT ──────────────────────────────────────────────
    if args.detect or args.all:
        ran_any = True
        detector = Detector(
            url=args.url,
            params=params,
            headers=headers,
            method=args.method,
            timeout=args.timeout
        )
        findings = detector.run()
        report.add("Detection", findings)

    # ── BYPASS ──────────────────────────────────────────────
    if args.bypass or args.all:
        ran_any = True
        bypass = Bypass(
            url=args.url,
            username_field=args.username_field,
            password_field=args.password_field,
            headers=headers,
            method=args.method,
            timeout=args.timeout
        )
        results = bypass.run()
        report.add("Login Bypass", results)

    # ── EXTRACT ─────────────────────────────────────────────
    if args.extract or args.all:
        ran_any = True
        extractor = Extractor(
            url=args.url,
            username_field=args.username_field,
            password_field=args.password_field,
            headers=headers,
            method=args.method,
            timeout=args.timeout
        )
        extracted = extractor.run(usernames=usernames)
        report.add("Extraction", extracted)

    # ── BLIND ───────────────────────────────────────────────
    if args.blind or args.all:
        ran_any = True
        blind = BlindDetector(
            url=args.url,
            params=params,
            headers=headers,
            method=args.method,
            timeout=args.timeout + 10,
            delay_threshold=args.delay
        )
        findings = blind.run()
        report.add("Blind Detection", findings)

    # ── REPORT ──────────────────────────────────────────────
    if args.report and ran_any:
        report.run()

    if not ran_any:
        print(f"{YELLOW}[!] No mode selected. Use --detect, --bypass, --extract, --blind or --all{RESET}")
        print(f"{YELLOW}[!] Use --help for usage info{RESET}\n")


if __name__ == "__main__":
    main()