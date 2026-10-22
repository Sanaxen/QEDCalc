@echo off
setlocal
cd /d "%~dp0"
python -m examples.three_loop_sector203_full_system_three_id_rank_gap --point 1
exit /b %ERRORLEVEL%
