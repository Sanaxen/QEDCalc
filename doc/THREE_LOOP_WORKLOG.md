

### 2026-11-20 VP05 Target A 1-row batch 285→288/339: three exact rows saved, fourth timed out; in-process per-row checkpoint implemented

The user uploaded `log_vp05_sector202_a_exact_single_next.txt` and `log_vp05_sector202_a_exact_single_audit.txt` (real Windows execution). Results agree: run `a339a`, processed **288/339**, rank **288**, dependent **0**, SHA256 **`3d6eddfcd30cf3a91c0f4674ed768bc38a19a055239a7390623d810f3d05dc57`**; old original source and certificate SHA pins valid and Step93 B preserved. Source rows **285→286** exited 0 after **588.9s**, **286→287** after **460.7s**, **287→288** after **453.7s**. **288→289 timed out at 901.9s with no new committed row**, and subsequent batches were correctly blocked. 51 original source rows remain. These summary logs do not isolate cost of rebuilding/replaying 288 source pivots each restart; code inspection confirms old exact engine replays all saved pivots against original IBP rows at each subprocess start. One-row subprocesses repeat this cost.

Implementation to reduce redundant full-state verification while retaining failure-proof checkpointing:
- Modified `examples/three_loop_vp05_sector202_exact_support_checkpoint.py`: new opt-in `--checkpoint-every-row`. Extracted the **same source checkpoint schema** into `save_exact_source_checkpoint(...)`, with exclusive temporary creation + fsync + os.replace. With this flag the existing strict QQ(z,d) original IBP replay for each newly calculated pivot is followed immediately by a durable checkpoint **per completed original row** within a single Python process. Existing old behavior remains the default without the flag; no Step93 or source conversion. A row timeout only loses unfinished row (checkpoint may remain advanced by already saved rows). Stale .tmp blocks exclusive save; never overwrite a stale intermediate.
- Updated `examples/three_loop_vp05_sector202_a_exact_batch.py` to **always supply `--checkpoint-every-row`** to the original engine for this isolated Target A run, allow at most **20 source rows** in one subprocess and **3600 seconds** subprocess timeout while still requiring exact explicit acknowledgement. Existing process/start checks, exact SHA configuration, non-overwrite attempt logs, input preservation and no Kira are unchanged. Its return status remains NOT_TARGET_PROOF even if all 339 pivots complete. Controller detects checkpoint advancement on a time stop and stops the batch series for audit.
- Extended `examples/test_three_loop_vp05_sector202_a_exact_batch.py` (15 tests) to validate injected flag and bounded budget.
- Added `examples/test_three_loop_vp05_sector202_exact_source_row_checkpoint.py` (2 offline serializer tests) to test atomic per-row state schema and refusal to clobber an abandoned .tmp. Code committed; **Windows unit-test PASS not yet supplied**.

New phase is **not** a new user Kira experiment and does not claim strict proof for Target A yet. Run the unit tests first; then one controlled single subprocess on existing `a339a` from 288 using up to **10 rows** and a 3600-second guard, auditing after. The controller will save each independently verified row, even if it cannot finish all ten before the guard. This is deliberately preferred to 10 separate replay-heavy one-row subprocesses.

```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_sector202_a_exact_batch examples.test_three_loop_vp05_sector202_exact_source_row_checkpoint -v
.\run_vp05_sector202_a_exact_batch.bat run --run-id a339a --batches 1 --rows-per-batch 10 --timeout-seconds 3600 --acknowledge EXECUTE_VP05_A_339_EXACT_SOURCE_BATCH > log_vp05_sector202_a_exact_rowcommit_run.txt 2>&1
.\run_vp05_sector202_a_exact_batch.bat audit --run-id a339a > log_vp05_sector202_a_exact_rowcommit_audit.txt 2>&1
```

Observe the saved checkpoint and internal batch attempt log if a timeout occurs. Do not change original stopped projects/Step93 B archive/union source. Even 339 source pivots is not exact Target A target identity until separate zero exact remainder and unscaled original-row IBP replay passes.


### 2026-11-20 VP05 sector202 Target A 288→292/339: row-level checkpoint survives 3600s timeout; timing instrumentation added

User supplied actual Windows `log_vp05_sector202_a_exact_rowcommit_run.txt` and `log_vp05_sector202_a_exact_rowcommit_audit.txt`. Both independently report exactly **292/339 processed original IBP source rows**, rank **292**, dependent **0**, with matching saved SHA256 `74e6594e4fd69682e95a79326821deaaf807264b3a89c83a3a28c6fa7929e9b6`. Source/checkpoint evidence remains pinned: source gzip `f0dd7f338ead97e455306bc49c4ce475fe8a8bee3e5a866f6fa17de1e9ad0163`, finite-field certificate `512114a669d3fb8761d89bfe11a51cc8ec146d46739a36b61e869edcddb583eb`. Controller status remains `VP05_A_339_EXACT_SOURCE_PARTIAL_PRESERVED_NOT_PROOF`.

One subprocess `batch_from_288_attempt_02.log` requested ten rows, but stopped after **3601.7s TIMEOUT**, durable advancement 288→292 (four rows). This directly confirms that the new in-process `--checkpoint-every-row` flag avoids discarding work when the long subprocess exceeds a wall-clock limit. **47 source rows remain.** No full Target A exact QQ(z,d) target proof, C retention, r7s5d3 local closure, or VP05 63-master closure. Kira not executed; Step93 and original source unchanged. Outer logs alone do not identify whether resume-time replay, actual exact elimination, or writing the growing checkpoint consumed the time.

Code changes to diagnose without altering the mathematics or safety bounds:
- `examples/three_loop_vp05_sector202_exact_support_checkpoint.py`: opt-in `--trace-source-timing` writes small read-only JSON console events for `resume_validation_complete`, `source_row_begin`, every ten elimination steps `elimination_progress` (row, elapsed, fill/support), `source_row_exact_verified`, and `source_row_checkpoint_durable` (save time). Existing exact original-IBP verification and per-row atomic checkpoint remain unchanged.
- `examples/three_loop_vp05_sector202_a_exact_batch.py`: always enables `--trace-source-timing` for next isolated A subprocess. The events go only to a newly named immutable per-attempt log inside the existing `a339a` log directory. No intermediate proof promotions.
- `examples/test_three_loop_vp05_sector202_a_exact_batch.py`: verifies timing flag is included. Unit-test Windows PASS not yet supplied.

Next Windows PowerShell:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_sector202_a_exact_batch examples.test_three_loop_vp05_sector202_exact_source_row_checkpoint -v
.\run_vp05_sector202_a_exact_batch.bat run --run-id a339a --batches 1 --rows-per-batch 10 --timeout-seconds 3600 --acknowledge EXECUTE_VP05_A_339_EXACT_SOURCE_BATCH > log_vp05_sector202_a_exact_timed_run.txt 2>&1
.\run_vp05_sector202_a_exact_batch.bat audit --run-id a339a > log_vp05_sector202_a_exact_timed_audit.txt 2>&1
```

Review both summary logs **and** the latest per-attempt `batch_from_292_attempt_01.log` for timings before considering changes to algorithm, wall-clock budget, hardware policy, or exact computation engine. Time ceiling may occur again, but completed original rows should still remain durable. Do not re-run the stopped Kira project `sec202a`.


### 2026-11-20 VP05 Target A timed row-commit continuation 292→294/339; internal timing log requested

Actual user-supplied Windows run log `log_vp05_sector202_a_exact_timed_run.txt` and independent read-only audit `log_vp05_sector202_a_exact_timed_audit.txt` agree on the same protected `a339a` source checkpoint: **294/339 processed**, rank **294**, dependent **0**, checkpoint SHA256 **`1b511c4fd23e39cc496d2410b0594503697199ad929aef9ec00d755779ba173d`**. New calculation advanced 292→294 despite the batch timing out after **3601.9 seconds**. 45 source rows remain. Both reports confirm unchanged original source and certificate hash values `f0dd7f338ead97e455306bc49c4ce475fe8a8bee3e5a866f6fa17de1e9ad0163` and `512114a669d3fb8761d89bfe11a51cc8ec146d46739a36b61e869edcddb583eb`, respectively; no Kira/Step93 mutation, no exact Target A proof, no C independent master-retention, and no 63-master closure.

The latest run's per-attempt internal timing log is reported at `output/three_loop_integral_family_audit/vp05_sector202_A_339_exact_a339a_logs/batch_from_292_attempt_01.log` but **was not included in the attachments**. Therefore the 3600s cannot yet be divided reliably into resume validation, each exact row elimination, and durable checkpoint serialization. Do **not** rerun a 3600s calculation purely to gather timing while this log may already exist: first read the existing internal log, including all `VP05_SECTOR202_EXACT_TIMING` records, its tail and `VP05_SECTOR202_EXACT_SUPPORT_PROGRESS` records. Inspect for last `phase` and any row-level plateau. Preserve checkpoint and all source/Step93/Kira inputs. Decide whether to optimize saved-pivot replay, row elimination, or checkpoint serialization based on observed timings.

Requested user command, no computation:

```powershell
Get-Content .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_logs\batch_from_292_attempt_01.log -Tail 150
```

Do not assert the Windows unit tests passed without an explicit test log. An exact original-source pivot pass is still not an exact QQ(z,d) Target A identity.


### 2026-11-20 VP05 sector202 Target A internal timing log decoded: expensive resume and late exact row processing

User uploaded Windows console/internal timing transcript `log(20261120-071058).txt`, containing the actual contents of `batch_from_292_attempt_01.log`. The timed run is already independently recorded as advancing saved 292→294 of 339, exact rank 294, with 3601.9s stop. Internal evidence:

- Initial 292 saved pivots were **fully verified on resume in 761.8s** (~12m42s). This is a material repeated fixed cost per process. No shortcut has been made to exact provenance replay.
- Original ID **2344**, new processed position 293: **89 exact elimination steps**, full row calculation/replay **1348.19s**, committed checkpoint **13.31s**. Step 80 was at **83.63s** elapsed; most of the unclassified row duration was after step 80 (remaining 9 eliminations plus normalization and original IBP replay).
- Original ID **2345**, new processed position 294: **56 exact elimination steps**, full row calculation/replay **880.12s**, checkpoint **12.68s**. Step 50 at **78.07s**, again the remaining 6 eliminations/normalization/replay dominate the unclassified tail.
- Original ID **2346**, next position 295, entered and reached **70 elimination steps** and **141.96s** within the same timed process. No `source_row_exact_verified`/durable checkpoint for it appears in the user transcript. Stop after 3601.9s with saved position 294. Do not interpret original ID 2346 as a mathematical failure; actual stop subphase beyond the last visible step cannot be inferred.
- This evidence shows checkpoint serialization (~13s) is not the dominant cost. Large exact rational expressions, late pivot elimination, normalization and source-row IBP replay need separate instrumentation; do not casually replace exact checks with modular sampling or allow proof promotions.

Committed additive, opt-in trace events in `examples/three_loop_vp05_sector202_exact_support_checkpoint.py` (triggered by existing `--trace-source-timing`) after the end of elimination and immediately after normalization and after original IBP replay. Events `row_elimination_complete`, `row_normalization_complete`, `row_original_ibp_replay_complete` and `dependent_row_ibp_replay_complete` have duration fields. **No algebraic manipulation, source identity, pivot ordering, checkpoint schema, hashing or safety caps were changed.** Run without altering `a339a` or saved Kira projects.

Before another long run, inspect whether previous timed internal log contains more lines than the console transcript. If further calculation is approved, the existing bounded isolated exact-A runner can be resumed from the current **294/339** with a single subprocess, per-row atomic commits, and instrumentation:

```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_sector202_a_exact_batch examples.test_three_loop_vp05_sector202_exact_source_row_checkpoint -v
.\run_vp05_sector202_a_exact_batch.bat run --run-id a339a --batches 1 --rows-per-batch 5 --timeout-seconds 3600 --acknowledge EXECUTE_VP05_A_339_EXACT_SOURCE_BATCH > log_vp05_sector202_a_exact_phase_run.txt 2>&1
.\run_vp05_sector202_a_exact_batch.bat audit --run-id a339a > log_vp05_sector202_a_exact_phase_audit.txt 2>&1
```

Inspect the newest batch internal `batch_from_294_attempt_01.log` to distinguish remaining late steps, normalization and exact IBP replay; do not infer that all 45 remaining rows will finish within a short duration. The exact **Target A zero rational-function remainder and independent unscaled original-IBP replay** remain not yet demonstrated. No Kira/Stage-2 boundary or 63-master closure claim.


### 2026-11-20 VP05 sector202 Target A phase-timed attempt saved 295/339; exact subphase diagnostics pending

User attached two UTF-16LE files `log_vp05_sector202_a_exact_phase_run.txt` and `log_vp05_sector202_a_exact_phase_audit.txt`, independently read and matched. Isolated run `a339a` progressed **294→295/339** with rank **295** and dependent **0**, before a **3601.8s timeout** from a single controlled subprocess. The current saved checkpoint SHA256 is **`b579c505e40ac4a5ad09a6258e746ad370398829b2884cae7d6537d26f27aa20`**, consistent in both files. Original source SHA256 `f0dd7f338ead97e455306bc49c4ce475fe8a8bee3e5a866f6fa17de1e9ad0163` and certificate SHA256 `512114a669d3fb8761d89bfe11a51cc8ec146d46739a36b61e869edcddb583eb` remain bound; no Kira or original/Step93 mutation is reported. Durable per-completed-row checkpointing again preserved one newly verified pivot despite the timeout.

The last attempt internal log is listed at `output/three_loop_integral_family_audit/vp05_sector202_A_339_exact_a339a_logs/batch_from_294_attempt_01.log`, **not uploaded yet**. The aggregate logs do not include the added `row_elimination_complete`, `row_normalization_complete`, `row_original_ibp_replay_complete` and timing information. Therefore do not attribute the slowdown to any of those phases without that internal file. **44 original source rows remain, but Target A exact rational-function identity, C master retention and full VP05 basis closure remain unproven.**

Next action is read-only log inspection, *before* any repeat 3600-second run:

```powershell
Get-Content .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_logs\batch_from_294_attempt_01.log -Tail 150
```

Preserve the saved `a339a` checkpoint and immutable per-attempt logs; no new Kira/FireFly experiment or aggressive lifting of time limits while the bottleneck is unclassified.


### 2026-11-20 VP05 A 295/339: observed late elimination bottleneck, per-step profile added

User provided read-only Windows console transcript `log(20261120-085839).txt`, showing the actual `batch_from_294_attempt_01.log` timing records:
- Resume verification of **294 previously saved original-IBP exact pivots: 854.21 seconds**. This is full exact provenance replay, not a random-modular-only check.
- The original source row **ID 2346** (saved position **295**, 75 pivots eliminated): through step 70 in **154.05s** but all 75 steps in **1551.57s**; thus the **final five steps consumed ~1397.52s**. Normalization **23.65s**, independent original-IBP replay **62.51s**, atomic checkpoint save **14.52s**. The row completed and was durably saved at processed 295. This proves time is dominated by late elimination plus one-time full resume replay, rather than by checkpoint serialization.
- Original source row **ID 2347** (next unfinished row, position 296): after 40 steps **321.77s**, with steps 31–40 consuming **316.8s**. This row was not verified/committed before the 3601.8s controller timeout. No mathematical failure observed. **44 original source rows** remain.
- Long final-step duration may come from `subtract(cur,brow,factor)` (row coefficients), `subtract(trace,btrace,factor)` (provenance), or their exact representation/cap checks; the existing ten-step timing cannot distinguish these and must not be overinterpreted as only coefficient swell.

Minimal *measurement-only* change committed in `examples/three_loop_vp05_sector202_exact_support_checkpoint.py`: with existing `--trace-source-timing`, also log **each elimination step after step 30** as `VP05_SECTOR202_EXACT_STEP_PROFILE`. Each event separately reports `row_subtract_s`, `source_subtract_s`, `post_subtract_checks_s`, current columns/support and pivot sizes, and row elapsed. Exact `subtract`/normalization/`verify` calls, source ordering, checkpoint schema and guard caps have **not** changed. The `a339a` controller already enables `--trace-source-timing`. No new Kira/FireFly nor changes to immutable Step93 B or original source.

Next test cautiously with only one new row requested, same single-process per-row durable checkpoint:

```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_sector202_a_exact_batch examples.test_three_loop_vp05_sector202_exact_source_row_checkpoint -v
.\run_vp05_sector202_a_exact_batch.bat run --run-id a339a --batches 1 --rows-per-batch 1 --timeout-seconds 3600 --acknowledge EXECUTE_VP05_A_339_EXACT_SOURCE_BATCH > log_vp05_sector202_a_exact_step_profile_run.txt 2>&1
.\run_vp05_sector202_a_exact_batch.bat audit --run-id a339a > log_vp05_sector202_a_exact_step_profile_audit.txt 2>&1
```

Before any run, prioritize inspecting already available timed attempt log; new profile is necessary only for finer-grained diagnosis. On a timeout collect the new internal `batch_from_295_attempt_01.log` and compare row/source/check parts. If original row 2347 is extremely expensive at 3600s, stop and consider a separate exact elimination optimization method rather than simply repeating timeouts. Full source processing is not exact Target A target identity proof. Preserve the last independently audited SHA-pinned checkpoint `b579c505e40ac4a5ad09a6258e746ad370398829b2884cae7d6537d26f27aa20`.
