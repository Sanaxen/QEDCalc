"""Read-only post-run inspection of the completed VP05 truncate_sp l2 initiate project.

This is an evidence audit, not a symbolic reduction. It never invokes Kira,
modifies previous results, or assumes that absent masters were reduced.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

DEFAULT=Path("output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734")
RE=re.compile(r"VP05_full\[[^\]\r\n]+\]")
FILES=("results/VP05_full/masters","results/preferredMasters","mandatory_provisional64_sector203.txt")
def read_integrals(path:Path):
    if not path.is_file():return None
    return RE.findall(path.read_text(encoding="utf-8",errors="replace"))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",type=Path,default=DEFAULT)
    a=p.parse_args()
    project=a.project.resolve()
    if not project.is_dir():p.error(f"project does not exist: {project}")
    raw={f:read_integrals(project/f) for f in FILES}
    selected,preferred,mandatory=(raw[f] for f in FILES)
    files=[]
    for rel in ("results/VP05_full/masters","results/preferredMasters",
                "results/kira.db","results/VP05_full/masters.final",
                "results/VP05_full/","tmp/VP05_full/"):
        path=project/rel
        if path.is_file():files.append({"path":rel,"type":"file","bytes":path.stat().st_size})
        elif path.is_dir():
            contents=[str(q.relative_to(project)) for q in path.rglob("*") if q.is_file()]
            files.append({"path":rel,"type":"directory","file_count":len(contents),
                "first_15_files":contents[:15]})
        else:files.append({"path":rel,"type":"absent"})
    classification=[]
    if selected is not None and mandatory is not None:
        for i,integral in enumerate(mandatory,1):
            classification.append({"target_number":i,"integral":integral,
                "in_reported_master_list":integral in selected,
                "status":"reported_master" if integral in selected else "not_listed_as_master__not_proof_of_reduction"})
    for name,arr in raw.items():
        if arr is not None and len(arr)!=len(set(arr)):p.error(f"duplicate integral entries in {name}")
    report={"project":str(project),"read_only":True,"files":files,
        "list_counts":{k:len(v) if v is not None else None for k,v in raw.items()},
        "selected_not_preferred":sorted(set(selected or [])-set(preferred or [])),
        "mandatory_targets":classification,
        "master_not_mandatory":sorted(set(selected or [])-set(mandatory or [])),
        "selected_masters":selected,
        "limitations":["A target absent from a selected-system master list is not, by itself, a symbolic reduction identity.",
          "initiate-only Kira run creates no proven full closure or globally complete master basis.",
          "No previous r5s6d0 basis can be declared equivalent to a truncated seed from counts alone."]}
    print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
