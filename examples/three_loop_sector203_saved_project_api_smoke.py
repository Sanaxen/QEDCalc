"""Real saved-project VP05 API smoke: actual masters and certificate, no Kira.

The input amplitude is a *synthetic unit coefficient*, not a computed VP05
projected trace. Uses the real saved masters file and verified reduction JSON.
No FORM reduction export is available in the initiate-only L2 project, so this
test uses an intentionally empty temporary FORM file and does not claim that
the complete VP05 amplitude has been reduced.
"""
from __future__ import annotations
import argparse,json,tempfile
from pathlib import Path
from types import SimpleNamespace
import sympy as sp
from examples.three_loop_sector203_l2_witness_subset import DEFAULT as PROJECT
from examples.three_loop_sector203_weight_audit import parse_file_integrals
from three_loop.master_coefficient_api import MasterCoefficientConfig,synthesize_master_coefficients
from three_loop.vp05_verified_reduction import DEFAULT_ARTIFACT,TARGET,MASTER_6,MASTER_5

class SympyExactBackend:
    def self_test(self):pass
    def canonical_sum(self,parts,progress=None):
        result=sp.cancel(sp.Add(*parts))
        return str(result),tuple(sorted(str(k) for k in result.free_symbols))

def bridge(_):
    return SimpleNamespace(terms=(SimpleNamespace(kira_indices=TARGET,coefficient=sp.Integer(1)),))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,default=PROJECT)
    p.add_argument("--artifact",type=Path,default=DEFAULT_ARTIFACT)
    a=p.parse_args()
    mastersfile=a.project/"results/VP05_full/masters"
    if not mastersfile.is_file():p.error("Saved original masters file missing")
    masters=parse_file_integrals(mastersfile)
    if len(masters)!=5 or MASTER_6 not in masters or MASTER_5 not in masters:
        p.error("Unexpected original saved master set")
    with tempfile.TemporaryDirectory(prefix="vp05_saved_project_api_smoke_") as folder:
        # There is no Kira FORM output for initiate-only run; no fake rules.
        form=Path(folder)/"empty.frm"
        form.write_text("",encoding="utf-8")
        config=MasterCoefficientConfig(
            family="VP05_full",form_export=form,masters_file=mastersfile,
            final_basis=frozenset(masters),
            expected_kira_targets=frozenset({TARGET}),
            expected_native_terms=1,
            verified_vp05_artifact=a.artifact,
        )
        result=synthesize_master_coefficients(
            [(TARGET,sp.Integer(1))],bridge,config,
            backend=SympyExactBackend(),progress=None)
    got={row.indices:sp.sympify(row.coefficient) for row in result.rows}
    z=sp.Symbol("z")
    checks={"api_passed":result.passed,
        "no_unresolved_integrals":not result.unresolved_integrals,
        "master_six_exact":sp.cancel(got.get(MASTER_6,0)-2/z)==0,
        "master_five_exact":sp.cancel(got.get(MASTER_5,0)+2/z)==0,
        "other_three_zero":all(sp.cancel(got.get(m,0))==0 for m in masters if m not in (MASTER_6,MASTER_5)),
        "five_saved_masters":result.reduction_masters==5,
        "one_target_bridge":result.bridge_unique_targets==1}
    report={"status":"PASS_SAVED_ARTIFACT_REAL_MASTER_API_SMOKE" if all(checks.values()) else "FAIL_SAVED_ARTIFACT_REAL_MASTER_API_SMOKE",
        "checks":checks,"project":str(a.project),"artifact":str(a.artifact),
        "actual_saved_masters_used":True,"actual_verified_certificate_used":True,
        "projected_amplitude":"SYNTHETIC_UNIT_TARGET_ONLY",
        "form_reduction":"EMPTY_NO_FORM_EXPORT_IN_INITIATE_ONLY_PROJECT",
        "backend":"SYMPY_EXACT_NO_FERMAT",
        "complete_vp05_amplitude_verified":False,
        "kira_executed":False,"saved_source_modified":False}
    print("VP05_SAVED_PROJECT_API_SMOKE "+json.dumps(report,ensure_ascii=False),flush=True)
    if not all(checks.values()):raise SystemExit(2)
if __name__=="__main__":main()
