#!/usr/bin/env python3
"""Fail-closed, dependency-free factory release policy helpers."""
import argparse
import json
import re
import sys
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
HIGH_RISK = (
    ".github/workflows/", "terraform/", "infra/", "infrastructure/",
    "migrations/", "database/migrations/", "iam/", "secrets/",
    "docker-compose", "dockerfile", ".tf", ".tfvars",
    "scripts/release_safety.py", "scripts/preflight.sh",
    "scripts/smoke_test.sh", "scripts/terraform_drift.sh",
)
LOW_RISK = ("docs/", "README.md")

def risk(paths):
    if not paths or not all(isinstance(p, str) and p for p in paths):
        return "high"
    for path in paths:
        normalized = path.lower().lstrip("./")
        if ".." in Path(normalized).parts or any(s in normalized for s in HIGH_RISK):
            return "high"
        if not (normalized.startswith("docs/") or normalized == "readme.md"):
            return "high"
    return "low"

def validate_promotion(source, target, sha, digest):
    if target not in ("test", "production") or not SHA.fullmatch(sha) or not DIGEST.fullmatch(digest):
        return False
    required = "dev" if target == "test" else "test"
    record = source.get(required, {})
    return (record.get("commit_sha") == sha and record.get("image_digest") == digest
            and record.get("smoke_passed") is True and record.get("approved") is True)

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    r = sub.add_parser("risk")
    r.add_argument("paths", nargs="+")
    p = sub.add_parser("promotion")
    p.add_argument("--manifest", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--sha", required=True)
    p.add_argument("--digest", required=True)
    args = parser.parse_args()
    if args.command == "risk":
        outcome = risk(args.paths)
        print(outcome)
        return 0 if outcome == "low" else 2
    manifest = json.loads(Path(args.manifest).read_text())
    valid = validate_promotion(manifest, args.target, args.sha, args.digest)
    print("Promotion provenance valid" if valid else "Promotion blocked")
    return 0 if valid else 1

if __name__ == "__main__":
    sys.exit(main())
