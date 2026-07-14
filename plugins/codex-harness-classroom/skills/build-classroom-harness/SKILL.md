---
name: build-classroom-harness
description: Create or validate a Korean-first three-agent Codex marketing harness from a user-supplied Obsidian vault. Use when a learner asks “내 가게 홍보팀 하네스를 구성해줘”, requests a classroom harness, or needs a no-code Fact Checker → Content Writer → Quality Checker workflow grounded in local business notes.
---

# Build a classroom harness

1. Explain: Agent=담당 직원, Skill=업무 매뉴얼, Harness=조직도+업무 순서+검수 규칙, Obsidian=회사 지식창고.
2. Ask for the target folder and Obsidian vault folder. Never guess either path.
3. Read [safety-contract.md](references/safety-contract.md).
   Use exactly `[근거: notes/store.md]`; the path is relative to the root of the user-supplied Obsidian vault.
4. On Windows PowerShell, read Korean text explicitly as UTF-8. If text is garbled, stop and re-read it as UTF-8; never infer facts from corrupted output.
5. Resolve the absolute directory containing this `SKILL.md` as `<SKILL_DIR>`. Do not resolve the bundled script relative to the learner project or current working directory.
6. Preview without writing:

   `python "<SKILL_DIR>/scripts/scaffold_harness.py" --target "<target>" --vault "<vault>" --dry-run`

7. Show the planned files. If the target contains any of them, keep the default no-overwrite behavior. Use `--force` only after the learner explicitly asks to replace them.
8. Generate by removing `--dry-run`, then run the generated `<target>/scripts/validate_harness.py --target "<target>" --vault "<vault>"`.
9. Tell the learner to open `<target>` in a new Codex session before invoking the generated team. Project-scoped custom agents are loaded for the session.
10. Follow the copyable lesson in [classroom-flow.md](references/classroom-flow.md) when teaching the FAIL→PASS exercise. Ask Codex to perform lesson edits; never ask the learner to edit a file manually.

Use [team-spec.template.md](templates/team-spec.template.md) only to explain the output contract. Execute the bundled Python script for deterministic generation; do not ask learners to edit TOML.
