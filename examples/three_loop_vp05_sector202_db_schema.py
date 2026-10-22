"""Read-only Kira SQLite metadata inventory for VP05 sector 202.

No data modification; URI immutable mode prevents SQLite journal writes.
Inspect schema and aggregate counts only, not binary coefficient payloads.
"""
from __future__ import annotations
import json,sqlite3
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parent.parent
SUFFIXES=(
"kira_vp05_full_firefly_numerator_r8s3d0_r6s6d2_sec202",
"kira_vp05_full_preferred_masters_r8s3d0_r6s6d2_sec202",
"kira_vp05_full_masters_candidate_sector_closure_r8s3d0_r9s5d2_sec202",
)
def inspect(path):
 result={"path":str(path),"exists":path.is_file()}
 if not path.is_file():return result
 result["size_bytes"]=path.stat().st_size
 with path.open("rb") as handle:result["header_hex"]=handle.read(16).hex()
 if not result["header_hex"].startswith(b"SQLite format 3".hex()):
  result["sqlite"]=False
  return result
 result["sqlite"]=True
 uri="file:"+quote(str(path.resolve()).replace("\\","/"),safe="/:")+"?mode=ro&immutable=1"
 try:
  conn=sqlite3.connect(uri,uri=True,timeout=1)
  try:
   conn.execute("PRAGMA query_only=ON")
   conn.execute("PRAGMA busy_timeout=1000")
   tables=conn.execute("SELECT type,name,sql FROM sqlite_master WHERE type IN ('table','view') ORDER BY name").fetchall()
   schema=[]
   for typ,name,sql in tables:
    fields=[{"name":v[1],"type":v[2],"pk":bool(v[5])} for v in conn.execute('PRAGMA table_info("'+name.replace('"','""')+'")')]
    count=None
    if typ=="table":
     try:count=conn.execute('SELECT COUNT(*) FROM "'+name.replace('"','""')+'"').fetchone()[0]
     except sqlite3.DatabaseError:pass
    schema.append({"type":typ,"name":name,"columns":fields,"row_count":count,
     "create_sql":sql[:2500] if sql else None})
   result["tables"]=schema
   result["integrity_check"]="skipped; read-only schema inventory"
  finally:conn.close()
 except sqlite3.Error as exc:result["sqlite_error"]=str(exc)
 return result
def main():
 rows=[inspect(ROOT/"output"/s/"results"/"kira.db") for s in SUFFIXES]
 print("VP05_SECTOR202_SQLITE_SCHEMA "+json.dumps({
  "status":"VP05_SECTOR202_KIRA_DB_READONLY_SCHEMA","rows":rows,
  "binary_payloads_decoded":False,"has_proven_explicit_reduction_coefficients":False,
  "no_kira_run":True,"no_database_writes":True},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
