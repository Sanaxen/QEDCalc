"""Read-only graph closure of physical VP05 sector202 targets in saved L2 IBP rows.

Structural incidence is not a rank, coefficient, or reducibility proof.
Avoids parsing huge symbolic coefficients and never changes source projects.
"""
from __future__ import annotations
import gzip,json,hashlib
from collections import defaultdict,deque,Counter
from examples.three_loop_sector203_weight_audit import ROOT,load_codec
from examples.three_loop_vp05_sector202_target_id_bridge import TARGETS
PROJECT=ROOT/"output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734"
def main():
 m=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
 bits,ordering=m.from_kiradb(str(PROJECT/"results/kira.db"))
 if ordering!=5:raise RuntimeError("Unexpected project codec ordering")
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 targets=[(codec.encode(t),139) for t in TARGETS]
 for t,(w,s) in zip(TARGETS,targets):
  if tuple(codec.decode(w))!=t:raise RuntimeError("Codec roundtrip invalid")
 rows=[];index=defaultdict(list);file_hashes={}
 for f in sorted((PROJECT/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz")):
  file_hashes[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
  with gzip.open(f,"rt",encoding="utf-8") as h:
   counter=0
   while marker:=h.readline():
    if marker.strip()!="Eq":raise RuntimeError("Malformed equation marker")
    head=int(h.readline().strip());count=int(h.readline().strip());counter+=1
    cols=set()
    for _ in range(count):
     v=h.readline().split()
     if len(v)<4:raise RuntimeError("Malformed term")
     cols.add((int(v[2]),int(v[3])))
    idx=len(rows)
    rows.append({"file":f.name,"ordinal":counter,"head":head,"columns":cols})
    for col in cols:index[col].append(idx)
 sizes={};target_components={};components=[]
 unvisited=set(range(len(rows)))
 while unvisited:
  start=min(unvisited);q=deque([start]);unvisited.remove(start)
  comp=[];columns=set()
  while q:
   i=q.popleft();comp.append(i)
   for col in rows[i]["columns"]:
    if col in columns:continue
    columns.add(col)
    for j in index[col]:
     if j in unvisited:unvisited.remove(j);q.append(j)
  cid=len(components)
  present=[k for k,t in enumerate(targets) if t in columns]
  components.append({"component_id":cid,"rows":len(comp),"unique_columns":len(columns),
    "target_indices":present,"source_sector_files":dict(Counter(rows[i]["file"] for i in comp)),
    "sample_rows":[{"file":rows[i]["file"],"ordinal":rows[i]["ordinal"]} for i in sorted(comp)[:12]]})
  for k in present:target_components[k]=cid
 cids=sorted(set(target_components.values()))
 report={"status":"VP05_SECTOR202_TARGET_INCIDENCE_CLOSURE",
  "project":str(PROJECT),"equations":len(rows),"unique_columns":len(index),
  "target_weights":[{"exponents":list(v),"weight":w,"recorded_sector":s,
     "found":(w,s) in index,"direct_equations":len(index.get((w,s),[])),
     "component_id":target_components.get(k)} for k,(v,(w,s)) in enumerate(zip(TARGETS,targets))],
  "connected_components":len(components),"target_bearing_components":[components[c] for c in cids],
  "all_three_in_one_component":len(target_components)==3 and len(cids)==1,
  "saved_system_sha256":file_hashes,
  "scope":"structural graph only; an incidence connection does not prove a reduction or determine coefficients",
  "kira_executed":False,"files_modified":False}
 print("VP05_SECTOR202_TARGET_INCIDENCE "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
