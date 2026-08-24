@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if exist "qedcalc\run_qedcalc.bat" cd /d "%~dp0qedcalc"

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: .venv\Scripts\python.exe not found.
  echo Copy this BAT into the QEDCalc v0.50.0 root folder.
  pause
  exit /b 2
)

set "PYTHONPATH=%CD%"
if not exist "test_results" mkdir "test_results"
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do set D=%%a%%b%%c
for /f "tokens=1-4 delims=:. " %%a in ("%time%") do set T=%%a%%b%%c%%d
set "OUT=test_results\v050_tail_%D%_%T%"
mkdir "%OUT%" >nul 2>&1

set "PY=.venv\Scripts\python.exe"

echo [A] Isolated suspected test...
"%PY%" -m pytest -vv -s tests/test_v026_general_q_ladder.py::test_corrected_spin_sum_route_is_kept_separate_from_archived_75_table > "%OUT%\suspect_test.log" 2>&1
set "RC1=%ERRORLEVEL%"
type "%OUT%\suspect_test.log"
echo suspect_test_exit_code=%RC1%> "%OUT%\exit_codes.txt"

if not "%RC1%"=="0" goto :package

echo.
echo [B] Remaining suite after the suspected test, in a fresh Python process...
"%PY%" -m pytest -vv --durations=100 ^
 tests/test_v034_incremental_scheduler.py ^
 tests/test_v038_full_degree2.py ^
 tests/test_v040_degree3.py ^
 tests/test_v041_structured_reconstruction.py ^
 tests/test_v044_ladder_assembly.py ^
 tests/test_v046_crossed_qlinear.py ^
 tests/test_v047_crossed_px.py ^
 tests/test_v048_crossed_u_tq_bridge.py ^
 tests/test_v049_crossed_raw_q_kernel.py ^
 tests/test_v050_crossed_automatic_hermite.py ^
 tests/test_v07_operations.py ^
 tests/test_v08_operations.py ^
 tests/test_v09_operations.py ^
 tests/test_vacuum_polarization.py > "%OUT%\tail_suite.log" 2>&1
set "RC2=%ERRORLEVEL%"
type "%OUT%\tail_suite.log"
echo tail_suite_exit_code=%RC2%>> "%OUT%\exit_codes.txt"

:package
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%OUT%.zip' -Force" >nul 2>&1

echo.
echo Diagnostic complete.
echo Result: %OUT%.zip
if not "%RC1%"=="0" (
  echo Exit code: %RC1%
  exit /b %RC1%
)
if defined RC2 (
  echo Exit code: %RC2%
  exit /b %RC2%
)
exit /b 0
