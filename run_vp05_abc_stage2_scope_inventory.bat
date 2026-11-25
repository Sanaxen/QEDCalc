@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_vp05_abc_stage2_scope_inventory
exit /b %errorlevel%
