@echo off
setlocal
python -m unittest discover -s tests -v || exit /b 1
python scripts\validate_repo.py || exit /b 1
echo PASS
