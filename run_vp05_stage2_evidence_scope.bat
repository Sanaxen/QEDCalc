@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_stage2_evidence_scope
exit /b %ERRORLEVEL%
