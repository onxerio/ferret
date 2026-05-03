# ============================================================
#  FERRET - report.py
#  Generates HTML and JSON reports from findings
# ============================================================

import json
import os
from datetime import datetime
from colorama import Fore, Style, init
init(autoreset=True)

GREEN  = Fore.GREEN
RED    = Fore.RED
YELLOW = Fore.YELLOW
CYAN   = Fore.CYAN
BOLD   = Style.BRIGHT
RESET  = Style.RESET_ALL

class Report:
    def __init__(self, target_url, findings=None):
        self.target_url = target_url
        self.findings   = findings or {}
        self.timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.filename   = f"ferret_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def add(self, section, data):
        """Add findings from a module"""
        self.findings[section] = data

    def _severity(self, findings_count):
        if findings_count == 0:
            return "NONE", "#95a5a6"
        elif findings_count <= 2:
            return "LOW", "#f39c12"
        elif findings_count <= 5:
            return "MEDIUM", "#e67e22"
        else:
            return "HIGH", "#e74c3c"

    def save_json(self):
        """Save raw findings as JSON"""
        output = {
            "tool":      "Ferret",
            "version":   "1.0.0",
            "author":    "Juggernaut",
            "target":    self.target_url,
            "timestamp": self.timestamp,
            "findings":  self.findings
        }
        filename = f"{self.filename}.json"
        with open(filename, "w") as f:
            json.dump(output, f, indent=4, default=str)
        print(f"{GREEN}[+] JSON report saved: {filename}{RESET}")
        return filename

    def save_html(self):
        """Generate professional HTML report"""
        total = sum(
            len(v) if isinstance(v, list) else (1 if v else 0)
            for v in self.findings.values()
        )
        severity, color = self._severity(total)

        # Build findings HTML
        findings_html = ""
        for section, data in self.findings.items():
            findings_html += f"""
            <div class="section">
                <h2>{section.upper()}</h2>
            """
            if isinstance(data, list):
                if not data:
                    findings_html += '<p class="none">No findings in this section.</p>'
                for item in data:
                    findings_html += '<div class="finding">'
                    for key, value in item.items():
                        findings_html += f"""
                        <div class="row">
                            <span class="key">{key}</span>
                            <span class="val">{value}</span>
                        </div>
                        """
                    findings_html += '</div>'
            elif isinstance(data, dict):
                if not data:
                    findings_html += '<p class="none">No findings in this section.</p>'
                for key, value in data.items():
                    findings_html += f"""
                    <div class="finding">
                        <div class="row">
                            <span class="key">{key}</span>
                            <span class="val">{value}</span>
                        </div>
                    </div>
                    """
            findings_html += '</div>'

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Ferret Report — {self.target_url}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: 'Courier New', monospace; background:#0d1117; color:#c9d1d9; padding:30px; }}
  .header {{ background:#161b22; border:1px solid #30363d; border-radius:8px; padding:30px; margin-bottom:24px; }}
  .header h1 {{ font-size:32px; color:#58a6ff; letter-spacing:2px; }}
  .header h1 span {{ color:#f85149; }}
  .meta {{ margin-top:16px; display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
  .meta-item {{ background:#0d1117; padding:10px 14px; border-radius:6px; border:1px solid #30363d; }}
  .meta-item .label {{ font-size:11px; color:#8b949e; text-transform:uppercase; }}
  .meta-item .value {{ font-size:14px; color:#e6edf3; margin-top:4px; }}
  .severity {{ display:inline-block; background:{color}; color:#fff; padding:6px 16px; border-radius:4px; font-weight:bold; font-size:14px; margin-top:16px; }}
  .section {{ background:#161b22; border:1px solid #30363d; border-radius:8px; padding:24px; margin-bottom:20px; }}
  .section h2 {{ color:#58a6ff; font-size:16px; text-transform:uppercase; letter-spacing:1px; margin-bottom:16px; border-bottom:1px solid #30363d; padding-bottom:10px; }}
  .finding {{ background:#0d1117; border:1px solid #30363d; border-radius:6px; padding:14px; margin-bottom:12px; }}
  .row {{ display:flex; gap:16px; margin-bottom:6px; }}
  .key {{ color:#8b949e; min-width:120px; font-size:13px; }}
  .val {{ color:#e6edf3; font-size:13px; word-break:break-all; }}
  .none {{ color:#8b949e; font-style:italic; }}
  .footer {{ text-align:center; color:#8b949e; font-size:12px; margin-top:30px; }}
</style>
</head>
<body>
<div class="header">
  <h1><span>FERRET</span> — NoSQL Injection Report</h1>
  <div class="meta">
    <div class="meta-item"><div class="label">Target</div><div class="value">{self.target_url}</div></div>
    <div class="meta-item"><div class="label">Timestamp</div><div class="value">{self.timestamp}</div></div>
    <div class="meta-item"><div class="label">Total Findings</div><div class="value">{total}</div></div>
    <div class="meta-item"><div class="label">Author</div><div class="value">Juggernaut</div></div>
  </div>
  <div class="severity">SEVERITY: {severity}</div>
</div>

{findings_html}

<div class="footer">
  Generated by Ferret v1.0.0 — github.com/onxerio/ferret — "It always finds what's buried"
</div>
</body>
</html>"""

        filename = f"{self.filename}.html"
        with open(filename, "w") as f:
            f.write(html)
        print(f"{GREEN}[+] HTML report saved: {filename}{RESET}")
        return filename

    def run(self):
        """Save both report formats"""
        print(f"\n{CYAN}{BOLD}[*] Generating reports...{RESET}\n")
        json_file = self.save_json()
        html_file = self.save_html()
        print(f"\n{GREEN}{BOLD}[*] Reports ready:{RESET}")
        print(f"  {YELLOW}→ {json_file}{RESET}")
        print(f"  {YELLOW}→ {html_file}{RESET}\n")
        return json_file, html_file