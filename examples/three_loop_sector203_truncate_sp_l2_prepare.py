"""Prepare isolated Kira sector203 r6s6d1 truncate_sp l=2 comparison (NO Kira run)."""
import argparse,json
from pathlib import Path
from examples.three_loop_sector203_provisional64_stage_prepare import main as stage_main
from examples.three_loop_sector203_weight_audit import ROOT

def main():
    # Reuse the validated fresh-project generator, then modify only NEW project.
    import sys
    from datetime import datetime
    import re
    run_id="truncate_sp_l2_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    prior=sys.argv
    try:
        sys.argv=[prior[0],"r6s6d1","--run-id",run_id]
        stage_main()
    finally:
        sys.argv=prior
    project=ROOT/"output"/("kira_vp05_full_provisional64_sec203_r6s6d1_"+run_id)
    job=project/"jobs.yaml"
    src=job.read_text(encoding="utf-8")
    anchor="      select_integrals:\n"
    if src.count(anchor)!=1 or "truncate_sp" in src:raise RuntimeError("Unexpected job structure")
    corrected=src.replace(anchor,"      truncate_sp:\n        - {topologies: [VP05_full], l: 2}\n"+anchor)
    job.write_text(corrected,encoding="utf-8",newline="\n")
    check=job.read_text(encoding="utf-8")
    if check.count("truncate_sp:")!=1 or "l: 2" not in check:
        raise RuntimeError("Failed to verify truncate_sp inserted in new project")
    manifest=project/"provisional64_sector203_preflight.json"
    payload=json.loads(manifest.read_text(encoding="utf-8"))
    payload.update({"truncate_sp_l":2,"status":"PREPARED_TRUNCATE_SP_L2_NOT_EXECUTED",
      "execution":"DO NOT run Kira before schema and scope validation",
      "jobs":str(job)})
    manifest.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("TRUNCATE_SP_L2_PREFLIGHT="+json.dumps(payload,ensure_ascii=False))
if __name__=="__main__":main()
