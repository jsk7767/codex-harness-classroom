#!/usr/bin/env python3
"""Create the classroom harness using only the Python standard library."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


AGENTS = """# 가게 홍보팀 하네스

## 역할

- Agent(담당 직원)는 각자 한 가지 책임을 맡는다.
- Skill(업무 매뉴얼)은 담당 직원이 따라야 할 절차다.
- Harness(조직도+업무 순서+검수 규칙)는 담당 직원의 순서와 합격 조건이다.
- Obsidian은 회사 지식창고이며 모든 사업 사실의 유일한 근거다.

## 실행 계약

Main Commander → Fact Checker → Content Writer → Quality Checker → PASS/FAIL 순서로 실행한다.
독립적인 읽기 전용 감사만 병렬로 실행할 수 있다. 같은 파일을 쓰는 담당 직원은 직렬로 실행한다.
메뉴, 가격, 할인, 영업시간, 주차, 후기, 고객 발언 및 기타 사업 사실을 지식창고 근거 없이 만들지 않는다.
근거가 없으면 줄을 `[확인 필요]`로 시작하고 홍보 문구에서 제외한다. 증거는 vault 루트 기준 `[근거: notes/store.md]` 형식만 사용한다.

## 산출물

- Fact Checker: `_workspace/01_fact-check.md`
- Content Writer: `_workspace/promotional-draft.md`
- Quality Checker: `_workspace/03_quality-check.md`
- 완료 전 `python scripts/validate_harness.py --target . --vault <vault>`를 실행한다.
"""

FACT_CHECKER = '''name = "fact-checker"
description = "Obsidian 지식창고에서 홍보 문안에 사용할 사실과 근거를 확인하는 읽기 전용 담당 직원"
sandbox_mode = "read-only"
developer_instructions = """
사용자가 지정한 Obsidian vault만 회사 지식창고로 취급한다. 메뉴, 가격, 할인, 영업시간, 주차, 후기, 고객 발언 및 모든 사업 사실을 원문에서 확인한다. 승인한 사실마다 vault 루트 기준 `[근거: notes/store.md]` 형식의 상대 경로를 붙여 _workspace/01_fact-check.md로 Main Commander에게 전달한다. 근거가 없으면 [확인 필요]로 표시한다. 내용을 추측하거나 홍보 문안을 작성하지 않는다.
"""
'''

CONTENT_WRITER = '''name = "content-writer"
description = "승인된 사실만 사용해 한국어 홍보 문안을 작성하는 담당 직원"
sandbox_mode = "workspace-write"
developer_instructions = """
_workspace/01_fact-check.md에서 승인되고 근거 경로가 있는 사실만 사용한다. _workspace/promotional-draft.md 하나만 작성한다. 메뉴, 가격, 할인, 영업시간, 주차, 후기, 고객 발언이나 다른 사업 사실을 보완하거나 추측하지 않는다. 사실이 부족하면 줄을 `[확인 필요]`로 시작하고 주장하지 않는다. 게시 가능한 모든 내용 줄에 vault 루트 기준 `[근거: notes/store.md]` 형식의 상대 경로를 붙인다.
"""
'''

QUALITY_CHECKER = '''name = "quality-checker"
description = "홍보 문안의 모든 사업 사실을 지식창고와 독립 대조해 PASS 또는 FAIL을 판정하는 읽기 전용 담당 직원"
sandbox_mode = "read-only"
developer_instructions = """
_workspace/promotional-draft.md를 Obsidian vault 원문과 독립적으로 대조한다. 제목과 `[확인 필요]` 줄을 제외한 모든 게시 가능 내용 줄에 vault 루트 기준 `[근거: notes/store.md]` 형식의 근거가 있어야 한다. 경로가 유효하지 않거나 원문과 다르면 FAIL이다. 결과와 수정 지시를 _workspace/03_quality-check.md 형식으로 Main Commander에게 반환한다. 문안을 직접 고치지 않는다.
"""
'''

MARKETING_SKILL = '''---
name: write-grounded-store-promotion
description: Write or review Korean store promotion content using only facts approved from a user-supplied Obsidian vault. Use for store marketing drafts, evidence checks, and PASS/FAIL review.
---

# 근거 기반 가게 홍보

1. Fact Checker의 승인 사실과 vault 루트 기준 상대 경로를 확인한다.
2. 승인 사실만 사용하고 모든 게시 가능 내용 줄에 `[근거: notes/store.md]` 형식의 근거를 붙인다.
3. 메뉴, 가격, 할인, 영업시간, 주차, 후기, 고객 발언 또는 다른 사업 사실을 추측하지 않는다.
4. 근거가 없으면 줄을 `[확인 필요]`로 시작하고 홍보 주장으로 쓰지 않는다.
5. Quality Checker의 독립 대조와 PASS 뒤에만 완료한다.
'''

TEAM_SPEC = """# 홍보팀 조직 명세

## 지식창고

- 사용자가 실행 시 제공하는 Obsidian vault
- 표시명: `{vault_name}`
- 개인 로컬 전체 경로는 생성물에 저장하지 않는다.
- 증거는 vault 루트 기준 상대 경로를 `[근거: notes/store.md]` 형식으로 기록한다.

## 조직도와 순서

1. Main Commander가 작업과 vault를 확인한다.
2. Fact Checker가 사실과 상대 경로 근거를 확인한다.
3. Content Writer가 승인된 사실만으로 초안을 쓴다.
4. Quality Checker가 vault 원문과 독립 대조한다.
5. Main Commander가 PASS면 종료하고 FAIL이면 Content Writer에게 수정 지시를 전달한다.

읽기 전용이며 서로 독립적인 감사 작업만 병렬로 실행할 수 있다. 같은 파일을 쓰는 작업과 선행 산출물에 의존하는 작업은 직렬로 실행한다.
"""

PASS_FAIL = """# PASS/FAIL 계약

## PASS

- 제목과 `[확인 필요]` 줄을 제외한 초안의 모든 게시 가능 내용 줄에 vault 루트 기준 `[근거: notes/store.md]` 형식의 근거가 하나 이상 있다.
- 해당 파일이 vault 안에 실제로 존재한다.
- Fact Checker 승인 내용과 원문이 일치한다.
- 확인되지 않은 메뉴, 가격, 할인, 영업시간, 주차, 후기 또는 고객 발언이 없다.

## FAIL

- 근거 없는 사업 사실이 하나라도 있다.
- 근거 경로가 vault 밖을 가리키거나 파일이 없다.
- 퍼센트 할인 등 숫자 주장이 근거 없이 쓰였다.
- 작성 담당자가 같은 파일을 동시에 수정했거나 검수 전 순서를 건너뛰었다.

FAIL이면 홍보물을 배포하지 않고 문제 문장을 삭제하거나 근거에 맞게 수정한 뒤 다시 검수한다.
"""

WORKSPACE_README = """# 작업 공간

담당 직원의 순차 산출물을 보관한다.

1. `01_fact-check.md`: 승인 사실과 근거
2. `promotional-draft.md`: 홍보 초안
3. `03_quality-check.md`: PASS/FAIL 판정

같은 파일은 한 번에 한 담당 직원만 쓴다. 개인 정보나 비밀값을 저장하지 않는다.
"""

SAFE_DRAFT = """# 홍보 초안

[확인 필요] Fact Checker가 승인한 지식창고 근거를 기다립니다.
"""

GENERATED_VALIDATOR = r'''#!/usr/bin/env python3
"""Validate a generated classroom harness and every evidence annotation."""
from __future__ import annotations
import argparse
import re
import sys
import tomllib
from pathlib import Path

REQUIRED = (
    "AGENTS.md",
    ".codex/agents/fact-checker.toml",
    ".codex/agents/content-writer.toml",
    ".codex/agents/quality-checker.toml",
    ".agents/skills/write-grounded-store-promotion/SKILL.md",
    "docs/harness/team-spec.md",
    "docs/harness/pass-fail-contract.md",
    "_workspace/README.md",
    "_workspace/promotional-draft.md",
    "scripts/validate_harness.py",
)
EXPECTED_SANDBOX = {
    "fact-checker": "read-only",
    "content-writer": "workspace-write",
    "quality-checker": "read-only",
}
CITATION = re.compile(r"\[근거: ([^\]\r\n]+\.md)\]")
AGENT_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

class KoreanArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(2, f"FAIL\n- 입력 오류: {message}\n")

def validate(target: Path, vault: Path) -> list[str]:
    errors: list[str] = []
    if not vault.is_dir():
        errors.append(f"vault 폴더가 없습니다: {vault}")
    for rel in REQUIRED:
        if not (target / rel).is_file():
            errors.append(f"필수 파일 없음: {rel}")
    for expected_name, expected_sandbox in EXPECTED_SANDBOX.items():
        path = target / ".codex/agents" / f"{expected_name}.toml"
        if not path.is_file():
            continue
        try:
            agent = tomllib.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"agent TOML 오류: {path.name}: {exc}")
            continue
        for field in ("name", "description", "developer_instructions", "sandbox_mode"):
            if not isinstance(agent.get(field), str) or not agent[field].strip():
                errors.append(f"missing agent field: {path.name}: {field}")
        name = agent.get("name", "")
        if isinstance(name, str) and (not AGENT_NAME.fullmatch(name) or name != expected_name):
            errors.append(f"invalid agent name: {path.name}: {name!r}")
        sandbox = agent.get("sandbox_mode")
        if isinstance(sandbox, str) and sandbox != expected_sandbox:
            errors.append(
                f"wrong sandbox_mode: {path.name}: {sandbox!r} (expected {expected_sandbox!r})"
            )
    draft = target / "_workspace/promotional-draft.md"
    if not draft.is_file() or not vault.is_dir():
        return errors
    vault_root = vault.resolve()
    for number, line in enumerate(draft.read_text(encoding="utf-8-sig").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("[확인 필요]") or line.startswith("> [확인 필요]"):
            continue
        citations = CITATION.findall(line)
        if not citations or line.count("[근거:") != len(citations):
            errors.append(
                f"unsupported business claim: 홍보 초안 {number}행에 "
                f"[근거: notes/store.md] 형식이 필요합니다: {stripped}"
            )
            continue
        for citation in citations:
            rel = Path(citation)
            evidence = (vault_root / rel).resolve()
            if rel.is_absolute() or ".." in rel.parts or not evidence.is_relative_to(vault_root):
                errors.append(f"unsafe evidence path: 홍보 초안 {number}행: {citation}")
            elif not evidence.is_file():
                errors.append(f"missing evidence: 홍보 초안 {number}행: {citation}")
    return errors

def main() -> int:
    parser = KoreanArgumentParser()
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--vault", required=True, type=Path)
    args = parser.parse_args()
    errors = validate(args.target.resolve(), args.vault.resolve())
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''


def files(vault_name: str) -> dict[str, str]:
    return {
        "AGENTS.md": AGENTS,
        ".codex/agents/fact-checker.toml": FACT_CHECKER,
        ".codex/agents/content-writer.toml": CONTENT_WRITER,
        ".codex/agents/quality-checker.toml": QUALITY_CHECKER,
        ".agents/skills/write-grounded-store-promotion/SKILL.md": MARKETING_SKILL,
        "docs/harness/team-spec.md": TEAM_SPEC.format(vault_name=vault_name),
        "docs/harness/pass-fail-contract.md": PASS_FAIL,
        "_workspace/README.md": WORKSPACE_README,
        "_workspace/promotional-draft.md": SAFE_DRAFT,
        "scripts/validate_harness.py": GENERATED_VALIDATOR,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="가게 홍보팀 Codex 하네스를 생성합니다.")
    parser.add_argument("--target", required=True, type=Path, help="생성할 프로젝트 폴더")
    parser.add_argument("--vault", required=True, type=Path, help="Obsidian vault 폴더")
    parser.add_argument("--dry-run", action="store_true", help="파일을 쓰지 않고 계획만 표시")
    parser.add_argument("--force", action="store_true", help="기존 필수 파일을 명시적으로 덮어쓰기")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    target = args.target.expanduser().resolve()
    vault = args.vault.expanduser().resolve()
    if target == Path(target.anchor):
        print(f"ERROR: 파일시스템 루트에는 생성할 수 없습니다: {args.target}", file=sys.stderr)
        return 2
    if not vault.is_dir():
        print(f"ERROR: vault 폴더가 없습니다: {args.vault}", file=sys.stderr)
        return 2
    if target == vault or target.is_relative_to(vault) or vault.is_relative_to(target):
        print("ERROR: target과 vault는 서로 같거나 내부에 포함될 수 없습니다.", file=sys.stderr)
        return 2
    planned = files(vault.name)
    collisions = [rel for rel in planned if (target / rel).exists()]
    print("DRY-RUN" if args.dry_run else "SCAFFOLD")
    for rel in planned:
        marker = " (exists)" if rel in collisions else ""
        print(f"- {rel}{marker}")
    if args.dry_run:
        return 0
    if collisions and not args.force:
        print("ERROR: 기존 파일을 덮어쓰지 않았습니다. 교체하려면 --force를 명시하세요.", file=sys.stderr)
        return 2
    for rel, content in planned.items():
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8", newline="\n")
    print(f"PASS: {len(planned)} files created")
    return 0


if __name__ == "__main__":
    sys.exit(main())
