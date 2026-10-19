"""Validate YAML frontmatter of agent, skill and factory files (marketplace crawler rules)."""
import re, sys, glob, yaml

REQUIRED = {"agent": ["name", "description", "author"],
            "skill": ["name", "description", "author"],
            "factory": ["name", "description", "owner", "authors"]}
SUPPORT = {"Self-Serve", "Best Effort Support", "Dedicated Capacity"}

def frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    return yaml.safe_load(m.group(1)) if m else None

bad = 0
targets = [(p, "agent") for p in glob.glob("agents/*.md") + glob.glob("agents/*/*.md")]
targets += [(p, "skill") for p in glob.glob("skills/*/SKILL.md")]
targets += [(p, "factory") for p in glob.glob("FACTORY.md") + glob.glob("factories/*/FACTORY.md")]
for path, kind in targets:
    try:
        fm = frontmatter(path)
    except yaml.YAMLError as e:
        print(f"FAIL {path}: YAML error: {e}"); bad += 1; continue
    if not isinstance(fm, dict):
        print(f"FAIL {path}: no frontmatter"); bad += 1; continue
    missing = [k for k in REQUIRED[kind] if k not in fm]
    problems = [f"missing {k}" for k in missing]
    if kind in ("agent", "skill") and "author" in fm and "<" not in str(fm["author"]):
        problems.append("author has no <email>")
    if kind == "factory":
        if fm.get("support_level") not in SUPPORT:
            problems.append(f"support_level invalid: {fm.get('support_level')!r}")
        if isinstance(fm.get("sdlc_phase"), list) or "," in str(fm.get("sdlc_phase", "")):
            problems.append("sdlc_phase must be a single value")
        if "project_deployments" in fm and fm["project_deployments"] == []:
            problems.append("project_deployments is an empty list (omit it)")
    parts = path.replace("\\", "/").split("/")
    # a FACTORY.md in the repository root has no parent folder to name-check
    if len(parts) > 1 and not re.fullmatch(r"[A-Za-z0-9_-]+", parts[-2]):
        problems.append("folder name has forbidden characters")
    if problems:
        print(f"FAIL {path}: " + "; ".join(problems)); bad += 1
    else:
        print(f"ok   {path}  name={fm['name']!r}")
print(f"\n{len(targets)} files, {bad} failing")
sys.exit(1 if bad else 0)
