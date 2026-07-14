# codex-harness-classroom

Korean-first, Windows-friendly Codex plugin that scaffolds a grounded three-agent classroom marketing harness from a user-supplied Obsidian vault. No learner-authored code or TOML is required.

Start with [README_KO.md](README_KO.md). The repository uses only the Python standard library and has no server, API key, telemetry, deployment, or external package requirement.

Verify with:

```shell
python -m unittest discover -s tests -v
python scripts/validate_repo.py
```

Licensed under Apache-2.0. Adapted conceptually from revfactory/harness; no endorsement is implied. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
