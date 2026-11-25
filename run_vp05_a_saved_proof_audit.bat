@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_a_saved_proof_audit
exit /b %errorlevel%
