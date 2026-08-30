@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set PY=.venv\Scripts\python.exe
) else (
    set PY=py
)

echo QEDCalc three-loop stages 1-3 validation
%PY% -m pytest -q tests\test_three_loop_stage1_3.py tests\test_three_loop_onshell.py tests\test_three_loop_integral_family.py tests\test_three_loop_integral_mapping.py tests\test_three_loop_laporta_plan.py tests\test_three_loop_ibp_frontier.py tests\test_three_loop_seed_pruning.py tests\test_three_loop_dependency_audit.py tests\test_three_loop_reverse_dependency.py tests\test_three_loop_pivot_blockers.py tests\test_three_loop_blocker_reduction.py tests\test_three_loop_local_block_elimination.py tests\test_three_loop_sector_block_profile.py tests\test_three_loop_sector_local_laporta.py tests\test_three_loop_sector_local_probe.py tests\test_three_loop_sector_local_modp.py tests\test_three_loop_sector_local_target_rescue.py
if errorlevel 1 (
    echo Three-loop stages 1-3 validation FAIL
    exit /b 1
)

echo Three-loop stages 1-3 validation PASS
exit /b 0
