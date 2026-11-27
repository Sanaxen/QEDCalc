@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_parent_substitution %*
exit /b %errorlevel%
