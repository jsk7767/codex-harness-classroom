from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAFFOLDER = ROOT / "plugins/codex-harness-classroom/skills/build-classroom-harness/scripts/scaffold_harness.py"


class RepositoryTests(unittest.TestCase):
    def run_scaffold(self, target: Path, vault: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCAFFOLDER), "--target", str(target), "--vault", str(vault), *extra],
            text=True,
            capture_output=True,
            encoding="utf-8",
            check=False,
        )

    def test_manifests(self) -> None:
        market = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(market["name"], "codex-harness-classroom")
        plugin = market["plugins"][0]
        self.assertEqual(plugin["source"], {"source": "local", "path": "./plugins/codex-harness-classroom"})
        self.assertEqual(plugin["policy"], {"installation": "AVAILABLE", "authentication": "ON_INSTALL"})
        manifest = json.loads((ROOT / "plugins/codex-harness-classroom/.codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "codex-harness-classroom")
        self.assertEqual(manifest["version"], "1.0.1")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["author"]["name"], "Jeon Seung-gi")
        public_repo = "https://github.com/jsk7767/codex-harness-classroom"
        self.assertEqual(manifest["homepage"], public_repo)
        self.assertEqual(manifest["repository"], public_repo)

    def test_required_repository_paths(self) -> None:
        required = [
            "AGENTS.md", "README_KO.md", "LICENSE", "NOTICE", "CHANGES_FROM_UPSTREAM.md",
            "THIRD_PARTY_NOTICES.md", "docs/research-sources.md", "scripts/validate_repo.py",
            "verify.bat", "verify.sh", ".gitignore", ".gitattributes",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            vault = base / "my-llm-wiki"
            vault.mkdir()
            target = base / "lesson"
            result = self.run_scaffold(target, vault, "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DRY-RUN", result.stdout)
            self.assertFalse(target.exists())

    def test_no_overwrite_and_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            vault = base / "vault"
            target = base / "lesson"
            vault.mkdir()
            target.mkdir()
            sentinel = target / "AGENTS.md"
            sentinel.write_text("mine", encoding="utf-8")
            result = self.run_scaffold(target, vault)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "mine")
            forced = self.run_scaffold(target, vault, "--force")
            self.assertEqual(forced.returncode, 0, forced.stderr)
            self.assertNotEqual(sentinel.read_text(encoding="utf-8"), "mine")

    def test_generated_validity_and_validator_pass_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            vault = base / "my-llm-wiki"
            target = base / "lesson"
            vault.mkdir()
            result = self.run_scaffold(target, vault)
            self.assertEqual(result.returncode, 0, result.stderr)
            required = [
                "AGENTS.md", ".codex/agents/fact-checker.toml", ".codex/agents/content-writer.toml",
                ".codex/agents/quality-checker.toml", "docs/harness/team-spec.md",
                ".agents/skills/write-grounded-store-promotion/SKILL.md",
                "docs/harness/pass-fail-contract.md", "_workspace/README.md", "scripts/validate_harness.py",
            ]
            for rel in required:
                self.assertTrue((target / rel).is_file(), rel)
            for path in (target / ".codex/agents").glob("*.toml"):
                parsed = tomllib.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(parsed["name"], path.stem)
                self.assertIn("description", parsed)
                self.assertIn("developer_instructions", parsed)
                self.assertIn("sandbox_mode", parsed)
                self.assertIn("UTF-8", parsed["developer_instructions"])
            self.assertIn("UTF-8", (target / "AGENTS.md").read_text(encoding="utf-8"))
            validator = target / "scripts/validate_harness.py"
            command = [sys.executable, str(validator), "--target", str(target), "--vault", str(vault)]
            passed = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)

            no_vault = subprocess.run(
                [sys.executable, str(validator), "--target", str(target)],
                text=True, capture_output=True, encoding="utf-8", check=False,
            )
            self.assertNotEqual(no_vault.returncode, 0)
            self.assertIn("FAIL", no_vault.stderr)

            agent_path = target / ".codex/agents/fact-checker.toml"
            agent_text = agent_path.read_text(encoding="utf-8")
            agent_path.write_text(agent_text.replace('name = "fact-checker"\n', ""), encoding="utf-8")
            missing_name = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
            self.assertEqual(missing_name.returncode, 1)
            self.assertIn("missing agent field: fact-checker.toml: name", missing_name.stdout)
            agent_path.write_text(agent_text, encoding="utf-8")

            agent_path.write_text(agent_text.replace('sandbox_mode = "read-only"\n', ""), encoding="utf-8")
            missing_sandbox = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
            self.assertEqual(missing_sandbox.returncode, 1)
            self.assertIn("missing agent field: fact-checker.toml: sandbox_mode", missing_sandbox.stdout)
            agent_path.write_text(agent_text.replace('sandbox_mode = "read-only"', 'sandbox_mode = "workspace-write"'), encoding="utf-8")
            wrong_sandbox = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
            self.assertEqual(wrong_sandbox.returncode, 1)
            self.assertIn("wrong sandbox_mode", wrong_sandbox.stdout)
            agent_path.write_text(agent_text, encoding="utf-8")

            draft = target / "_workspace/promotional-draft.md"
            draft.write_text("# 홍보 초안\n\n오늘 배달 무료!\n", encoding="utf-8")
            delivery = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
            self.assertEqual(delivery.returncode, 1)
            self.assertIn("unsupported business claim", delivery.stdout)

            draft.write_text("# 홍보 초안\n\n전 메뉴 20% 할인!\n", encoding="utf-8")
            discount = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
            self.assertEqual(discount.returncode, 1)
            self.assertIn("unsupported business claim", discount.stdout)

            evidence = vault / "notes/store.md"
            evidence.parent.mkdir()
            evidence.write_text("오늘 배달 무료", encoding="utf-8")
            draft.write_text("# 홍보 초안\n\n오늘 배달 무료! [근거: notes/store.md]\n", encoding="utf-8")
            grounded = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
            self.assertEqual(grounded.returncode, 0, grounded.stdout + grounded.stderr)
            self.assertIn("PASS", grounded.stdout)

            draft.write_text(
                "# 홍보 초안\n\n오늘 배달 무료! [근거: notes/store.md] [근거: notes/missing.md]\n",
                encoding="utf-8",
            )
            every_citation = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", check=False)
            self.assertEqual(every_citation.returncode, 1)
            self.assertIn("missing evidence", every_citation.stdout)

    def test_scaffolder_rejects_target_vault_overlap_and_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            vault = base / "vault"
            vault.mkdir()
            cases = (
                (vault, vault),
                (vault / "lesson", vault),
            )
            for target, source in cases:
                result = self.run_scaffold(target, source, "--dry-run")
                self.assertEqual(result.returncode, 2)
                self.assertIn("서로 같거나 내부", result.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            vault = target / "vault"
            vault.mkdir()
            result = self.run_scaffold(target, vault, "--dry-run")
            self.assertEqual(result.returncode, 2)
            self.assertIn("서로 같거나 내부", result.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            vault.mkdir()
            root = Path(vault.anchor)
            result = self.run_scaffold(root, vault, "--dry-run")
            self.assertEqual(result.returncode, 2)
            self.assertIn("파일시스템 루트", result.stderr)

    def test_runtime_residue_and_hygiene_validator(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_repo.py")],
            text=True, capture_output=True, encoding="utf-8", check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_skill_resolves_bundled_scaffolder_absolutely(self) -> None:
        skill = (ROOT / "plugins/codex-harness-classroom/skills/build-classroom-harness/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("absolute directory containing this `SKILL.md`", skill)
        self.assertIn('python "<SKILL_DIR>/scripts/scaffold_harness.py"', skill)
        self.assertNotIn("python scripts/scaffold_harness.py", skill)

    def test_evidence_and_validator_contract_is_static(self) -> None:
        skill_root = ROOT / "plugins/codex-harness-classroom/skills/build-classroom-harness"
        runtime_paths = (
            ROOT / "AGENTS.md",
            ROOT / "README_KO.md",
            skill_root / "SKILL.md",
            skill_root / "references/safety-contract.md",
            skill_root / "references/classroom-flow.md",
            skill_root / "templates/team-spec.template.md",
            skill_root / "scripts/scaffold_harness.py",
        )
        combined = "\n".join(path.read_text(encoding="utf-8") for path in runtime_paths)
        self.assertIn("[근거: notes/store.md]", combined)
        self.assertIn("UTF-8", combined)
        for drift in ("[근거: vault/기준/상대경로.md]", "[근거: vault의/상대경로.md]", "[근거: 상대경로.md]"):
            self.assertNotIn(drift, combined)
        scaffolder = (skill_root / "scripts/scaffold_harness.py").read_text(encoding="utf-8")
        self.assertIn('parser.add_argument("--vault", required=True', scaffolder)
        self.assertIn("EXPECTED_SANDBOX", scaffolder)
        self.assertIn('"fact-checker": "read-only"', scaffolder)
        self.assertIn('"content-writer": "workspace-write"', scaffolder)
        self.assertNotIn("CLAIM_WORDS", scaffolder)

    def test_copyable_classroom_contract(self) -> None:
        readme = (ROOT / "README_KO.md").read_text(encoding="utf-8")
        self.assertIn("codex plugin marketplace add jsk7767/codex-harness-classroom --ref main --json", readme)
        self.assertIn("codex plugin add codex-harness-classroom@codex-harness-classroom --json", readme)
        self.assertIn("새 Codex 세션", readme)
        self.assertIn('근거 표기 없이 "전 메뉴 20% 할인!"을 추가', readme)
        self.assertIn('방금 추가한 근거 없는 "전 메뉴 20% 할인!" 문장만 삭제', readme)
        self.assertNotIn("현재 Codex가 안내하는", readme)

    def test_notice_and_research_links(self) -> None:
        notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
        for phrase in ("Copyright 2026 Jeon Seung-gi", "Copyright 2025 robin", "Apache License"):
            self.assertIn(phrase, notice)
        sources = (ROOT / "docs/research-sources.md").read_text(encoding="utf-8")
        required_links = (
            "https://github.com/ganimjeong/Harness-for-codex",
            "https://developers.openai.com/codex/guides/agents-md",
            "https://developers.openai.com/codex/skills",
            "https://developers.openai.com/codex/subagents",
            "https://developers.openai.com/codex/plugins/build",
            "https://github.com/walkinglabs/learn-harness-engineering",
            "https://github.com/agentsmd/agents.md",
            "https://github.com/revfactory/harness-100",
            "https://github.com/DenisSergeevitch/agents-best-practices",
            "https://github.com/AgentWrapper/agent-orchestrator",
            "https://github.com/openai/codex",
        )
        for link in required_links:
            self.assertIn(link, sources)


if __name__ == "__main__":
    unittest.main()
