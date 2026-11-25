@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_boundary_evidence_reconcile
exit /b %errorlevel%
