#!/usr/bin/env python3
"""Deterministically validate the public repository using stdlib only."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/codex-harness-classroom"
SKILL = PLUGIN / "skills/build-classroom-harness"

REQUIRED = (
    ".agents/plugins/marketplace.json",
    "plugins/codex-harness-classroom/.codex-plugin/plugin.json",
    "plugins/codex-harness-classroom/skills/build-classroom-harness/SKILL.md",
    "plugins/codex-harness-classroom/skills/build-classroom-harness/references/safety-contract.md",
    "plugins/codex-harness-classroom/skills/build-classroom-harness/references/classroom-flow.md",
    "plugins/codex-harness-classroom/skills/build-classroom-harness/templates/team-spec.template.md",
    "plugins/codex-harness-classroom/skills/build-classroom-harness/scripts/scaffold_harness.py",
    "README_KO.md",
    "README.md",
    "LICENSE",
    "NOTICE",
    "CHANGES_FROM_UPSTREAM.md",
    "THIRD_PARTY_NOTICES.md",
    "docs/research-sources.md",
    "scripts/validate_repo.py",
    "verify.bat",
    "verify.sh",
)
BANNED_RUNTIME = (
    "TeamCreate",
    "SendMessage",
    "TaskCreate",
    ".claude/agents",
    "CLAUDE.md",
    "Opus",
)
CANONICAL = (
    ROOT / "AGENTS.md",
    SKILL / "SKILL.md",
    SKILL / "references/safety-contract.md",
    SKILL / "references/classroom-flow.md",
    SKILL / "templates/team-spec.template.md",
    SKILL / "scripts/scaffold_harness.py",
)
PRIVATE_PATHS = (
    re.compile(r"[A-Za-z]:\\Users\\[^<\s]"),
    re.compile(r"/(?:Users|home)/[^<\s]"),
)
SECRET_PATTERNS = (
    re.compile(r"(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}", re.I),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
)


def validate() -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing required file: {rel}")

    try:
        market = json.loads((ROOT / REQUIRED[0]).read_text(encoding="utf-8"))
        entry = market["plugins"][0]
        if entry["name"] != "codex-harness-classroom":
            errors.append("marketplace plugin name mismatch")
        if entry["source"]["path"] != "./plugins/codex-harness-classroom":
            errors.append("marketplace source path mismatch")
        if not {"installation", "authentication"} <= entry["policy"].keys():
            errors.append("marketplace policy incomplete")
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        errors.append(f"invalid marketplace: {exc}")

    try:
        manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        if manifest.get("name") != PLUGIN.name or manifest.get("skills") != "./skills/":
            errors.append("invalid plugin manifest identity or skills path")
        if manifest.get("version") != "1.0.1":
            errors.append("plugin version must be 1.0.1")
        if manifest.get("author", {}).get("name") != "Jeon Seung-gi":
            errors.append("plugin author mismatch")
        public_repo = "https://github.com/jsk7767/codex-harness-classroom"
        if manifest.get("homepage") != public_repo or manifest.get("repository") != public_repo:
            errors.append("plugin public repository metadata mismatch")
    except (OSError, ValueError) as exc:
        errors.append(f"invalid plugin manifest: {exc}")

    notice = ROOT / "NOTICE"
    if notice.is_file():
        notice_text = notice.read_text(encoding="utf-8")
        for phrase in ("Copyright 2026 Jeon Seung-gi", "Copyright 2025 robin", "Apache License"):
            if phrase not in notice_text:
                errors.append(f"NOTICE missing attribution: {phrase}")

    evidence_example = "[근거: notes/store.md]"
    evidence_drift = (
        "[근거: vault/기준/상대경로.md]",
        "[근거: vault의/상대경로.md]",
        "[근거: 상대경로.md]",
    )
    for path in CANONICAL + (ROOT / "README_KO.md",):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for drift in evidence_drift:
            if drift in text:
                errors.append(f"evidence syntax drift in {path.relative_to(ROOT)}: {drift}")
    safety_text = (SKILL / "references/safety-contract.md").read_text(encoding="utf-8")
    if evidence_example not in safety_text:
        errors.append("safety contract missing canonical evidence syntax")
    scaffolder_text = (SKILL / "scripts/scaffold_harness.py").read_text(encoding="utf-8")
    utf8_contract_paths = (
        SKILL / "SKILL.md",
        SKILL / "references/safety-contract.md",
        SKILL / "scripts/scaffold_harness.py",
        ROOT / "README_KO.md",
    )
    for path in utf8_contract_paths:
        if "UTF-8" not in path.read_text(encoding="utf-8"):
            errors.append(f"Windows UTF-8 safety contract missing: {path.relative_to(ROOT)}")
    required_validator_contracts = (
        'parser.add_argument("--vault", required=True',
        "EXPECTED_SANDBOX",
        '"fact-checker": "read-only"',
        '"content-writer": "workspace-write"',
        '"quality-checker": "read-only"',
        "line.count(\"[근거:\")",
    )
    for contract in required_validator_contracts:
        if contract not in scaffolder_text:
            errors.append(f"generated validator contract missing: {contract}")
    if "CLAIM_WORDS" in scaffolder_text:
        errors.append("brittle CLAIM_WORDS heuristic remains")

    for path in CANONICAL:
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            for residue in BANNED_RUNTIME:
                if residue in text:
                    errors.append(f"banned runtime residue in {path.relative_to(ROOT)}: {residue}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in PRIVATE_PATHS:
            if pattern.search(text):
                errors.append(f"private local path in {path.relative_to(ROOT)}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible secret in {path.relative_to(ROOT)}")
    return sorted(set(errors))


def main() -> int:
    errors = validate()
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: repository validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
