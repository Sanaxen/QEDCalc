"""Read-only audit of the isolated VP05 full-stage capsule. Never run Kira."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from examples.three_loop_sector203_kira_full_stage_specific_validation import ROOT, AUDIT
from examples.three_loop_sector203_single_nonmaster_prepare import TARGET
from examples.three_loop_sector203_weight_audit import parse_file_integrals

FILES = ("config/integralfamilies.yaml", "config/kinematics.yaml",
         "mandatory_single_nonmaster.txt", "preferred_provisional64_sector203.txt",
         "jobs.yaml")
HEADER = "# REVIEW-ONLY: DO NOT RUN KIRA FROM THIS FILE\n"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--capsule", type=Path,
                        default=Path("output/vp05_full_stage_execution_capsule"))
    parser.add_argument("--output", type=Path,
                        default=AUDIT / "vp05_full_stage_capsule_audit.json")
    args = parser.parse_args()
    capsule = args.capsule.resolve()
    source = ROOT.resolve()
    audit = AUDIT.resolve()
    checks = {}
    def ck(name, value):
        checks[name] = bool(value)
    ck("isolated_destination", capsule != source and source not in capsule.parents
       and capsule != audit and audit not in capsule.parents)
    ck("capsule_exists", capsule.is_dir())
    manifest = args.capsule / "CAPSULE_REVIEW_ONLY.json"
    ck("manifest_exists", manifest.is_file() and not manifest.is_symlink())
    data = {}
    if checks["manifest_exists"]:
        try:
            data = json.loads(manifest.read_text(encoding="utf-8-sig"))
        except (ValueError, OSError):
            pass
    ck("manifest_status", data.get("status") == "CAPSULE_CREATED_NOT_EXECUTED"
       and data.get("kira_executed") is False
       and data.get("ready_to_execute") is False)
    ck("manifest_destination", data.get("destination") == str(capsule))
    recorded = data.get("files_sha256", {})
    ck("manifest_lists_expected_files", isinstance(recorded, dict)
       and set(recorded) == set(FILES))
    actual = {}
    for relative in FILES:
        candidate = args.capsule / relative
        exists = candidate.is_file() and not candidate.is_symlink()
        ck("file_present_" + relative.replace("/", "_"), exists)
        if exists:
            actual[relative] = sha(candidate)
            ck("manifest_hash_" + relative.replace("/", "_"),
               isinstance(recorded, dict) and recorded.get(relative) == actual[relative])
        if relative != "jobs.yaml":
            original = ROOT / relative
            ck("source_hash_" + relative.replace("/", "_"),
               exists and original.is_file() and not original.is_symlink()
               and sha(original) == actual.get(relative))
    found = set()
    if args.capsule.is_dir():
        for path in args.capsule.rglob("*"):
            if path.is_symlink():
                found.add("SYMLINK:" + str(path.relative_to(args.capsule)))
            elif path.is_file():
                found.add(str(path.relative_to(args.capsule)).replace("\\", "/"))
    ck("no_extra_files_or_symlinks", found == set(FILES) | {"CAPSULE_REVIEW_ONLY.json"})
    ck("single_target_exact",
       (args.capsule / FILES[2]).is_file()
       and parse_file_integrals(args.capsule / FILES[2]) == [TARGET])
    preview = AUDIT / "vp05_single_nonmaster_full_stage_jobs.preview.yaml"
    ck("preview_exists", preview.is_file())
    if preview.is_file() and (args.capsule / "jobs.yaml").is_file():
        text = preview.read_text(encoding="utf-8-sig")
        ck("job_exact_preview", text.startswith(HEADER)
           and (args.capsule / "jobs.yaml").read_text(encoding="utf-8-sig") == text[len(HEADER):])
    else:
        ck("job_exact_preview", False)
    validation = AUDIT / "vp05_kira_full_stage_specific_validation.json"
    ck("prior_static_pass", validation.is_file()
       and json.loads(validation.read_text(encoding="utf-8-sig")).get("status") == "VP05_SPECIFIC_STATIC_PASS")
    failed = [key for key, passed in checks.items() if not passed]
    result = {"status": "CAPSULE_AUDIT_PASS_NOT_EXECUTED" if not failed else "CAPSULE_AUDIT_BLOCKED",
              "checks": checks, "failed": failed, "files_sha256": actual,
              "kira_executed": False, "vp05_reduction_executed": False,
              "schema_validated_by_kira_on_vp05": False, "ready_to_execute": False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("VP05_FULL_STAGE_CAPSULE_AUDIT " + json.dumps(result, ensure_ascii=False), flush=True)
    if failed:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
