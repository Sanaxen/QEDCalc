@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_physical_alias_evidence_gate
exit /b %ERRORLEVEL%
