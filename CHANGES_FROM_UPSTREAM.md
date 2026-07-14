# Changes from upstream

This repository is a substantial, classroom-focused adaptation of the team-architecture ideas in `revfactory/harness`.

- Replaced the original runtime-specific team mechanisms with Codex-native `AGENTS.md`, plugin skills, `.codex/agents/*.toml`, marketplace metadata, and subagent roles.
- Reduced the default architecture to a deterministic Korean classroom pipeline: commander, fact checker, content writer, and quality checker.
- Added a Windows-safe Python standard-library scaffolder with dry-run, no-overwrite, and explicit force behavior.
- Added an Obsidian-first evidence contract and a deterministic unsupported-claim validator.
- Added a copyable Korean lesson that demonstrates an unsupported 20% discount failing and a corrected draft passing.
- Added repository and generated-artifact tests, private-path and secret scans, and cross-platform verification entrypoints.

Historical descriptions of the original project may name its former runtime concepts. They are not instructions for this repository. No endorsement by revfactory or other referenced authors is implied.
