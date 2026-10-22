"""Read-only saved-project diagnostic for the two uncompleted VP05 closure seeds.

No Kira launch, no checkpoint or promotion writes. Never infer a completed
master basis from logs, intermediate database, or a sector-local certificate.
"""
from __future__ import annotations
import json
from pathlib import Path
from three_loop.master_basis_batch import AUDIT_DIR
from three_loop.integral_family_classification import ROOT

SEEDS=("r8s6d2","r8s5d3")
PREFIX="kira_vp05_full_masters_candidate_closure_r8s3d0_"
FILE_NAMES=("jobs.yaml","integralfamilies.yaml","kinematics.yaml",
            "mandatory_candidate_closure_targets.txt")
LOG_HINTS=("error","failed","killed","memory","swap","oom","terminate",
           "stop","abort","signal","exception","time limit","no space")
def file_info(path):
    return {"exists":path.is_file(),"bytes":path.stat().st_size if path.is_file() else None}
def tail_log(path,limit=18):
    if not path.is_file() or path.stat().st_size>20*1024*1024:return []
    try:
        lines=path.read_text(encoding="utf-8",errors="replace").splitlines()
        hits=[line.strip()[:240] for line in lines if any(x in line.lower() for x in LOG_HINTS)]
        return {"last_lines":[line.strip()[:240] for line in lines[-8:]],
                "issue_lines":hits[-limit:],"line_count":len(lines)}
    except OSError:return {}
def inspect(seed):
    project=ROOT/"output"/(PREFIX+seed)
    results=project/"results"/"VP05_full"
    data={"seed":seed,"project":str(project),"project_exists":project.is_dir(),
          "files":{name:file_info(project/name) for name in FILE_NAMES},
          "masters":file_info(results/"masters"),
          "masters_final":file_info(results/"masters.final")}
    for dirname in ("results","tmp","pyred","sectormappings","firefly_saves","ff_save"):
        target=project/dirname
        data[dirname+"_exists"]=target.is_dir()
    log_candidates=[]
    if project.is_dir():
        for parent in (project,project/"logs",project/"results"):
            if parent.is_dir():
                for path in parent.iterdir():
                    if path.is_file() and (path.suffix.lower() in (".log",".out",".err") or path.name.lower() in ("kira.log","run.log")):
                        log_candidates.append(path)
    data["log_files"]=[{"path":str(path),"size":path.stat().st_size,"summary":tail_log(path)} for path in log_candidates[:12]]
    data["log_files_truncated"]=len(log_candidates)>12
    return data
def main():
    rows=[inspect(s) for s in SEEDS]
    report={"status":"VP05_STAGE2_CLOSURE_PROJECT_INVENTORY",
            "projects":rows,"master_outputs_missing":[x["seed"] for x in rows if not (x["masters"]["exists"] or x["masters_final"]["exists"])],
            "safe_to_mark_closure_pass":False,
            "recommended_next_step":"Inspect missing seed project logs and resource guard records; choose minimal evidence-preserving rerun only after policy review.",
            "kira_executed":False,"files_modified":False}
    print("VP05_STAGE2_CLOSURE_PROJECT_INVENTORY "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
