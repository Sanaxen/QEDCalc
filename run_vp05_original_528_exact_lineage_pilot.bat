@echo off
setlocal
cd /d "%~dp0"
echo [VP05] Exact lineage replay: five compressed groups against original 528 equations.
python -m examples.three_loop_sector203_original_528_exact_lineage_audit --max-groups 5 --max-source-terms 20000
exit /b %ERRORLEVEL%
