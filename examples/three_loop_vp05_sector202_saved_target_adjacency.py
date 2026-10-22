"""Read-only target equation adjacency for saved VP05 physical sector 202.

Uses the existing external Kira weight codec and the L2 project's own DB.
Enumerates all original equations mentioning each target, including those
from other SYSTEM files. Never infers coefficient-level reducibility merely
from appearances or a connected equation graph.
"""
from __future__ import annotations
import gzip,hashlib,json,re
from collections import Counter
from pathlib import Path
from examples.three_loop_sector203_weight_audit import ROOT,load_codec
from examples.three_loop_vp05_sector202_target_id_bridge import TARGETS
PROJECT=ROOT/"output/kira_vp05_full_provisional64_sec203_r6s6d1_truncate_sp_l2_20261016_135543_689734"
def main():
 m=load_codec((ROOT/"output/tools/pyred_weight.py").resolve())
 db=PROJECT/"results/kira.db"
 bits,ordering=m.from_kiradb(str(db))
 if ordering!=5:raise RuntimeError("Unexpected L2 integral ordering")
 cfg=(PROJECT/"config/integralfamilies.yaml").read_text(encoding="utf-8")
 if not re.search(r"top_level_sectors:\s*\[\s*203\s*\]",cfg):raise RuntimeError("Unexpected L2 top-level sector")
 codec=m.WeightCodec(np=12,bits=bits,iord=ordering,topsectors=[203])
 weights={codec.encode(v):v for v in TARGETS}
 for w,v in weights.items():
  if tuple(codec.decode(w))!=v:raise RuntimeError("Codec roundtrip failure")
 files=sorted((PROJECT/"tmp/VP05_full").glob("SYSTEM_VP05_full_*.gz"))
 found=Counter();heads=Counter();rows=[];total_eq=0;total_terms=0;target_pairs=Counter()
 for file in files:
  digest=hashlib.sha256(file.read_bytes()).hexdigest()
  with gzip.open(file,"rt",encoding="utf-8") as fh:
   n_eq=0
   while line:=fh.readline():
    if line.strip()!="Eq":raise ValueError("Invalid SYSTEM marker: "+file.name)
    head=int(fh.readline().strip())
    n=int(fh.readline().strip());n_eq+=1;total_eq+=1;total_terms+=n
    terms=[]
    for _ in range(n):
     f=fh.readline().split()
     if len(f)<4:raise ValueError("Truncated SYSTEM equation: "+file.name)
     terms.append((int(f[2]),int(f[3])))
    present=sorted(set(w for w,s in terms if w in weights))
    if not present:continue
    for w in present:found[w]+=1
    for w,s in terms:
     if w in weights:target_pairs[(w,s)]+=1
    if head in weights:heads[head]+=1
    rows.append({"file":file.name,"equation_index":n_eq,"head":head,
       "term_count":n,"target_weights":present,
       "target_count":len(present),"distinct_terms":len(set(terms)),
       "other_term_count":sum(w not in weights for w,s in terms),
       "source_file_sha256":digest})
 rows.sort(key=lambda v:(-v["target_count"],v["term_count"],v["file"],v["equation_index"]))
 pairs=Counter()
 for row in rows:
  ws=row["target_weights"]
  for i in range(len(ws)):
   for j in range(i+1,len(ws)):pairs[(ws[i],ws[j])]+=1
 print("VP05_SECTOR202_SAVED_TARGET_ADJACENCY "+json.dumps({
  "status":"VP05_SECTOR202_SAVED_TARGET_ADJACENCY","project":str(PROJECT),
  "system_files":len(files),"equations":total_eq,"terms":total_terms,
  "target_equation_rows":len(rows),
  "targets":[{"exponents":list(v),"weight":w,"rows_containing":found[w],
    "term_occurrences":[{"sector":s,"count":c} for (weight,s),c in target_pairs.items() if weight==w],
    "equation_heads":heads[w]} for w,v in weights.items()],
  "pairwise_same_equation":[{"weights":list(k),"row_count":n} for k,n in pairs.items()],
  "rows_with_two_or_more_targets":sum(r["target_count"]>=2 for r in rows),
  "rows_with_three_targets":sum(r["target_count"]==3 for r in rows),
  "representative_rows":rows[:25],
  "sufficient_for_coefficient_proof":False,
  "note":"Graph/row co-occurrence only; no exact polynomial coefficient reconstruction or target-in-rowspace certificate.",
  "kira_executed":False,"files_modified":False},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
