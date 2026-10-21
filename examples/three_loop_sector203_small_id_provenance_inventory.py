"""Audit small SYSTEM IDs against declared Kira sectors and saved reduction files.

Read-only. Do not assign physical integrals to IDs by ordinal position.
"""
from __future__ import annotations
import argparse,json,re,hashlib
from pathlib import Path
from examples.three_loop_sector203_l2_witness_subset import DEFAULT

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,default=DEFAULT)
    p.add_argument("--output",type=Path,default=Path("output/three_loop_integral_family_audit/vp05_small_id_provenance_inventory.json"))
    a=p.parse_args();root=a.project.resolve()
    targets=[root/"config/integralfamilies.yaml",root/"config/kinematics.yaml",
             root/"results/VP05_full/masters",root/"results/VP05_full/master_integrals",
             root/"results/VP05_full/kira.log"]
    findings=[]
    for f in targets:
        if not f.is_file():continue
        lines=f.read_text(encoding="utf-8",errors="replace").splitlines()
        hits=[{"line":i,"text":s.strip()[:240]} for i,s in enumerate(lines,1)
              if re.search(r"master|sector|preferred|integral_order|redu|identify",s,re.I)]
        findings.append({"file":str(f.relative_to(root)),"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),
          "lines":len(lines),"matches":hits[:45]})
    result={"project":str(root),"files_found":len(findings),"files":findings,
      "small_id_to_physical_integral_mapping_verified":False,
      "warning":"Text metadata alone does not establish numeric SYSTEM ID mapping. Need explicit Kira convention or independently checked mapping."}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("VP05_SMALL_ID_PROVENANCE_INVENTORY "+json.dumps(result),flush=True)
if __name__=="__main__":main()
