import subprocess, sys
from qedcalc.operations.corner import corner_phase63_pure_matching_audit
import qedcalc
print("QEDCalc v0.74 validation")
a=corner_phase63_pure_matching_audit()
for k,v in a.items(): print(f"{k}: {v}")
assert a["analytic_matching_constant"] == 0
assert a["last_within_uncertainty"]
print("Phase-63: PASS")
rc=subprocess.call([sys.executable,"-m","pytest","-q","tests/test_corner.py"])
if rc: raise SystemExit(rc)
print("version:",qedcalc.__version__)
assert qedcalc.__version__ == "0.74.0"
print("v0.74 validation PASS")
