"""Shared, standard-library-only active-plan parsing for assessment and archival."""
import re
from pathlib import Path


def field(text, name, default="Unknown"):
    match = re.search(r"^\*\*" + re.escape(name) + r"\*\*:\s*([^\n]+)", text, re.M)
    return match.group(1).strip() if match else default


def normalize(raw, criteria=()):
    for status in ("Completed", "In Progress", "Not Started", "Ready"):
        if raw.lower() == status.lower():
            return status
    if criteria and all(c["done"] for c in criteria):
        return "Completed"
    return raw


def metadata(path):
    text = Path(path).read_text()
    tasks = []
    pattern = r"^### ((?:TASK|REF)-\d+): ([^\n]+)\n(.*?)(?=^### (?:TASK|REF)-\d+:|^## |\Z)"
    for key, title, body in re.findall(pattern, text, re.M | re.S):
        criteria = [{"done": flag.lower() == "x", "text": label}
                    for flag, label in re.findall(r"^- \[([ xX])\] (.+)$", body, re.M)]
        tasks.append({"taskId": key, "title": title.strip(),
                      "status": normalize(field(body, "Status"), criteria),
                      "dependencies": field(body, "Dependencies", "None"),
                      "completionCriteria": criteria})
    if not tasks:
        for line in text.splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            match = re.fullmatch(r"((?:TASK|REF)-\d+)(?:\s+(.+))?", cells[0])
            if not match or len(cells) < 2:
                continue
            key, title = match.groups()
            raw = cells[2] if title and len(cells) > 2 else cells[1]
            tasks.append({"taskId": key, "title": title or key,
                          "status": normalize(raw), "dependencies": "See plan dependencies table",
                          "completionCriteria": []})
    status = normalize(field(text, "Status"))
    return {"status": status, "tasks": tasks,
            "designReference": field(text, "Design Reference", "Unspecified"),
            "complete": status == "Completed" and all(t["status"] == "Completed" for t in tasks)}


def plan_files(directory):
    return sorted(p for p in Path(directory).glob("*.md") if p.is_file() and not p.is_symlink())
