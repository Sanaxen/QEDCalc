@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_restricted_reuse_preflight
exit /b %ERRORLEVEL%
