#!/usr/bin/env sh
set -eu
python3 -m unittest discover -s tests -v
python3 scripts/validate_repo.py
echo PASS
