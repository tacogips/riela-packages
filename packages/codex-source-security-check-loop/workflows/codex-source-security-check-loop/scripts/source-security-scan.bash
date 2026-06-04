#!/usr/bin/env bash
set -euo pipefail

mailbox_dir="${RIEL_MAILBOX_DIR:?RIEL_MAILBOX_DIR is required}"
output_path="${mailbox_dir}/outbox/output.json"
mkdir -p "$(dirname "$output_path")"

target="${1:-.}"
if [[ -z "$target" ]]; then
  target="."
fi

if [[ ! -e "$target" ]]; then
  python3 - "$output_path" "$target" <<'PY'
import json
import sys

output_path, target = sys.argv[1:]
payload = {
    "status": "failed",
    "targetPath": target,
    "error": f"target path does not exist: {target}",
    "methods": [],
    "findings": [
        {
            "id": "SCAN-TARGET-MISSING",
            "method": "setup",
            "severity": "high",
            "file": target,
            "line": None,
            "message": "Target path does not exist, so security scanning could not run.",
            "evidence": target,
        }
    ],
    "coverageGaps": ["target path missing"],
}
with open(output_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
PY
  exit 0
fi

target="$(cd "$target" && pwd)"
scan_tmp="$(mktemp -d)"
trap 'rm -rf "$scan_tmp"' EXIT

run_network_audits="${SECURITY_RUN_NETWORK_AUDITS:-false}"
max_findings="${SECURITY_MAX_FINDINGS:-50}"
include_paths="${SECURITY_INCLUDE_PATHS:-}"
exclude_paths="${SECURITY_EXCLUDE_PATHS:-}"

if [[ ! "$max_findings" =~ ^[0-9]+$ ]] || [[ "$max_findings" -le 0 ]]; then
  max_findings=50
fi

python3 - "$output_path" "$target" "$scan_tmp" "$run_network_audits" "$max_findings" "$include_paths" "$exclude_paths" <<'PY'
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

output_path, target, scan_tmp, run_network_audits, max_findings, include_paths, exclude_paths = sys.argv[1:]
target_path = Path(target)
scan_tmp_path = Path(scan_tmp)
max_findings = int(max_findings)
network_allowed = run_network_audits.lower() == "true"

default_excludes = {
    ".git",
    ".hg",
    ".svn",
    ".rielflow",
    ".next",
    ".turbo",
    ".cache",
    ".venv",
    "venv",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "coverage",
    "target",
    "tmp",
    "temp",
    "__pycache__",
}

binary_suffixes = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tgz",
    ".bz2",
    ".xz",
    ".7z",
    ".tar",
    ".lockb",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".wasm",
    ".so",
    ".dylib",
    ".a",
    ".o",
    ".class",
    ".jar",
}

text_suffixes = {
    ".bash",
    ".c",
    ".cc",
    ".cfg",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".env",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".kts",
    ".lua",
    ".md",
    ".mjs",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scala",
    ".sh",
    ".sql",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


def split_paths(raw):
    if not raw:
        return []
    parts = []
    for chunk in raw.replace("\n", ",").split(","):
        chunk = chunk.strip()
        if chunk:
            parts.append(chunk)
    return parts


extra_excludes = set(split_paths(exclude_paths))
include_filters = split_paths(include_paths)


def relpath(path):
    try:
        return str(path.relative_to(target_path))
    except ValueError:
        return str(path)


def is_excluded(path):
    rel = relpath(path)
    parts = set(Path(rel).parts)
    if parts & default_excludes:
        return True
    for pattern in extra_excludes:
        if rel == pattern or rel.startswith(pattern.rstrip("/") + "/"):
            return True
    if include_filters:
        return not any(rel == pattern or rel.startswith(pattern.rstrip("/") + "/") for pattern in include_filters)
    return False


def is_text_candidate(path):
    if path.suffix.lower() in binary_suffixes:
        return False
    if path.suffix.lower() in text_suffixes:
        return True
    if path.name in {"Dockerfile", "Containerfile", "Makefile", "Taskfile.yml", "Brewfile"}:
        return True
    return path.stat().st_size <= 256 * 1024


def read_text(path):
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data[:4096]:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return data.decode("latin-1")
        except UnicodeDecodeError:
            return None


def collect_files():
    files = []
    if target_path.is_file():
        return [target_path] if is_text_candidate(target_path) else []
    for root, dirs, names in os.walk(target_path):
        root_path = Path(root)
        dirs[:] = [
            d
            for d in dirs
            if not is_excluded(root_path / d)
        ]
        for name in names:
            path = root_path / name
            if is_excluded(path):
                continue
            try:
                if path.is_file() and is_text_candidate(path):
                    files.append(path)
            except OSError:
                continue
    return files


files = collect_files()
commands = []
coverage_gaps = []
findings = []
methods = []


def add_finding(method, severity, file, line, message, evidence, check_id):
    if sum(1 for finding in findings if finding["method"] == method) >= max_findings:
        return
    findings.append(
        {
            "id": f"{method.upper()}-{check_id}-{sum(1 for finding in findings if finding['method'] == method) + 1:03d}",
            "method": method,
            "severity": severity,
            "file": file,
            "line": line,
            "message": message,
            "evidence": evidence[:500],
        }
    )


secret_patterns = [
    ("OPENAI_API_KEY", "high", re.compile(r"\bsk-[A-Za-z0-9][A-Za-z0-9_\-]{20,}\b")),
    ("ANTHROPIC_API_KEY", "high", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}\b")),
    ("GITHUB_TOKEN", "high", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    ("AWS_ACCESS_KEY", "high", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("PRIVATE_KEY", "high", re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    (
        "GENERIC_SECRET_ASSIGNMENT",
        "medium",
        re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\b\s*[:=]\s*['\"][^'\"\n]{16,}['\"]"),
    ),
]

for path in files:
    text = read_text(path)
    if text is None:
        continue
    for line_no, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if "example" in lowered or "placeholder" in lowered or "dummy" in lowered:
            continue
        for check_id, severity, pattern in secret_patterns:
            if pattern.search(line):
                add_finding(
                    "secrets",
                    severity,
                    relpath(path),
                    line_no,
                    f"Potential committed secret matched {check_id}.",
                    line.strip(),
                    check_id,
                )

methods.append(
    {
        "name": "secrets",
        "status": "completed",
        "filesScanned": len(files),
        "findingCount": sum(1 for finding in findings if finding["method"] == "secrets"),
    }
)


def run_command(argv, cwd=target_path, timeout=120):
    commands.append({"argv": argv, "cwd": str(cwd)})
    try:
        completed = subprocess.run(
            argv,
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "available": True,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except FileNotFoundError:
        return {"available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
    except subprocess.TimeoutExpired as error:
        return {
            "available": True,
            "returncode": None,
            "stdout": error.stdout or "",
            "stderr": f"command timed out after {timeout}s",
        }


if shutil.which("gitleaks"):
    report = scan_tmp_path / "gitleaks.json"
    result = run_command(
        [
            "gitleaks",
            "detect",
            "--source",
            str(target_path),
            "--no-git",
            "--redact",
            "--report-format",
            "json",
            "--report-path",
            str(report),
        ],
        timeout=240,
    )
    parsed = []
    if report.exists():
        try:
            parsed = json.loads(report.read_text(encoding="utf-8") or "[]")
        except json.JSONDecodeError:
            coverage_gaps.append("gitleaks report was not valid JSON")
    for leak in parsed[:max_findings]:
        add_finding(
            "gitleaks",
            "high",
            leak.get("File") or leak.get("file") or "",
            leak.get("StartLine") or leak.get("line"),
            f"Gitleaks detected {leak.get('RuleID') or leak.get('Description') or 'a secret'}",
            leak.get("Match") or leak.get("Secret") or json.dumps(leak, sort_keys=True),
            str(leak.get("RuleID") or "LEAK"),
        )
    methods.append(
        {
            "name": "gitleaks",
            "status": "completed",
            "available": True,
            "returncode": result["returncode"],
            "findingCount": sum(1 for finding in findings if finding["method"] == "gitleaks"),
        }
    )
else:
    coverage_gaps.append("gitleaks executable not available")
    methods.append({"name": "gitleaks", "status": "skipped", "available": False, "findingCount": 0})

static_rules = [
    ("COMMAND_EXEC", "high", re.compile(r"\b(?:exec|execFile|spawn|system|popen|Runtime\.getRuntime\(\)\.exec)\s*\(")),
    ("EVAL", "high", re.compile(r"\b(?:eval|Function)\s*\(")),
    ("DISABLE_TLS_VERIFY", "high", re.compile(r"NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0")),
    ("INSECURE_RANDOM", "medium", re.compile(r"\bMath\.random\s*\(")),
    ("SQL_CONCAT", "medium", re.compile(r"(?i)(select|insert|update|delete).{0,80}\+")),
    ("INSECURE_HTTP", "medium", re.compile(r"(?i)\bhttp://")),
    ("BROAD_CORS", "medium", re.compile(r"(?i)(Access-Control-Allow-Origin|cors\().{0,80}(\*|origin:\s*true)")),
]

for path in files:
    text = read_text(path)
    if text is None:
        continue
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "#", "*")):
            continue
        if path.name == "source-security-scan.bash" and "re.compile(" in line:
            continue
        for check_id, severity, pattern in static_rules:
            if pattern.search(line):
                add_finding(
                    "static",
                    severity,
                    relpath(path),
                    line_no,
                    f"Static heuristic matched {check_id}. Verify data flow and exploitability.",
                    stripped,
                    check_id,
                )

methods.append(
    {
        "name": "static",
        "status": "completed",
        "filesScanned": len(files),
        "findingCount": sum(1 for finding in findings if finding["method"] == "static"),
    }
)

manifest_names = {
    "package.json",
    "bun.lock",
    "bun.lockb",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "Pipfile.lock",
    "Gemfile.lock",
    "Cargo.lock",
    "go.mod",
    "go.sum",
}
manifests = []
for root, dirs, names in os.walk(target_path):
    root_path = Path(root)
    dirs[:] = [d for d in dirs if not is_excluded(root_path / d)]
    for name in names:
        if name in manifest_names:
            manifests.append(root_path / name)

if network_allowed:
    if (target_path / "package.json").exists() and shutil.which("npm"):
        audit = run_command(["npm", "audit", "--json"], timeout=180)
        if audit["stdout"]:
            try:
                audit_json = json.loads(audit["stdout"])
                vulnerabilities = audit_json.get("vulnerabilities") or {}
                for name, item in list(vulnerabilities.items())[:max_findings]:
                    severity = item.get("severity") or "medium"
                    add_finding(
                        "dependencies",
                        "high" if severity in {"critical", "high"} else "medium",
                        "package.json",
                        None,
                        f"npm audit reported {severity} vulnerability in {name}.",
                        json.dumps(item, sort_keys=True)[:500],
                        "NPM_AUDIT",
                    )
            except json.JSONDecodeError:
                coverage_gaps.append("npm audit output was not valid JSON")
else:
    coverage_gaps.append("network dependency audits skipped; set runNetworkAudits true to enable package-manager audit commands")

methods.append(
    {
        "name": "dependencies",
        "status": "completed",
        "networkAudits": network_allowed,
        "manifestCount": len(manifests),
        "manifests": [relpath(path) for path in manifests[:100]],
        "findingCount": sum(1 for finding in findings if finding["method"] == "dependencies"),
    }
)

for manifest in [path for path in manifests if path.name == "package.json"]:
    try:
        package_json = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception:
        continue
    scripts = package_json.get("scripts") or {}
    for script_name, script_value in scripts.items():
        if not isinstance(script_value, str):
            continue
        if re.search(r"(?i)(curl|wget).{0,80}(\||sh|bash)|postinstall|preinstall|npm\s+install\s+-g", script_value):
            add_finding(
                "supply-chain-config",
                "medium",
                relpath(manifest),
                None,
                f"Package script `{script_name}` needs supply-chain review.",
                script_value,
                "RISKY_PACKAGE_SCRIPT",
            )

for path in files:
    rel = relpath(path)
    if rel.startswith(".github/workflows/") and path.suffix in {".yml", ".yaml"}:
        text = read_text(path) or ""
        if re.search(r"uses:\s+[^@\s]+(?:\s|$)", text):
            add_finding(
                "supply-chain-config",
                "medium",
                rel,
                None,
                "GitHub Action appears unpinned or missing an explicit ref.",
                "uses: without @ref",
                "UNPINNED_GITHUB_ACTION",
            )
        if "pull_request_target" in text:
            add_finding(
                "supply-chain-config",
                "medium",
                rel,
                None,
                "Workflow uses pull_request_target; verify checkout and script injection boundaries.",
                "pull_request_target",
                "PULL_REQUEST_TARGET",
            )

methods.append(
    {
        "name": "supply-chain-config",
        "status": "completed",
        "findingCount": sum(1 for finding in findings if finding["method"] == "supply-chain-config"),
    }
)

severity_order = {"high": 0, "medium": 1, "low": 2}
findings.sort(key=lambda item: (severity_order.get(item["severity"], 9), item["method"], item["file"] or "", item["line"] or 0))
findings = findings[: max_findings * 5]

blocking = [finding for finding in findings if finding["severity"] in {"high", "medium"}]
payload = {
    "status": "completed",
    "targetPath": str(target_path),
    "configuration": {
        "includePaths": include_filters,
        "excludePaths": sorted(default_excludes | extra_excludes),
        "maxFindingsPerMethod": max_findings,
        "runNetworkAudits": network_allowed,
    },
    "methods": methods,
    "commands": commands,
    "findings": findings,
    "summary": {
        "filesScanned": len(files),
        "findingCount": len(findings),
        "high": sum(1 for finding in findings if finding["severity"] == "high"),
        "medium": sum(1 for finding in findings if finding["severity"] == "medium"),
        "low": sum(1 for finding in findings if finding["severity"] == "low"),
        "blockingFindingCount": len(blocking),
        "needsFix": len(blocking) > 0,
    },
    "coverageGaps": coverage_gaps,
}

with open(output_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
PY
