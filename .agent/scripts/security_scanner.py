"""Automated Security & Vulnerability Scanner for AI-Career-Agent.

Inspects backend, AI module, and frontend codebase for OWASP Top 10 vulnerabilities,
dangerous patterns, secrets leakage, and misconfigurations.
"""

import os
import re
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent

# Vulnerability rules for static analysis
RULES = [
    {
        "id": "SEC-001",
        "name": "Hardcoded Secrets / API Keys",
        "pattern": re.compile(r"""(?i)(sk-[a-zA-Z0-9]{20,}|AIzaSy[a-zA-Z0-9_-]{33}|password\s*=\s*['"][^'"]{6,}['"]|secret_key\s*=\s*['"][^'"]{6,}['"])"""),
        "severity": "CRITICAL",
        "desc": "Hardcoded API keys, tokens, or credentials found in source code.",
    },
    {
        "id": "SEC-002",
        "name": "Dangerous Execution / Command Injection",
        "pattern": re.compile(r"\b(eval|exec|os\.system|subprocess\.Popen|subprocess\.call|subprocess\.run)\s*\("),
        "severity": "HIGH",
        "desc": "Potential arbitrary code/command execution pattern.",
    },
    {
        "id": "SEC-003",
        "name": "Insecure Deserialization",
        "pattern": re.compile(r"\b(pickle\.loads?|yaml\.load\s*\([^,)]+\))"),
        "severity": "HIGH",
        "desc": "Insecure deserialization of untrusted payloads.",
    },
    {
        "id": "SEC-004",
        "name": "SQL Injection (Unparameterized Queries)",
        "pattern": re.compile(r"""(?:execute|raw|query)\s*\(\s*f['"].*?\b(?:SELECT|INSERT|UPDATE|DELETE)\b""", re.IGNORECASE),
        "severity": "CRITICAL",
        "desc": "Raw string formatting used in SQL query execution.",
        "extensions": {".py"},
    },
    {
        "id": "SEC-005",
        "name": "Frontend XSS (Unsanitized HTML Injection)",
        "pattern": re.compile(r"dangerouslySetInnerHTML\s*=\s*\{\{\s*__html:\s*(?!DOMPurify)"),
        "severity": "HIGH",
        "desc": "dangerouslySetInnerHTML used without DOMPurify sanitization.",
    },
    {
        "id": "SEC-006",
        "name": "Path Traversal in File Operations",
        "pattern": re.compile(r"""open\s*\(\s*f?['"].*\{.*(?:filename|path|file_path).*\}"""),
        "severity": "MEDIUM",
        "desc": "Unsanitized dynamic filename directly passed into open().",
    },
]

EXCLUDE_DIRS = {".git", ".pytest_cache", "node_modules", "dist", ".agents", "build", "__pycache__", "venv", ".venv"}


def scan_file(file_path: Path) -> list[dict]:
    findings = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    lines = content.splitlines()
    for rule in RULES:
        if "extensions" in rule and file_path.suffix.lower() not in rule["extensions"]:
            continue
        for idx, line in enumerate(lines, start=1):
            # Skip test files and comment lines for some rules
            stripped = line.strip()
            if stripped.startswith(("#", "//", "/*", "*")):
                continue
            if "test_" in file_path.name or "mock" in file_path.name.lower():
                continue

            match = rule["pattern"].search(line)
            if match:
                findings.append({
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "severity": rule["severity"],
                    "file": str(file_path.relative_to(WORKSPACE)),
                    "line": idx,
                    "content": stripped[:120],
                    "desc": rule["desc"],
                })
    return findings


def run_scan() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    print("=" * 60)
    print(" [SECURITY] AI-CAREER-AGENT AUTOMATED SECURITY SCANNER ")
    print("=" * 60)

    target_dirs = [WORKSPACE / "be", WORKSPACE / "ai", WORKSPACE / "fe" / "src"]
    total_files = 0
    all_findings = []

    for target in target_dirs:
        if not target.exists():
            continue
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in {".py", ".ts", ".tsx", ".js", ".jsx", ".html"}:
                    total_files += 1
                    file_path = Path(root) / file
                    findings = scan_file(file_path)
                    all_findings.extend(findings)

    print(f"\n[INFO] Scanned {total_files} source files across backend, AI core, and frontend.\n")

    if not all_findings:
        print("[SUCCESS] NO CRITICAL / HIGH STATIC SECURITY VULNERABILITIES FOUND!")
        print("   - SQL Injection: 0 findings")
        print("   - Code/Command Injection: 0 findings")
        print("   - Hardcoded Secrets: 0 findings")
        print("   - Unsanitized Frontend HTML: 0 findings")
        print("   - Insecure Deserialization: 0 findings\n")
    else:
        print(f"[WARNING] Found {len(all_findings)} potential security findings:")
        for f in all_findings:
            print(f"  [{f['severity']}] {f['rule_id']} - {f['rule_name']}")
            print(f"    File: {f['file']}:{f['line']}")
            print(f"    Code: {f['content']}")
            print(f"    Desc: {f['desc']}\n")

    print("=" * 60)
    return len(all_findings)


if __name__ == "__main__":
    sys.exit(run_scan())
