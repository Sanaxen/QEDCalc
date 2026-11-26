

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


### 2026-11-20 VP05 sector202 Target A 295→296/339: profiled one-row run exit 0; internal step log pending

Windows logs `log_vp05_sector202_a_exact_step_profile_run.txt` and `log_vp05_sector202_a_exact_step_profile_audit.txt` were uploaded and their UTF-16 contents cross-checked. Isolated run `a339a` advances saved original-source exact checkpoint from **295 to 296 / 339**. One subprocess exited normally (`exit_code=0`, `timed_out=false`) in **2379.4 seconds** (approximately 39m39s). Saved **rank=296**, **dependent=0**, checkpoint SHA256 `90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297` matched both independent outer logs. Original source SHA256 `f0dd7f338ead97e455306bc49c4ce475fe8a8bee3e5a866f6fa17de1e9ad0163` and modular certificate SHA256 `512114a669d3fb8761d89bfe11a51cc8ec146d46739a36b61e869edcddb583eb` remain unchanged. No Kira or protected Step93 source changes; **43 source rows remain**. Target A exact reduction, sector202 retained masters and VP05 63-master closure remain unproven.

The isolated per-step profiling log file exists by controller report at `output/three_loop_integral_family_audit/vp05_sector202_A_339_exact_a339a_logs/batch_from_295_attempt_01.log` but was **not among these two attachments**. This internal log records timing per late elimination step; its evidence is necessary before attributing the ~2379s to exact row subtraction, original-IBP provenance subtraction or size checks. The next action is **read-only inspection** of that existing log rather than initiating another ~1-hour single-row attempt merely to gather profiling information.

```powershell
Get-Content .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_logs\batch_from_295_attempt_01.log -Tail 150
```

If the file is available, upload its complete content. Keep all previous batch logs and checkpoints intact; do not weaken QQ(z,d) identity testing in favor of modular-only evidence, raise memory limits, or rerun stopped Kira.


### 2026-11-20 VP05 sector202 Target A 296/339: actual late-step exact profiling identifies provenance subtraction bottleneck

User uploaded actual internal Windows `batch_from_295_attempt_01.log` (not just outer summaries). Source row original ID **2347** is the completed processed row **296**; prior external audit independently matches checkpoint SHA256 `90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`, rank296, dependent0, 43 source rows remain.

Detailed timing in this log:
- 295 previously saved pivot rows' exact provenance replay at process startup: **890.89s**.
- Source row 2347 elimination completed at **1403.76s**, 52 steps; normalization **13.60s**, original-source IBP exact replay **52.48s**, durable checkpoint **14.98s**; new row takes **1484.81s** including checkpoint.
- Step-by-step profile for steps 31–52 inclusive summed: `row_subtract_s=419.910`, `source_subtract_s=960.536`, `post_subtract_checks_s=18.628` seconds. Provenance subtraction consumes **approximately 68.7%** of these timed subphases, integral row subtraction **30.0%** and safety checks **1.3%**. These sums exclude first 30 cheap steps and phases beyond the elimination loop.
- Most expensive steps **39–45**: row subtraction **368.624s**, original-IBP provenance subtraction **917.906s**, post checks **10.058s**; combined row+trace **1286.53s**. Step 41 provenance subtraction **225.619s**; step 42 provenance subtraction **227.808s**. The bottleneck is exact QQ(z,d) rational coefficients attached to extensive provenance support (trace support ~109–135), **not** checkpoint serialization, cap scans or normalization.
- Existing `subtract(dest,source,mult)` in `examples/three_loop_vp05_sector202_exact_prefix_smoke.py` performs a full `sp.cancel(dest.get(k,0)-mult*v)` on every coefficient per update, used for both current integral row and original-source provenance. This repeated symbolic rational cancellation is a strong optimization target, but replacing it with unverified modular arithmetic, lazy expressions, or arbitrary changed reduction order would risk the exact certificate. Preserve original sources, current exact checkpoint and replay verification.

Decision: **do not change the proven algorithm in place or run another long computation for timing.** First design and verify a separate exact-equivalent sparse rational-function subtraction implementation, with random QQ(z,d) coefficient identities, original-IBP replay and compare against current SymPy `sp.cancel`; benchmark on **saved representative late exact coefficients** or an isolated copy, before opt-in execution. Retain the existing default, all per-row atomic saves, full exact replay and RAM/timeout policies. Do not claim a speedup without a real benchmark. No Kira/FireFly. Test log for Windows tests has not been attached.

All results are still source-pivot proof progress, **not** a final exact target A identity, C master retention or VP05 63-master closure.


### 2026-11-20 VP05 Target A 296/339: isolated exact QQ(z,d) subtraction probe and tests, no production switch

User requested continuation of the measured performance optimization. We **did not change** the exact source engine's SymPy `subtract`, exact source provenance replay, pivot ordering, controller time/RAM limits, saved 296/339 checkpoint, protected Step93 B, or Kira/FireFly projects.

Added `examples/three_loop_vp05_exact_arithmetic_probe.py`: read-only candidate implementing exact sparse subtraction in the rational fraction field `QQ(z,d)` using `sympy.polys.fields.field`, converting FracElement values to/from SymPy expressions only as part of the benchmark. It measures the **existing per-key `sp.cancel` implementation** against a separate field candidate and checks all output keys and coefficients using an independent `sp.cancel` difference equal to zero. It reports per-case full conversion-inclusive seconds, speed ratios, and whether exact equivalence passed; no automatic promotion, no modular-only proof and no production engine mutation.

The probe includes 3 compact synthetic test cases, plus a bounded selection of actual saved original-source provenance coefficients from the isolated Target A source checkpoint, refusing B/wrong scope/mismatched SHA256, with limits `--cases 1..5`, `--max-terms 1..12` and `--max-chars 16..240` for a safe first trial. This **tests only small sampled arithmetic operations**; it does not benchmark the full 100+ support updates nor guarantee production speedup. The saved file must be uploaded/available locally on the user's Windows machine; scripts are designed to read its existing canonical location.

Added `examples/test_three_loop_vp05_exact_arithmetic_probe.py` with 5 offline tests: zero cancellation, the 3 analytic mixed sparse cases, **32 deterministic rational-function QQ(z,d) cases**, in-memory input nonmutation, saved SHA mismatch rejection and wrong-target checkpoint refusal. A private local prototype running the same 32 deterministic rational-function cases yielded **PASS**. Local 3 tiny case timings were ~0.13x (slower for trivial zero), ~3.3x and ~3.9x relative to `sp.cancel`; these are not user's Windows timings and must not be presented as established end-to-end acceleration. Windows run of committed test file **not yet observed**; no claim of Windows PASS.

On user's existing Windows repository, first:

```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_exact_arithmetic_probe -v
python -m examples.three_loop_vp05_exact_arithmetic_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --expected-sha256 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297 --cases 2 --max-terms 4 --max-chars 240 > log_vp05_exact_arithmetic_probe.txt 2>&1
```

The SHA256 pin is from the user's **most recently audited 296/339** checkpoint. If it mismatches because source work advanced, inspect and re-audit rather than bypassing the pin. If it says insufficient sampled provenance entries, log that result and adjust only the bounded *sampling* options, not the input or proof. Do not run the full Target A source elimination concurrently with this probe. Original source checkpoint exactness and Target A final identity remain distinct.

The user's latest saved results remain **296/339 processed, rank296, dependent0, 43 rows remaining**. The experimental field arithmetic remains opt-in and isolated until real bounded Windows benchmark and exact comparisons justify a controlled integration; do not promise or claim speed gain for full symbolic source replay.


### 2026-11-20 VP05 A saved checkpoint exact arithmetic probe: Windows small-sample equivalence PASS, production untouched

User uploaded actual Windows UTF-16LE `log_vp05_exact_arithmetic_probe.txt`; parsed one `VP05_EXACT_ARITHMETIC_PROBE` record:
- Status **`EXACT_EQUIVALENCE_PASS_PROBE_ONLY`**; every comparison `exact_pass=true`. Checkpoint `a339a` SHA256 pinned **`90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`**, saved processed **296/339**. `checkpoint_modified=false`, `production_engine_modified=false`, `target_A_proven=false`, `kira_executed=false`.
- Synthetic zero-cancel: baseline **0.000078s**, QQ(z,d) candidate **0.000325s**, baseline/candidate ratio **0.2392** (candidate *slower*). Synthetic rational overlap: **0.008284s vs 0.001600s** (**5.1789x**). Nontrivial rational: **0.007671s vs 0.001821s** (**4.213x**).
- Two **real saved-provenance samples of 4 source terms each** (8 output terms) completed exact comparison. First: **0.005211s vs 0.001768s** (**2.9471x**); second: **0.005506s vs 0.002058s** (**2.6758x**). These numbers include per-case SymPy-to-field conversion and back, but are milliseconds and do **not** benchmark the 100+ provenance support or full late source-row elimination/replay. The field approach is promising on compact rational samples, but **no full-run speedup was established**. The 5-file offline unittest output was not attached; do not claim Windows unit-test pass.
- The actual 296/339 checkpoint is intact, rank 296 and dependent0 from previous audit; **43 source rows remain**. Mathematical Target A exact rational-function reduction, independent unscaled original-source replay for A, sector202 C master retention and VP05 63-master closure remain unproven.

Next safe action: run the **already installed** read-only arithmetic benchmark with 12 terms (vs previous 4), 240 chars, two bounded saved original-source samples. Do not change production engine or checkpoint. Reuse the same pinned SHA256 and do not run Kira or the 1-hour exact source batch concurrently:

```powershell
python -m examples.three_loop_vp05_exact_arithmetic_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --expected-sha256 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297 --cases 2 --max-terms 12 --max-chars 240 > log_vp05_exact_arithmetic_probe_12terms.txt 2>&1
```

If there are too few qualifying saved samples, this is a bounded selection limitation rather than a mathematical failure. Do not bypass checkpoint SHA pin. If exact-equivalent 12-term tests succeed with reasonable timings, design/benchmark a broader 100+ support sample and potentially reusable field context before introducing any opt-in exact engine change.


### 2026-11-20 VP05 Target A saved-provenance arithmetic probe: 12-term Windows exact PASS and safe 100+ support inventory

User uploaded UTF-16LE `log_vp05_exact_arithmetic_probe_12terms.txt`, decoded and parsed. Result `EXACT_EQUIVALENCE_PASS_PROBE_ONLY` for all 5 cases, including two **real saved 12-term provenance** comparisons against unchanged checkpoint SHA256 `90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297` (**296/339**, rank296, dependent0 from prior audit):
- Saved provenance case 0: original `sp.cancel` **0.036483s**, isolated exact QQ(z,d) candidate **0.008604s**, ratio **4.2403x**; 12 source terms, 12 destination terms, 13 output terms, `exact_pass=true`.
- Saved provenance case 1: original **0.020817s**, candidate **0.007406s**, ratio **2.8109x**; 12 source terms, 12 destination terms, 23 output terms, `exact_pass=true`.
- Synthetic rational-overlap **5.3149x**, nontrivial **4.2857x**, trivial zero cancellation slower (0.2412x). All strictly equal via symbolic `sp.cancel` difference, not finite-field checks.
- The probe itself reports checkpoint and production engine unmodified, Target A not proven, no Kira. This is a 12-term microbenchmark, **not** a proof of 100+ support full update speed or final Target A identity.

Implemented guarded experimental-only changes, **no production engine or checkpoint mutation**:
- `examples/three_loop_vp05_exact_arithmetic_probe.py` extends `--max-terms` to **128**, bounds coefficient string length to at most **600**, and filters candidate traces by string length **before** parsing SymPy expressions. Adds `--inventory-only` to read the pinned checkpoint and report max qualifying support and counts with ≥50, ≥100, ≥128 coefficients. Inventory performs **no coefficient conversion or subtraction**, no saved data writes. Existing symbolic exact comparison and output policy remain.
- `examples/test_three_loop_vp05_exact_arithmetic_probe.py` now includes **7 offline tests**, adding mock 100-term support count/immutability and SHA mismatch. Windows PASS **not yet supplied**; do not claim it.
- Start with read-only inventory at coefficient limit 240 chars, using pinned checkpoint SHA, to establish whether 100-term test cases even exist. Only after that, if at least **two** qualifying saved pivot traces exist, run **one** 100-term exact comparison with one case. Avoid unconstrained 128-term benchmark or increasing char caps until evidence warrants. The inventory counts qualifying pivots but not which pair is selected; if no pair, record the limitation.

Suggested Windows PowerShell:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_exact_arithmetic_probe -v
python -m examples.three_loop_vp05_exact_arithmetic_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --expected-sha256 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297 --inventory-only --max-chars 240 > log_vp05_exact_arithmetic_inventory.txt 2>&1
```

Stop after inventory for review; do not initiate the 100-term benchmark until qualifying support/count and Windows tests are checked. If inventory has sufficient samples, plan isolated read-only `--cases 1 --max-terms 100 --max-chars 240`, bounded by an external controller timeout if expression complexity grows. Preserve original protected input and any critical source proof. No master-basis closure or Target A proof claimed.


### 2026-11-20 VP05 A read-only saved provenance inventory: only one 100-term qualifying trace

User uploaded `log_vp05_exact_arithmetic_inventory.txt` with actual Windows result `VP05_EXACT_ARITHMETIC_INVENTORY` status `READ_ONLY_SAVED_PROVENANCE_INVENTORY_NOT_PROOF`. SHA256 of isolated Target A checkpoint matches `90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`; processed **296/339**. With **max coefficient expression string length=240**, eligible-pivot counts are: **11** pivots with ≥50 provenance entries, **1** pivot with ≥100 entries, **0** pivots with ≥128 entries, and max eligible support **111**. Checkpoint/production engine remain unmodified; Target A not proved.

Current `sampled_cases_from_checkpoint` uses two **distinct qualifying** pivot provenance rows per full comparison, so merely selecting `--max-terms 100` with these data would raise an **insufficient qualifying samples** error. Do NOT pretend 100-term comparison is already possible. Next choose **50-term** bounded true provenance comparison using two eligible saved pivots, one case, exact QQ(z,d) candidate compared against existing per-key `sp.cancel`, and checkpoint hash guard. This does not perform new Kira or run long exact source checkpoint continuation.

```powershell
python -m examples.three_loop_vp05_exact_arithmetic_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --expected-sha256 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297 --cases 1 --max-terms 50 --max-chars 240 > log_vp05_exact_arithmetic_probe_50terms.txt 2>&1
```

If 50 terms still show accurate full sparse symbolics and a useful speedup, next develop a bounded mixed-size source/destination benchmark (one 100+ trace paired with an eligible smaller trace) and/or direct coefficient-series benchmarking on the real saved 100+ trace, making source/destination size explicit. Never convert benchmark-only result to Target A exact proof or final 63-master closure; 43 original source rows remain and original source rowspace proof does not itself establish Target A.


### 2026-11-20 VP05 A 50-term Windows exact field microbenchmark PASS; mixed-support 100→50 candidate added

The user uploaded `log_vp05_exact_arithmetic_probe_50terms.txt`. Its actual decoded Windows run reports `EXACT_EQUIVALENCE_PASS_PROBE_ONLY`, checkpoint SHA256 `90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`, processed **296/339**, and no saved data or production engine mutation. The genuine saved provenance 50-term case named `saved_provenance_166595340533761_139_00` had **50 source terms**, **50 destination terms**, **80 result terms**: baseline full per-coefficient SymPy `sp.cancel` subtraction **0.510826s**, exact QQ(z,d) field candidate including conversions **0.178561s**, ratio **2.8608x**, independent exact symbolic equality PASS. Three synthetic cases also passed, but trivial zero cancellation remains slower under field conversion. These are sampled arithmetic microbenchmarks, NOT observed full source-row elimination timings or final proof. Production checkpoint is untouched, 43 source rows remain.

The previous read-only inventory showed with coefficient strings ≤240 characters: 11 pivots qualify at ≥50 support, but **only one** at ≥100 support. Hence the old symmetric sample selection cannot test 100-vs-100. Added a new **opt-in, SHA-pinned, bounded, read-only unequal-support** sample method `sampled_mixed_support_case` to `examples/three_loop_vp05_exact_arithmetic_probe.py`. It selects one eligible >=100 source pivot and a **different** >=50 destination pivot and performs one exact symbolic subtraction with the same independent full coefficient-equality verifier. The 100/50 arithmetic is still synthetic pairing of **genuine checkpoint coefficients**, not a reproduction of the original 41/42 expensive elimination multiplier or pivot path. Original production `subtract`, Kira, saved 296 checkpoint, Stage 93 and worklog provenance are unchanged. Added two offline unit tests (total **9** in probe test module) to verify 100/50 exact equality, immutable checkpoint, SHA validation and refusal when no distinct destination exists. Windows PASS of updated tests and 100/50 benchmark **not yet supplied**.

Next bounded Windows run (after pulling and tests):

```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_exact_arithmetic_probe -v
python -m examples.three_loop_vp05_exact_arithmetic_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --expected-sha256 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297 --mixed-source-terms 100 --mixed-dest-terms 50 --max-chars 240 > log_vp05_exact_arithmetic_probe_mixed100x50.txt 2>&1
```

If the mixed sample cannot be selected, report limitations instead of changing the checkpoint or pretending it passed. This single case may be more expensive than prior tests, but no full exact-source/Kira job is started. Do not claim benchmark speedups automatically carry over to entire source-row proof; retain exact original-IBP replays.


### 2026-11-20 VP05 A Windows mixed provenance 100-source × 50-destination exact comparison PASS

User uploaded original UTF-16LE Windows `log_vp05_exact_arithmetic_probe_mixed100x50.txt`; its single JSON result was decoded from the actual attachment and verified:
- Status `EXACT_EQUIVALENCE_PASS_PROBE_ONLY`; case `mixed_saved_source_166595340009474_139_100_to_50`.
- Two **distinct saved original-source pivot provenance** sets, 100 source terms and 50 destination terms; exact output 130 nonzero terms, exact-symbolic equality `exact_pass=true`.
- Baseline per-key SymPy `sp.cancel` subtraction **0.855611 s** versus isolated `QQ(z,d)` fraction-field subtraction including SymPy round-trip **0.307200 s**, measured ratio **2.7852x**.
- SHA256-pinned original exact source checkpoint: `90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`, position **296/339**, no source or engine mutation, Target A exact proof false, no Kira.
- Together with smaller 4/12/50-term exact-equivalent comparisons this is promising evidence for a separately testable field arithmetic backend. However **the pairing and multiplier are synthetic**; this is not a verbatim replay of the slow original ID 2347 step 41/42, nor a measured production-engine speedup, and does not establish Target A exact identity or 63-master closure. Only this isolated microbenchmark is confirmed PASS; the most recently updated unittest runner's Windows output was not provided.

Next **read-only** step: inventory larger expression coefficients before selecting a stronger test and designing an opt-in guarded field-backend pilot. Probe inventory at `--max-chars 600` using the same pinned checkpoint; compare distribution to prior 240-character inventory (11 pivots with ≥50 entries, 1 with ≥100, max 111). Do not blindly raise production expression/support/swap caps or overwrite immutable evidence.

```powershell
python -m examples.three_loop_vp05_exact_arithmetic_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --expected-sha256 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297 --inventory-only --max-chars 600 > log_vp05_exact_arithmetic_inventory_600.txt 2>&1
```

Once characterized, a production candidate should be strictly **opt-in**, first tested against exact `sp.cancel` and original-source IBP symbolic replay on isolated samples, preserve the old default, source and all Step93 artifacts, use limited run scope and per-row atomic checkpoints. Avoid promoting an arithmetic-only equivalence probe to mathematical Target A proof.


### 2026-11-20 VP05 Target A read-only arithmetic inventory with 600-character bound: 3 pivots ≥128 support

User uploaded actual Windows UTF-16LE `log_vp05_exact_arithmetic_inventory_600.txt`, parsed as `VP05_EXACT_ARITHMETIC_INVENTORY`:
- status `READ_ONLY_SAVED_PROVENANCE_INVENTORY_NOT_PROOF`, max coefficient string length **600**.
- Checkpoint SHA256 `90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`, processed **296/339**, no checkpoint or production engine mutation and `target_A_proven=false`.
- Qualifying entries: max support **136**; **18** saved pivots have ≥50 coefficient strings of ≤600 chars; **3** have ≥100 and **3** have ≥128.
- Compare 240-char earlier read-only audit: max support111, 11 pivots≥50, 1≥100, 0≥128. Therefore two distinct saved pivot traces now qualify for a symmetric 100-by-100 or 128-by-128 arithmetic microbenchmark; this does not imply the arithmetic is fast, and large rational expressions may cause time/space blowup.

Next *bounded* diagnostic should begin with **one 100×100 case** and max expression string length 600, rather than untested 128×128. Existing read-only probe takes `--cases 1 --max-terms 100 --max-chars 600` and the exact SHA pin; it does not mutate the production source engine. Do not attempt source-family proof continuation or new Kira simultaneously. On a timeout or failure, retain existing data and inspect the log; do not weaken exact `sp.cancel` equality or claim an extrapolated full-run speedup.

```powershell
python -m examples.three_loop_vp05_exact_arithmetic_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --expected-sha256 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297 --cases 1 --max-terms 100 --max-chars 600 > log_vp05_exact_arithmetic_probe_100terms_600.txt 2>&1
```

For explicit wall-clock safety, use PowerShell `Start-Process -PassThru` and `Wait-Process -Timeout` with a guard if this run is performed during normal unattended use; the existing standalone probe itself has **no internal timeout**. Avoid claiming the above command is automatically bounded in elapsed time. This still measures only synthetically paired genuine saved coefficients rather than original expensive 2347 elimination and does not prove final Target A identity or full 63-master basis.


### 2026-11-20 VP05 A exact arithmetic: real Windows 100×100 saved provenance PASS (4.12x microbenchmark)

User uploaded real Windows UTF-16LE `log_vp05_exact_arithmetic_probe_100terms_600.txt`, decoded from the file bytes. The `VP05_EXACT_ARITHMETIC_PROBE` result reports `EXACT_EQUIVALENCE_PASS_PROBE_ONLY` and all exact comparisons pass. Main saved provenance case `saved_provenance_166595340009474_139_00` selected two genuine stored coefficient sets with **100 source terms and 100 destination terms**, producing **103 nonzero result terms**, with expression string cap 600. Existing per-term `sp.cancel` baseline **4.343657 s**, candidate `QQ(z,d)` rational-field conversion and subtraction **1.053755 s**, measured **4.1221× faster** for this synthetic pairing; symbolic exact equivalence `exact_pass=true`.

The synthetic controls also pass: rational_overlap speed ratio 4.9064x, rational_nontrivial 4.3789x; trivial zero-cancel slower, 0.2833x. Original source checkpoint is still **296/339**, SHA256 **`90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`**, `checkpoint_modified=false`, `production_engine_modified=false`, `target_A_proven=false`, `kira_executed=false`. No claim of measured full elimination-speed improvement, completed A identity, C master retention or VP05 63-master closure. 43 original source rows remain.

Candidate field arithmetic now passes real small 4-term, 12-term, 50-term, mixed 100×50 and 100×100 provenance microbenchmarks. The 600-char inventory found **three distinct saved pivots with ≥128 eligible provenance entries**, so an additional **single 128×128** exact read-only comparison can be attempted cautiously using the existing guarded data scope. Keep full exact equality check, pinned source SHA, and original engine unchanged; do not extrapolate 4.12x to actual 200-second symbolic steps.

```powershell
python -m examples.three_loop_vp05_exact_arithmetic_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --expected-sha256 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297 --cases 1 --max-terms 128 --max-chars 600 > log_vp05_exact_arithmetic_probe_128terms_600.txt 2>&1
```

Standalone script has **no internal wall-clock limit**; keep the process monitored or use a separately bounded subprocess. After this arithmetic-only benchmark, design **opt-in and isolated exact source-row pilot** with same original-source IBP replay and saved checkpoint protection, comparing to original SymPy version on an independently verified small source subset. Never introduce candidate arithmetic directly into the already saved `a339a` run without a documented equivalence and rollback protocol.


### 2026-11-20 VP05 A exact rational-field 128×128 Windows PASS; bounded persistent-field sequence pilot introduced

User uploaded real UTF-16LE `log_vp05_exact_arithmetic_probe_128terms_600.txt` and the output was decoded directly. Status `EXACT_EQUIVALENCE_PASS_PROBE_ONLY`. Genuine stored original-source provenance coefficient pairing `saved_provenance_166595340009474_139_00`: **128 source entries**, **128 destination entries**, **133 nonzero output entries**, full exact equality `exact_pass=true`. SymPy per-key `sp.cancel` baseline **5.174119s**, isolated exact fraction-field candidate including conversion **1.292855s**, observed ratio **4.0021x** for this synthetic pairing. All synthetic small controls passed exact comparison; trivial zero cancel remained slower (`0.3235x`). Checkpoint SHA256 pinned at `90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`, saved processed **296/339**, no production engine or checkpoint mutation, no new Kira, `target_A_proven=false`.

After passing 4-, 12-, 50-, mixed 100×50, 100×100, and now 128×128 arithmetic benchmarks, the next unresolved question is the **reuse of QQ(z,d) internal representation across several consecutive provenance updates**. Added independent, opt-in, read-only `examples/three_loop_vp05_exact_sequential_probe.py`. It samples `rounds+1` *distinct* SHA-pinned saved pivot source traces, bounded by coefficient size and term count, benchmarks repeated unchanged SymPy `sp.cancel` updates against a persistent field-state candidate, and performs **complete `sp.cancel` symbolic equality checks after each update**. It separately accounts for one-time conversion to the field and reports per-round coefficient calculation time and full exact comparison time, avoiding optimistic field-only timing. It never executes source-row Kira, never changes production arithmetic or saved checkpoint, and explicitly outputs `real_original_ibp_path_replayed=false`. The samples and update multipliers are synthetic, not the observed original 2347 elimination pivot path; this is **not** a proof of the original full IBP family or a production performance claim.

Added 5 offline tests in `examples/test_three_loop_vp05_exact_sequential_probe.py` for two exact updates, cancellation/reintroduction, malformed multiplier rejection, saved-state SHA pin/selection/immutability, and refusal on insufficient qualifying pivot traces. **Windows tests of this new module have not yet been observed**; do not claim PASS in user's environment.

Next bounded experimental run, initially **50 terms and two sequential updates**, because 600-character inventory has 18 distinct qualifying traces at >=50 entries. This should be evaluated before attempting 128 terms and >1 update, which may trigger field expression swell. On user's Windows repository:

```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_exact_arithmetic_probe examples.test_three_loop_vp05_exact_sequential_probe -v
python -m examples.three_loop_vp05_exact_sequential_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --expected-sha256 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297 --terms 50 --max-chars 600 --rounds 2 > log_vp05_exact_sequential_probe_50x2.txt 2>&1
```

The standalone pilot has no automatic wall-clock kill; monitor process/time/memory, and stop if abnormal. Review internal output including `one_time_field_conversion_s`, `total_baseline_update_s`, `total_field_update_plus_conversion_s`, per-round `exact_pass` and `verification_s`. Do not claim final Target A QQ(z,d) reduction proof, new-sector master C retention, or global 63-master closure based on sampled arithmetic alone. Production source remains **296/339**, 43 unprocessed source rows, until a separately run and audited exact source continuation.


### 2026-11-20 VP05 Target A 50-term two-update persistent QQ(z,d) Windows test PASS

User uploaded Windows UTF-16LE `log_vp05_exact_sequential_probe_50x2.txt`. Actual single `VP05_EXACT_SEQUENTIAL_PROBE` JSON record was decoded and independently parsed:
- Overall **`EXACT_SEQUENCE_PASS_PROBE_ONLY`**, 2 requested and 2 completed rounds, **both `exact_pass=true`** against full strict SymPy `sp.cancel` difference after every update.
- First 50-term update: baseline SymPy `sp.cancel` **3.428604s**, persistent fraction-field update **0.099640s**, output 60 nonzero terms, strict equality verification **0.210665s**.
- Second 50-term update: baseline **10.232445s**, persistent fraction-field update **0.228318s**, output 65 nonzero terms, strict equality verification **0.588806s**.
- One-time conversion into QQ(z,d) field representation **0.577416s**. Baseline update subtotal **13.661049s**. Field conversion plus both update subtotals **0.905374s**, ratio **15.0888×**. Including the two standalone strict comparisons (0.799471s) gives **1.704845s** and **8.0131×** ratio against the baseline subtotal, for this particular benchmark. End-to-end reported wall **15.367071s** because it executes **both paths and verification**, not because optimized-only took 15.367 seconds. Distinguish benchmark overhead from candidate runtime.
- SHA256-pinned original A checkpoint **`90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`**, processed **296/339**, `checkpoint_modified=false`, `production_engine_modified=false`, `target_A_proven=false`, `kira_executed=false`, `real_original_ibp_path_replayed=false`. **43 source rows remain**. These are synthetically sequenced genuine saved provenance traces, not actual IBP elimination multipliers/path, not a full-stage speed claim.

Next cautious **read-only** scaling experiment on the same three eligible saved ≥128-entry traces, but only **one update** with 128 terms before attempting two larger updates; requires still-exact per-update independent equality and pinned input. Existing standalone probe's `--terms 128 --rounds 1 --max-chars 600` supports this without repository changes. It has no built-in timeout; monitor its runtime/memory; do not assume bound solely because round count is 1. E.g.:

```powershell
python -m examples.three_loop_vp05_exact_sequential_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --expected-sha256 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297 --terms 128 --max-chars 600 --rounds 1 > log_vp05_exact_sequential_probe_128x1.txt 2>&1
```

Only after successfully comparing a more realistic elimination path and independent QQ(z,d) original-IBP replay should opt-in production integration be considered; never mutate existing 296-row saved state or Step93 B archive based on microbenchmarks alone.


### 2026-11-20 VP05 A 128-term one-update persistent QQ(z,d) Windows PASS; input remains protected

User uploaded actual Windows UTF-16LE `log_vp05_exact_sequential_probe_128x1.txt` (decoded from attachment). The result `VP05_EXACT_SEQUENTIAL_PROBE` reported `status=EXACT_SEQUENCE_PASS_PROBE_ONLY`, one completed 128-source-term update resulting in **133** output terms, with **`exact_pass=true`** against a full independent symbolic SymPy `sp.cancel` comparison.

Timing: prior SymPy update **5.157762s**; persistent QQ(z,d) field update **0.224192s**, one-time conversion of chosen saved traces and multiplier **0.689511s**, field update plus conversion **0.913703s**, ratio **5.6449x** for this synthetic update. Independent full exact equality verification cost **0.394282s**; including conversion, field update and independent comparison **1.307985s**, ratio **3.9433x** versus baseline update alone. Reported `wall_s=6.466641s` measures both competing paths and verification in the same diagnostic invocation, **not** optimized-only wall time.

Pinned original Target A checkpoint SHA256 **`90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`**, processed **296/339**, checkpoint/production engine unchanged, no Kira, Target A not proven, **`real_original_ibp_path_replayed=false`**. This validates exact arithmetic of an independently sampled 128-term stored provenance update, *not* original Kira/IBP elimination sequence, not a full speedup claim, not Stage-2/63-master closure. There are **43 source rows left** in the saved 339 source-row pivot task.

The existing read-only persistent QQ(z,d) sequence probe supports 2 updates with 128-term distinct saved provenance from three eligible pivots (600-character coefficient limit inventory: 3 qualify at >=128); the second update might trigger expression swell. The next bounded exploratory step is **128 terms, 2 sequential updates**, only after Windows tests succeed and with user monitoring of CPU/RAM/time. This remains no-write and does not execute protected Kira or exact source continuation:

```powershell
python -m examples.three_loop_vp05_exact_sequential_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --expected-sha256 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297 --terms 128 --max-chars 600 --rounds 2 > log_vp05_exact_sequential_probe_128x2.txt 2>&1
```

No built-in wall-clock timeout exists in this diagnostic; use an external timeout guard or manual monitoring, and preserve file input. After confirming multiple larger updates, the remaining crucial engineering stage is an isolated **real exact IBP source-row pivot-path replay** using the saved immutable input and identical pivot order, comparing both original and QQ(z,d) engines against exact source relations, before any opt-in production integration. Do not treat synthetic saved-pivot pairings as real IBP pivots.


### 2026-11-21 VP05 A Windows 128-term two-update exact field sequence PASS; original-IBP first-pivot read-only pilot introduced

The user uploaded UTF-16LE `log_vp05_exact_sequential_probe_128x2.txt` and the actual full line was read from the attachment. The emitted `VP05_EXACT_SEQUENTIAL_PROBE` reports **`EXACT_SEQUENCE_PASS_PROBE_ONLY`**, **two exact matches** against SymPy per-round exact rational cancellations:
- Round 1: 128 source terms → 133 output terms; baseline `sp.cancel` **5.345175 s** vs persistent QQ(z,d) update **0.224356 s**, independent symbolic equality check **0.390538 s**, `exact_pass=true`.
- Round 2: 128 source terms → 136 output terms; baseline **19.708178 s**, persistent field update **0.595092 s**, verification **1.084544 s**, `exact_pass=true`.
- One-time field conversion **1.041322 s**; baseline updates sum **25.053353 s**; field updates plus conversion **1.860770 s**, measured ratio **13.4630×**. Sum candidate with verification `1.860770 + 0.390538 + 1.084544 = 3.335852 s`, baseline-only/candidate-plus-verification ratio **7.5103×**. Full logged wall time **28.392305 s** is both comparison implementations plus verification/overhead, *not* the field-only run.
- Saved original A checkpoint SHA256 `90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`, **296/339**, `checkpoint_modified=false`, `production_engine_modified=false`, `target_A_proven=false`, `kira_executed=false`, **`real_original_ibp_path_replayed=false`**. No real full-path acceleration or A target identity proven; 43 original source rows remain.

To move beyond synthetically paired saved coefficients, added a **separate read-only first REAL original-IBP pivot step** pilot:
- `examples/three_loop_vp05_exact_real_first_pivot_probe.py`. Pinned SHA256 of *all three immutable files*: A 296-row checkpoint `90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`, exported `vp05_sector202_exact_source_rows.json.gz` `f0dd7f338ead97e455306bc49c4ce475fe8a8bee3e5a866f6fa17de1e9ad0163`, and original modular certificate `512114a669d3fb8761d89bfe11a51cc8ec146d46739a36b61e869edcddb583eb`. Validates A-only 339 selected original source IDs, the previously 296 source rows and source/selection SHA, refuses symlinks or unpinned inputs. Uses the exact **next real exported source row**, its actual initial leading coefficient and matching normalized saved pivot, compares the original `sp.cancel` sparse subtraction for both **row and provenance trace** with the isolated QQ(z,d) field subtraction. Exact row+trace equality is independently checked; then calls the existing engine `verify` to replay the **actual exported original IBP source equations** for the resulting (intermediate) row and original-source provenance. Reports old vs field timings and initial field/back conversion costs, keeps the saved checkpoint unchanged. Does not execute next rows or normalize/create a new saved pivot. Cannot claim complete original IBP path from a single first step; output states `real_original_ibp_path_steps=1` only and `target_A_proven=false`.
- `examples/test_three_loop_vp05_exact_real_first_pivot_probe.py`: 4 offline tests for exact pilot row+trace and source replay, independent rejection of fake provenance even if both arithmetic paths agree, pinned SHA rejection before JSON parsing, and symbolic-link guard. Windows PASS **not yet confirmed**; the script has **no built-in wall-clock limit**. If next real row initially has no matching saved leading pivot, the pilot **explicitly refuses** instead of manufacturing a pivot (this is a structural limitation, not a Target A proof/failure).
- The production `examples/three_loop_vp05_sector202_exact_support_checkpoint.py` module is **imported read-only**, not edited, and the pilot performs no checkpoint writes; source rows are read from existing protected exported file, no Kira.

Next Windows command, **after pulling and passing tests**, from repository root:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_exact_real_first_pivot_probe -v
python -m examples.three_loop_vp05_exact_real_first_pivot_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json > log_vp05_exact_real_first_pivot_probe.txt 2>&1
```
User should monitor RAM/time (no internal wall-clock timeout); if the pilot rejects an unmatched original leading pivot or fails exact replay, **do not** alter source hashes or saved checkpoint to force progress. Review and diagnose first. The first real pivot is a limited but meaningful advancement over the prior synthetic replay; further actual elimination steps, exact full-source replay, independently justified Target A zero remainder, sector C and VP05 63-master closure remain open.


### 2026-11-21 VP05 real-first-pivot pilot unittest Windows WinError 1314 — privileged symlink fixture only

Windows user ran `python -m unittest examples.test_three_loop_vp05_exact_real_first_pivot_probe -v`. **Four tests ran; only `test_symlink_is_refused` errored** before guard execution. The exact traceback is `checkpoint.symlink_to(original)` -> `OSError: [WinError 1314] クライアントは要求された特権を保有していません。` (missing symbolic-link creation privilege in Windows / Developer Mode). This is **not** an IBP or QED arithmetic error. The real first-pivot probe script has not yet been demonstrated to run successfully; no first-pivot equality, original-IBP replay, or Target A proof is claimed.

Changed **only the unittest fixture setup** in `examples/test_three_loop_vp05_exact_real_first_pivot_probe.py`: wrap `checkpoint.symlink_to(original)` with `try/except OSError`; use `self.skipTest` **only when `exc.winerror == 1314`**, and re-raise other OS errors. On systems able to create symlinks, the test continues and must verify the production pilot rejects a linked protected file. The real pilot's symlink guard and SHA-pinned source/checkpoint/certificate checks are **not weakened or changed**. This avoids requiring elevated PowerShell to run ordinary offline tests. The observed latest Windows suite result was 1 error, not a PASS; retest required.

Windows steps from repository root:

```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_exact_real_first_pivot_probe -v
```

Expected in this nonprivileged setup: **4 tests, 3 OK, 1 skipped**, overall `OK (skipped=1)`; if instead any error appears, inspect output. When tests are clean, run the **read-only real first original-IBP pivot comparison**:

```powershell
python -m examples.three_loop_vp05_exact_real_first_pivot_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json > log_vp05_exact_real_first_pivot_probe.txt 2>&1
```

The protected A checkpoint remains at 296/339 (SHA256 `90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297`), original exported source & provenance certificate are unchanged. This test is read-only but has no internal wall-clock timeout; do not confuse a skipped symlink fixture with the actual integrity check on production inputs.


### 2026-11-21 VP05 real original-source first pivot PASS; independent actual-order multi-pivot replay introduced

User uploaded `log_vp05_exact_real_first_pivot_probe(1).txt` and real Windows output `VP05_REAL_FIRST_PIVOT_FIELD_PROBE` reports `REAL_ORIGINAL_IBP_FIRST_PIVOT_EXACT_PASS_NOT_TARGET_PROOF`. Exported real IBP source original ID **2348**, pivot **[43447889166336,73]**, 4 source integral columns, 2 stored pivot columns, pivot original-source trace support 1, output 4 columns and trace support 2. Full exact symbolic `strict_exact_row_equal=true`, `strict_exact_trace_equal=true`, original exported IBP replay independently `original_ibp_source_replay_verified=true`. This is a real initial pivot rather than synthetic saved-trace pairing, but it is tiny: existing SymPy row+trace 0.000012s; field input conversion 0.000515s, field update 0.000132s, back-conversion 0.000073s, source replay and equality verification 0.001179s; no speed benefit at this first step. User's original A checkpoint SHA `90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297` remains 296/339, unchanged. No production engine change, target proof or Kira.

To evaluate more than this trivial first step, implemented **`examples/three_loop_vp05_exact_real_multistep_probe.py`** as a separate *read-only* actual-order diagnostic. It reuses the strict SHA-pinned checkpoint, exported source and certificate validation. Selects next real original source row ID2348, follows successive `min(row)` exact stored pivot leads in the saved basis (not synthetic multipliers), and keeps field row and trace as persistent `QQ(z,d)` fraction elements. Independently updates baseline via per-key SymPy `sp.cancel`. After **each genuine step**: checks full exact row and trace parity and replays the original exported IBP equations via the original engine's `verify`. Records per-step pivot, support, baseline vs field times, conversion and verification; cap 1..8 steps, default4. Stops on zero or no saved lead; never normalizes/adds a new pivot or saves checkpoint, never runs Kira. No built-in wall-clock timeout; monitor RAM/time. Output `VP05_REAL_ORIGINAL_IBP_MULTISTEP_FIELD_PROBE`, status `REAL_ORIGINAL_IBP_MULTISTEP_EXACT_PASS_NOT_TARGET_PROOF`. A complete exact source 339-row reduction, Target A proof, sector C and 63-master closure remain unresolved. 

Added `examples/test_three_loop_vp05_exact_real_multistep_probe.py` with four offline tests: two genuine shaped source-replay steps with exact parity, stopping on missing pivot, provenance tampering rejection, step-count guard. Windows tests **not yet observed**.

User Windows commands:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_exact_real_multistep_probe -v
python -m examples.three_loop_vp05_exact_real_multistep_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --max-steps 4 > log_vp05_exact_real_multistep_probe_4.txt 2>&1
```
Inspect the actual output before further expansion. The 4-step run may stop early on no matching saved lead; this is expected, not a proof failure. Guard all original protected files, and never run source-completion Kira or overwrite the pinned checkpoint as part of the pilot.


### 2026-11-21 VP05 A real IBP multistep 4/4 exact replay PASS; very small steps favor SymPy

User uploaded Windows UTF-16LE `log_vp05_exact_real_multistep_probe_4.txt`. Parsed `VP05_REAL_ORIGINAL_IBP_MULTISTEP_FIELD_PROBE` result `REAL_ORIGINAL_IBP_MULTISTEP_EXACT_PASS_NOT_TARGET_PROOF`: original exported source ID **2348**, requested/completed **4/4** *real stored-pivot* exact elimination steps, `stopped_because=max_steps`, next lead **[43448963563520,73]**. Every step has **strict exact integral-row equality, strict exact provenance equality and independent original exported IBP equation replay verified**. Pivots and support: step1 pivot [43447889166336,73], pivot trace support1, output trace2, output columns4; step2 pivot [43448963039234,73], pivot trace support3, output trace5, columns8; step3 pivot [43448963301378,73], pivot trace support6, output trace7, columns7; step4 pivot [43448963432448,73], pivot trace support4, output trace10, columns10. This is a real observed prefix of the original source pivot path, **not yet the complete original 2348 row**.

Actual timing over four very small steps: `total_baseline_s=0.003723` vs `total_field_conversion_plus_update_s=0.004334`, hence field route is **1.164× slower** here due to conversion overhead. Per-step baseline (s) [0.000012,0.001249,0.002429,0.000033], field internal updates [0.000168,0.000345,0.000665,0.000449]. This is consistent with large 128×128 synthetic-sequence benchmarks being favorable yet tiny actual pivots not favorable. Do **not** claim universal 13× improvement or immediate switch of production engine: crossover/support threshold and actual source-row pivot coefficients require separate evaluation. Pinned original A checkpoint SHA **90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297**, processed 296/339; no saved checkpoint or production engine modification, Target A not proven and no Kira.

Next safe diagnostic **already supported by committed read-only probe** is to extend this same real original 2348 row from 4 to **at most 8** pivot steps, while retaining full per-step symbolic equality + original-IBP replay, same checksum pin, no writes, and monitoring memory/time. This collects larger support crossover evidence but may still be small. If 8 steps remain tiny, do not continue endlessly with synthetic tiny measurements; develop a bounded read-only audit against the known heavy 2347 exact-path trace / previously saved records, or an opt-in copied scratch state with stringent equivalence and rollback guards. The existing standalone diagnostic has no internal timeout. Windows command after repository updates:

```powershell
python -m examples.three_loop_vp05_exact_real_multistep_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --max-steps 8 > log_vp05_exact_real_multistep_probe_8.txt 2>&1
```

The target-level exact identity, master C retention, and VP05 63-master closure remain open. Do not mutate the 296-source saved checkpoint based on this pilot.


### 2026-11-25 VP05 A actual IBP eight-step parity PASS; expand next read-only comparison to 64 steps

Actual attached Windows `log_vp05_exact_real_multistep_probe_8.txt` decoded and JSON inspected. Status `REAL_ORIGINAL_IBP_MULTISTEP_EXACT_PASS_NOT_TARGET_PROOF`, real original source ID2348, completed 8/8, next lead [45081051267072,137]. All 8 strict symbolic row/trace comparisons and literal original IBP replay verified. Output columns per step 4,8,7,10,8,9,31,33; trace support 2,5,7,10,10,11,12,14. Baseline updates 0.023314s, field updates with conversion and back-conversion 0.010831s, ratio 2.152525x. Per-step exact equality and original-source replay verification sum 0.114701s, excluded from arithmetic timing; additionally consumed saved-pivot replay and input parsing are not included. This is real pivot prefix, not full source row or full-run speed evidence. Original A 296/339 checkpoint unchanged with SHA256 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297; no production engine modification, Target A proof, or Kira.

Instead of more tiny increments, extended isolated real multistep probe to **64 maximum steps** (same next source row only), with flushed `VP05_REAL_PIVOT_BEGIN` and `VP05_REAL_PIVOT_VERIFIED` diagnostics so interrupted runs retain verified prefix evidence in stdout. No checkpoints written or resume within row; restarting recomputes prefix. Corrected terminal classification to report no_saved_pivot even when actual path ends exactly at cap; updated test and added extended-cap path-end test. Commits 381f01a and 1b2cf2a. Updated Windows tests not yet executed/confirmed. No internal wall-clock or memory limit; use external process timeout and monitor memory. Avoid concurrent production runs. The previous source ID2347 needed 52 steps, but ID2348 may differ; 64 is a diagnostic cap, not an assumed actual length. If row reaches new leading pivot, this is unnormalized row result only, not durable source completion. 

Windows:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_exact_real_multistep_probe -v
python -m examples.three_loop_vp05_exact_real_multistep_probe --checkpoint .\output\three_loop_integral_family_audit\vp05_sector202_A_339_exact_a339a_v1.json --max-steps 64 > log_vp05_exact_real_multistep_probe_64.txt 2>&1
```
Do not claim source position advanced or proof until separately normalized, replayed, and safely saved/audited. Next assess actual heavy path, then design opt-in isolated source continuation with per-row durable checkpoints rather than repetitive tiny synthetic runs.


### 2026-11-25 VP05 A real 64-step exact parity PASS; isolated resumable field continuation

User supplied log_vp05_exact_real_multistep_probe_64.txt. Parsed complete attached JSON: ID2348 64/64 strict row, trace and literal original IBP replay PASS; stopped at cap, next lead [166578161057792,139]. Peak 99 integral columns / 57 trace entries. SymPy update 3.188116s, persistent field including conversion/back conversion 0.573420s, ratio 5.559827x; independent comparison/replay 13.048857s excluded, as are saved-pivot verification and input load. Not full row completion or overall speedup. Protected A seed remains 296/339 SHA 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297; 43 rows remaining.

Implemented opt-in --experimental-field in exact support checkpoint engine, restricted to dedicated A fieldpilot filename in BASE, resume, per-row checkpoint, incompatible factoring/diagnostic modes refused. Default SymPy unchanged. Persistent field state holds row and provenance through actual pivot updates, returns SymPy views for existing expression caps, and requires eliminated lead to disappear. Existing normalization, independent original-IBP verify, resume replay and atomic per-row save remain unchanged. Combined row+trace timing recorded under row_subtract_s (source_subtract_s zero in field mode). Added examples/three_loop_vp05_a_field_pilot.py and run_vp05_a_field_pilot.bat: validates original source/certificate through existing preflight, pins a339a seed, exclusively copies it into fieldpilot scratch checkpoint, resumes scratch only, limits subprocess to 12h, checks durable progress and protected seed afterwards. Do not run concurrently; no cross-process lock or RAM guard is implemented, and abrupt termination during temp-file write may require manual review of .tmp rather than automatic deletion. Scratch output is not formally promoted. Added offline persistent two-update parity test; updated Windows tests not yet run here. Implementation commits 09703bb, d342867, accfe3d8, e42913a.

After pull, run:
```powershell
python -m unittest examples.test_three_loop_vp05_a_field_pilot examples.test_three_loop_vp05_exact_real_multistep_probe -v
.\run_vp05_a_field_pilot.bat --rows 43 --timeout-seconds 43200
```
Monitor RAM/swap and stop if needed. On ordinary timeout or interruption, re-run same batch to resume from verified durable row, unless .tmp or audit failure requires review. Existing checkpoint validation replays all saved pivots at startup. The scratch result must be independently audited before any promotion. Even 339/339 does not prove Target A reduction, C master retention or VP05 closure.


### 2026-11-25 VP05 A 339/339 source completion, independent resume replay, and exact target proof implementation

User supplied log(20261125-003359).txt: fieldpilot completed 296 -> 339/339, rank339, dependent0, exit0, no timeout, original checkpoint unchanged, target_A_proven=false. Completed fieldpilot SHA256 945547ba7e166d41932041d2ca34917c7dacf883b20765e7551d013a863ff755. Original 296-row SHA remains 90c81c6d418cd7c5abad30ec178429aea3075c83a54d874b457335baa985d297. User supplied log_vp05_a_fieldpilot_independent_audit.txt: resume_validation_complete, saved_processed339, saved_rank339, resume_elapsed_s2063.02 (34m23s). The existing nonexperimental SymPy resume validation replays all saved pivots against original exported IBP rows; this confirms source pivot replay, not target proof. Audit log does not independently print checkpoint SHA, so next program explicitly pins completed checkpoint hash.

Implemented separate examples/three_loop_vp05_a_fieldpilot_target_proof.py (e86788a), regression tests (1bc09c2), launcher run_vp05_a_fieldpilot_target_proof.bat (e4dbe1c). Existing union target program remains unchanged. Reuses its exact target definitions, candidate rational formulas, codec and original SymPy replay, validates completed A-only 339-row state and original source/certificate hashes, executes persistent QQ(z,d) target reduction with 339-step/256-column/339-support caps, requires zero remainder and successful original-source replay, writes exclusive proof-candidate JSON including original-source multipliers, target terms and SHA. No production promotion or VP05 closure claim; no Kira. The proof candidate is not yet executed on actual Windows inputs. Added four offline regression tests, not run here. No hard wall-clock/RAM or intermediate polynomial-size cap; monitor process. Interrupted proof run recomputes from beginning; no internal resume; existing output must not be overwritten. Next independently audit serialized proof candidate before formal promotion.

Windows:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_a_fieldpilot_target_proof -v
.\run_vp05_a_fieldpilot_target_proof.bat 2>&1 | Tee-Object -FilePath log_vp05_a_fieldpilot_target_proof.txt
```
Expected success tag VP05_A_TARGET_EXACT_PROOF, status VP05_A_EXACT_TARGET_PROOF_CANDIDATE, remainder_terms=0, original_ibp_replay_verified=true. Candidate output vp05_sector202_target_a_fieldpilot_exact_proof.json. On error preserve logs and all existing files; no forced promotion. Target C retention and full 63-master closure remain open.


### 2026-11-25 VP05 Target A exact zero remainder and original-IBP replay PASS; saved proof audit introduced

Windows log_vp05_a_fieldpilot_target_proof.txt decoded from uploaded UTF-16 file. VP05_A_EXACT_TARGET_PROOF_CANDIDATE: 70 actual target elimination steps, zero exact remainder, 339 nonzero original-source multipliers, original_ibp_replay_verified=true. Reduction 111.2398752s; independent SymPy replay 9.5281364s. Proof file vp05_sector202_target_a_fieldpilot_exact_proof.json SHA256 9393696362fb2e22c011e734fe92393d845ac0055d2f6a9a1114c8e21b308858. Completed checkpoint pinned SHA 945547ba7e166d41932041d2ca34917c7dacf883b20765e7551d013a863ff755. This establishes the reported exact Target A identity against exported original IBP equations; the serialized file itself has not yet been independently reread and audited. Formal promotion remains false; B unchanged, C retention and VP05 63-master closure remain open.

Added examples/three_loop_vp05_a_saved_proof_audit.py (93dce6b) and run_vp05_a_saved_proof_audit.bat (ca6cff2). Read-only: pins proof/checkpoint/source/certificate SHA, reconstructs target terms from existing definitions/formulas and codec, validates serialized target terms and all 339 distinct nonzero original multipliers against A support, performs independent original SymPy replay from disk, rechecks hashes. No elimination rerun or Kira. Not yet executed in Windows; no formal promotion. Run after pull:
```powershell
.\run_vp05_a_saved_proof_audit.bat 2>&1 | Tee-Object -FilePath log_vp05_a_saved_proof_audit.txt
```
Expected VP05_A_SAVED_PROOF_READ_ONLY_AUDIT_PASS. Actual proof file not available to assistant, only run log; local audit required before promotion. Preserve original files.


### 2026-11-25 VP05 A serialized proof independent audit PASS; confirmed proof archive preparation

User uploaded log_vp05_a_saved_proof_audit.txt, read directly as UTF-16. VP05_A_SAVED_PROOF_READ_ONLY_AUDIT_PASS; proof SHA256 9393696362fb2e22c011e734fe92393d845ac0055d2f6a9a1114c8e21b308858, completed checkpoint SHA256 945547ba7e166d41932041d2ca34917c7dacf883b20765e7551d013a863ff755, original_support=339, original_ibp_replay_verified=true, replay_s=9.399406600001385, files_modified=false. Target A exact identity and serialized proof replay complete. Formal promotion false and whole-family 63 closure false in actual log.

Added examples/three_loop_vp05_a_confirmed_archive.py (2c044fe) and run_vp05_a_confirmed_archive.bat (e994725). The script re-runs the pinned read-only proof audit, exclusively creates vp05_sector202_target_a_confirmed_v1 under the existing audit output directory, copies exact proof JSON (including all 339 source multipliers), verifies both hashes, saves a manifest including the audit result and source/checkpoint/certificate pins, reads back manifest and verifies archived proof hash. Original files and canonical registry not modified. This is a confirmed proof archive, not family promotion. Script not executed here; Windows output needed. No automatic overwrite or retry of an existing archive; incomplete directory after failure requires inspection, not deletion. No automatic timeout. Next command:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
.\run_vp05_a_confirmed_archive.bat 2>&1 | Tee-Object -FilePath log_vp05_a_confirmed_archive.txt
```
Expected VP05_A_CONFIRMED_ARCHIVE with status VP05_A_CONFIRMED_PROOF_ARCHIVE and proof/manifest SHA. Subsequent work: reconcile archived A and B evidence, establish C retention and sector202 closure, then complete standard Stage-2 and registry audit. Neither C retention nor VP05 63-master closure is established by this archive.


### 2026-11-25 VP05 A archive confirmed; C restricted-system retention diagnostic

User supplied log_vp05_a_confirmed_archive.txt: VP05_A_CONFIRMED_PROOF_ARCHIVE, proof SHA256 9393696362fb2e22c011e734fe92393d845ac0055d2f6a9a1114c8e21b308858, manifest SHA256 c4b285f0066160f0bf443ad2278b6e9dfe183fd033aa78bcbde078ddaf43529e, 339 original multipliers, registry_promotion_completed=false. A archived and independently replayed, B Step93 formal archive unchanged. No user backup/move/delete action required.

Implemented examples/three_loop_vp05_c_retention_probe.py (8b7c65c), regression tests (fb9114e) and run_vp05_c_retention_probe.bat (6c507ee). Pins confirmed A archive, replays existing A audit, checks B formal post-audit, uses original restricted project's own codec, all 2678 saved SYSTEM equations, three finite-field points, and rank increments for C alone and modulo opaque key (4,73). Records input SYSTEM hashes before/after; these are runtime inventory hashes, not previously pinned source equivalence. No Kira or writes. Finite-field rank increments alone do not prove generic rank upper bound or C independence over QQ(z,d). Need exact rank upper-bound/dependency certificate or exact annihilator witness, and independently address new r7s5d3 scope and whole-family closure. A/B identities are insufficient for this. M remains opaque, not a physically identified master. Tests added but not run here; Windows data unavailable. Run:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_c_retention_probe -v
.\run_vp05_c_retention_probe.bat 2>&1 | Tee-Object -FilePath log_vp05_c_retention_probe.txt
```
Expected VP05_C_RESTRICTED_RANK_DIAGNOSTIC_NOT_PROOF. No internal timeout or RAM guard; sparse fill cap 20000. Review all three results before choosing exact witness method; no canonical registry update.


### 2026-11-25 VP05 C full-row-rank diagnostic PASS; deterministic restricted independence certificate

User uploaded log_vp05_c_retention_probe.txt. Three regular-looking finite-field points (1000003,17,7), (1000033,19,11), (1000037,21,15), each 2678 SYSTEM rows, 2954 specialized columns, rank2678, C increment true, opaque M increment true, C increment modulo M true. Times 3.9405953, 3.9804316, 3.9369393 seconds. Fourteen SYSTEM files hashed in log. No Kira or writes. Unlike a general rank-increment diagnostic, the augmented matrix here has full row rank at specialization. A nonzero 2680-row minor at a verified regular specialization proves generic full row rank over QQ(z,d), with upper bound supplied by the number of rows, not probabilistic reconstruction. Thus restricted C/M independence can be certified without giant symbolic elimination. Still not a proof of independence modulo the entire 63 candidate basis or extended seed IBPs; opaque M identification and boundary equivalence remain open.

Added examples/three_loop_vp05_c_exact_rank_certificate.py (f6d52e7), tests (a7c5cdb) and launcher (3040013). Pins all fourteen original SYSTEM hashes from actual log, confirms C codec, independently evaluates literal coefficients as exact rational functions via QQ(z,d) numerator/denominator polynomial specialization, checks p-adic denominator regularity and cross-checks prior AST modular evaluator. Uses discovery-ordered pivot columns and pivot products to certify a nonzero augmented square minor, saves column order, residues, determinant, prime/point, source hashes, scope-limited exact ranks. No Kira or mutation of existing outputs; exclusive new certificate JSON. Windows tests and certificate run not observed yet. No timeout/RAM guard, sparse fill cap 20000. Output may not be overwritten. Run:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_c_exact_rank_certificate -v
.\run_vp05_c_exact_rank_certificate.bat 2>&1 | Tee-Object -FilePath log_vp05_c_exact_rank_certificate.txt
```
Expected VP05_C_RESTRICTED_EXACT_INDEPENDENCE_CERTIFICATE with nonzero determinant_mod_p and augmented_rank=2680. Independently audit saved certificate before using it as restricted evidence. No family promotion.


### 2026-11-25 VP05 C restricted exact rank certificate success status reported

User reports VP05_C_RESTRICTED_EXACT_INDEPENDENCE_CERTIFICATE from Windows execution. This is the success status of the pinned full-row-rank minor program: conditional on the reported run, exact ranks E=2678, E+M=2679, E+M+C=2680 over QQ(z,d), proving C independence modulo M in the original restricted SYSTEM only. Full console JSON, determinant residue, certificate SHA256 and actual certificate file have not yet been supplied; do not claim independent saved-certificate audit or formal promotion. Request existing log_vp05_c_exact_rank_certificate.txt (no recomputation needed). New boundary equivalence, opaque M physical identification, full 63-basis independence and Stage-2 closure remain open.


### 2026-11-25 VP05 C exact rank certificate full log received; independent fixed-minor audit

User supplied log_vp05_c_exact_rank_certificate.txt (UTF-16 read). VP05_C_COEFFICIENT_CHECK: 2678 rows, 21836 terms, all_regular_and_independently_equal=true. VP05_C_RESTRICTED_EXACT_INDEPENDENCE_CERTIFICATE: determinant_mod_p=937916 at pinned point (1000003,17,7), augmented_rank=2680, certificate SHA256 1ef90dbda58cff51f1e055c1908f71f422f3c2016e0b17b04a47d09cfffa9f5f. This certifies exact full row rank and C independence modulo opaque M for original restricted SYSTEM, conditional on saved certificate audit; not extended seed/full basis retention. A/B unchanged.

Added examples/three_loop_vp05_c_saved_rank_audit.py (d3c7a7a), launcher (d933628), tests (ef8b26c). Pins certificate and original SYSTEM hashes, reads all terms with existing regular-specialization cross-check, independently restricts rows to the saved ordered columns and performs fixed-column triangular elimination with a separate integer-index algorithm, verifies all 2680 pivot residues and determinant 937916, rechecks hashes. No new pivot selection, Kira, file mutation or family registration. Tests added but not executed here; local data unavailable. No automatic timeout. Next:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_c_saved_rank_audit -v
.\run_vp05_c_saved_rank_audit.bat 2>&1 | Tee-Object -FilePath log_vp05_c_saved_rank_audit.txt
```
Expected VP05_C_SAVED_EXACT_RANK_CERTIFICATE_AUDIT_PASS. Next reconcile A/B/C evidence against newer sector202 boundary scope before claiming closure; do not rerun large Kira without specific evidence gap.


### 2026-11-25 VP05 C saved exact rank audit PASS reported; ABC Stage-2 integration inventory

User reports VP05_C_SAVED_EXACT_RANK_CERTIFICATE_AUDIT_PASS. The status is emitted only after pinned saved certificate, all 2680 pivot residues, determinant residue 937916 and all 21836 original terms have been verified. Full audit JSON not supplied, so record user-reported PASS, not assistant independently executed audit. A and B confirmed archives and C restricted certificate are now available. No additional C calculation requested.

Added examples/three_loop_vp05_abc_stage2_scope_inventory.py (aaf213b) and launcher (6283ca9). Read-only inventory: pin A archive manifest/proof and C certificate hashes, reuse existing B formal archive post-audit and Stage-2 gap review, report candidate/closure coverage for A/B/C, existing standard and sector-local boundary evidence. No proof of expanded-seed equivalence or full closure, no mutation/promotion. Existing gap review is reused, no new regression test executed here. Need actual user's local output before selecting next boundary scope bridge. Execute:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
.\run_vp05_abc_stage2_scope_inventory.bat 2>&1 | Tee-Object -FilePath log_vp05_abc_stage2_scope_inventory.txt
```
Expected VP05_ABC_STAGE2_SCOPE_INVENTORY_NOT_CLOSURE. This is an evidence inventory, not another A/B/C proof computation. Note existing non202 batch evidence may live outside standard gap review filenames; inspect separately if missing. No automatic timeout or Kira.


### 2026-11-25 VP05 ABC inventory received; reconcile isolated sector evidence and review candidate independence

Actual log_vp05_abc_stage2_scope_inventory.txt: A/B/C are all present in both 63-candidate manifest and closure targets. 26 candidate sectors, 3 in sector202. Standard r9s5d2 stable 63 and sector-local 26-sector PASS; standard r8s6d2 and r8s5d3 both missing verified master lists, local standard aggregate audits absent, promotion_ready absent. Do not rerun r9s5d2. Crucial: restricted A/B exact relations use C and opaque M=(4,73); cannot automatically delete A/B or claim 61 or 63 independent physical masters without mapping M and confirming the source relations apply to the physical family. Restricted C independence modulo M does not establish independence modulo full candidate basis.

Added examples/three_loop_vp05_boundary_evidence_reconcile.py (ffcae8f) and launcher (b00d48b). Reuses verified first01, medium01, next01 and no202a isolated runs, merges their r8s5d3 local retention statuses with existing standard sector inventories, reports missing local evidence separately for two outstanding seeds. No Kira, no file writes, no closure pass. Raw codec decode of opaque weight4 is deliberately only a trial, not a physical identification. Next use actual remaining sector list and resolve M via authoritative source ID mapping/physical relation before choosing candidate revision and bounded new runs. Tests not run, local outputs unavailable.
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
.\run_vp05_boundary_evidence_reconcile.bat 2>&1 | Tee-Object -FilePath log_vp05_boundary_evidence_reconcile.txt
```
Expected VP05_BOUNDARY_EVIDENCE_RECONCILED_NOT_CLOSURE.


### 2026-11-25 VP05 remaining 202-free boundary batch

Actual log_vp05_boundary_evidence_reconcile.txt: local evidence counts r8s6d2 12/26 and r8s5d3 16/26; standard r9s5d2 26/26 previously. Missing r8s6d2: 202,203,204,205,206,207,228,229,230,231,234,237,238,239. Missing r8s5d3: 78,101,116,202,203,206,207,234,238,239. M weight4 decode failed (ppw 4 out of range (1 comps)); M remains opaque, no physical identity assignment. A/B/C archives unchanged.

Implemented examples/three_loop_vp05_remaining_safe_batch.py (2c46e0b, scope correction 5c38b05), run_vp05_remaining_safe_batch.bat (b0f2fab), scope tests (9f207fc). Exactly ten new isolated jobs: r8s5d3 sectors 78,101,116; r8s6d2 sectors 204,205,228,229,230,231,237. Sector238 excluded because (238 & 202)==202. All jobs are missing from prior local inventory, do not contain sector202, and exclude prior RAM-stopped 206/234. Effective r=min(8,popcount(sector)+d); scope is exact-sector diagnostic, not global closure. Existing monitor with sampled RAM warn/stop18/22 GiB, swap4/8 GiB, 5s interval, per-job5400s and batch scheduling budget12h. Budget is not a hard wall clock guarantee (preflight/preparation/termination overhead). Reopen SHA-pinned inputs, exclusive dirs, no overwrite. Reuse completed or preserve guard-stopped; interrupted or changed master sets require review. Windows integration/tests not executed here. No M mapping implementation in this change, and no promotion.

```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_remaining_safe_batch -v
.\run_vp05_remaining_safe_batch.bat run --hours 12 2>&1 | Tee-Object -FilePath log_vp05_remaining_safe_batch.txt
.\run_vp05_remaining_safe_batch.bat audit 2>&1 | Tee-Object -FilePath log_vp05_remaining_safe_audit.txt
```
Review actual audit before planning further jobs. Do not confuse local retention with full Stage-2 closure.


### 2026-11-25 VP05 remaining_safe01 actual execution: three local retained, seven RAM stops

Actual uploaded log_vp05_remaining_safe_batch.txt: all ten planned jobs attempted. r8s5d3: sector78 145.1s (1 candidate), 101 190.1s (2), 116 10.0s (1), all exit0 and exact candidate-set match in initiate-only master lists. r8s6d2: 204 625.8s last logged sector200, 205 660.8s last200, 228 635.8s last196, 229 560.8s last69, 230 620.8s last196, 231 555.7s last69, 237 630.8s last200; all RAM guard stop exit125, Kira -15, success=false. Sum monitored elapsed 4635.7s (77m15.7s), successful jobs 345.2s, stopped jobs 4290.5s. No family closure. Local evidence provisional totals r9s5d2 26/26, r8s5d3 19/26, r8s6d2 12/26 =57/78. Seven s6 failures cluster at logged subsectors 69,196,200 even without sector202; last logged progress does not prove exact internal cause. Do not rerun same jobs or increase RAM/swap caps. Preserve stopped directories. Need existing read-only audit log_vp05_remaining_safe_audit.txt, then inspect saved metrics, SYSTEM inventory and possible reusable subsector reductions, with scope equivalence checked. M mapping still unresolved. No new calculation implementation or closure claim in this entry.


### 2026-11-25 VP05 RAM guard visualization and stopped-job forensics

User supplied memory graph showing repeated rise and release, displayed configured maximum 30.00 GB and observed peak 21.92 GB. Consistent with seven RAM guard stops and sequential recovery in remaining_safe01 execution; graph alone does not identify allocation cause or guarantee absence of inter-sample overshoot. Keep existing 18/22 GiB RAM and 4/8 GiB swap warning/stop thresholds.

Implemented examples/three_loop_vp05_safe_stop_forensics.py (a23a896), launcher (8ff5293), grouping tests (dfdaa2b). Reopens all ten saved jobs via existing scope/status checks, verifies three retained and seven RAM-stopped jobs with observed last-sector IDs, reads metrics and bounded log tails, inventories partial SYSTEM and database metadata without decompression or Kira execution. Reports bitwise inclusion and possible effective exact-sector seed for logged subsector; not proof of cause, equivalence or reuse. No writes to existing outputs. This supersedes the previously requested standalone remaining_safe audit for this triage. No new Kira run yet; local regression tests and Windows actual audit not executed by assistant. Execute:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_safe_stop_forensics -v
.\run_vp05_safe_stop_forensics.bat 2>&1 | Tee-Object -FilePath log_vp05_safe_stop_forensics.txt
```
Expected VP05_SAFE_STOP_FORENSICS_READ_ONLY. Use actual partial SYSTEM availability and log phases to choose next computational approach; do not assume last logged subsector is exact allocation source. M identity remains unresolved.


### 2026-11-25 remaining_safe01 saved-state audit received

User supplied log_vp05_remaining_safe_audit.txt, status VP05_REMAINING_SAFE_AUDIT_NOT_CLOSURE. All ten saved job states agree with execution log: r8s5d3 sectors 78,101,116 completed_local_retained (four candidate integrals total); r8s6d2 sectors 204,205,228,229,230,231,237 guard_stopped, reason ram_stop, Kira returncode -15, success=false, unchanged last logged sector groups 200/196/69. Saved input manifests and candidate lists passed existing status checks. No rerun of these jobs needed for inventory. This is the earlier standalone audit, NOT log_vp05_safe_stop_forensics.txt; it does not contain partial SYSTEM inventory, bounded Kira log tails or resource peak data. The already committed safe-stop forensics launcher is the next operation, read-only, no new Kira. No new mathematical closure or promotion.


### 2026-11-25 VP05 stopped-job forensics received; isolated subsector generation pilot

Actual log_vp05_safe_stop_forensics.txt: all ten states verified; stopped seven show recursive equation selection/generation, no saved SYSTEM gzip files or masters, DB 28672 bytes each. RAM peaks 22.02,22.16,22.12,22.02,22.08,22.17,22.08 GiB; sampled swap peak zero. Last logged sectors 69 (229,231),196 (228,230),200 (204,205,237), all bitwise subsectors of corresponding parent; not proof of direct allocation cause. All three have three positive lines and proposed local seed r5s6d2. No rerun of parent jobs.

Added examples/three_loop_vp05_subsector_pilot.py (f3bd29c), launcher (58d58ce), tests (6eafa3b). Three isolated r5s6d2 projects with recursive selection explicitly set to local top sector, initiate-only solver. Plain variant first, optional trunc2 variant only after guard stop and if old saved q.P/jobs.yaml contains uniquely confirmed scalar truncate_sp: 2 at six-space indentation. Historical actual YAML not accessible here; unsupported layout blocks truncation and is reported, not guessed. Not a direct extraction of all original IBP rows: initiate-only may produce master list but no SYSTEM gzip; actual output inventory determines subsequent export plan. Each project hashes input files and preserves existing outputs; completed/guard-stopped skipped, interrupted/unexpected failure requires review. 18/22 GiB RAM, 4/8 GiB swap, 5s interval, 5400s per job, 12h scheduling budget; preparation/termination overhead can exceed budget slightly. No whole-family or parent-scope equivalence, no registry change, no M mapping. Tests added but not executed here; Windows Kira execution unverified.
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_subsector_pilot -v
.\run_vp05_subsector_pilot.bat run --hours 12 2>&1 | Tee-Object -FilePath log_vp05_subsector_pilot.txt
```
Expected VP05_SUBSECTOR_PILOT_NOT_CLOSURE; inspect actual per-job state, setting blocker, and saved equation/master inventory. Audit mode available without Kira.


### 2026-11-25 VP05 isolated plain generation failed; documented truncate_sp pilot

Actual log_vp05_subsector_pilot.txt: plain sector69 565.8s peak22.01GiB, sector196 655.9s peak22.08GiB, sector200 645.9s peak22.11GiB, all RAM stops Kira -15, swap0, no SYSTEM/master files. Total1867.6s. All three trunc2 skipped because old scalar-setting assumption failed, not because truncated Kira failed. Kira 3 paper arXiv:2505.20197 documents truncate_sp list entries with topologies and integer l and discourages recursive mandatory selection with truncation. Use documented syntax, not assumed historical scalar. Added examples/three_loop_vp05_subsector_truncate_batch.py (8156e2b), launcher dcedbdc, tests d47c5ff. New isolated projects, explicit ten scalar/dot targets per sector, r5s6d2 seed, l=2,0,-2 in sequence, weaker truncation only after successful previous run; preserve/skip guard-stopped, unexpected stop fails closed. No numerator target coverage, no parent equivalence or closure, no guarantee of SYSTEM export. Same monitor thresholds and scheduling limits. Windows tests not executed here. Original plain projects preserved. Run:
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_subsector_truncate_batch -v
.\run_vp05_subsector_truncate_batch.bat run --hours 12 2>&1 | Tee-Object -FilePath log_vp05_subsector_truncate_batch.txt
```
Expected VP05_SUBSECTOR_TRUNCATE_DIAGNOSTIC_NOT_CLOSURE. Inspect actual results before extending targets.


### 2026-11-25 VP05 independent IBP actual pilot and compact checkpoint engine

Actual log_vp05_subsector_truncate_batch.txt: all l=2 jobs RAM stopped, no SYSTEM/master output, 565.8/630.8/630.8s, peaks22.01/22.06/22.12 GiB, swap0. Independent generator implemented 910212d, launcher 3b4187c, tests 54c9028, guard aaeaece. Actual log_vp05_independent_ibp.txt confirms propagator inversion and 180 derivative comparisons, kernel SHA 09244783a9ce300ffbdd6b3e4c0f9eb216295eda9f7237b5c8e6ed513c85624b. Eight completed independent shells, Completed rows 18000 (=24750-6750); attempted 23178 (=18000+5178), last attempted row may not have completed both points. Earlier response incorrectly stated 19500 completed. Sector69 ranks 127/959/4363; 196 ranks127/987, s2 stopped at attempted row5178 due to stored term cap; 200 ranks127/987/4553. Both points agree for completed shells. No measured RAM peak or time in this log. Shells independent, not cumulative rank or exact closure.

Compact engine c4ef2b0, launcher fc38e9c, tests 2007fb7. Collision-free packed integer key (12 five-bit exponents with static sector population/r/s complexity prefix); harder-first pivot ordering, one evaluation point at a time, per-point 1.5M stored terms and 20k fill cap; previous 500k cap per point was simultaneous two-point engine. Separate output vp05_independent_ibp_compact02, kernel pin, checksummed row-cursor/pivot checkpoints every1000 rows and on handled stop. Host available RAM guard unchanged, sampled host used RAM peak and elapsed time logged. Benchmark s2 all three, compare known ranks, advance each successful sector up to s6; stop blocked sector and continue others. Checkpoint checksum is integrity not mathematical proof; resume validates structure, not full source replay. Abrupt termination may leave lock or tmp, requiring review. No Kira, no exact closure, no symmetry/LI/zero-sector proof, no cross-shell union. Tests added but not run here. 
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_compact_ibp -v
.\run_vp05_compact_ibp.bat --smax 6 --hours 12 2>&1 | Tee-Object -FilePath log_vp05_compact_ibp.txt
```
Expected VP05_COMPACT_IBP_NOT_CLOSURE. Review actual rank and fill before further expansion.


### 2026-11-25 VP05 compact02 measured results and adaptive03 continuation

Actual log_vp05_compact_ibp.txt: s2 six point jobs complete, both points ranks 4363/4553/4553 for sectors69/196/200 respectively. Point0 stored terms 177515/371514/179835; vs old completed 293491/368506 for69/200, reductions39.5%/51.2%, sector196 old incomplete. s3 point0 partial cursor/rank/terms: 69 21334/13752/1499224; 196 11093/8646/1499479; 200 17952/13222/1499810. All stopped by stored term cap, total50379 completed rows preserved, max sampled host used RAM12.084465GiB, not process-only RSS. No measured swap from this run. s3 point1 not begun. No closure.

Adaptive03 engine 42481bc, launcher 6fcfef6, tests fb01c19. Separate directory, original compact02 read-only, same kernel/point/row order/pivot order. Legacy checksum and structure validated and s2/s3 actual observed cursor/rank/terms checked; migration to streaming per-pivot line checkpoint with checksum. Initial cap5M, growth1M to max12M conditional on >=10GiB available RAM and heuristic 256bytes/term allowance above 8GiB reserve. Retain host available8GiB guard; sampled/heuristic, not hard process memory cap. Fill cap remains20k. Save every5000 rows and handled stop; checkpoint serialization avoids whole JSON copies. Legacy load still reads old JSON whole once. Atomic replacement of adaptive checkpoint only; stale temporary/lock requires review. No full mathematical source replay, no cumulative-shell reduction/closure. Added tests not executed in assistant environment; Windows runtime unverified.
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_adaptive_ibp -v
.\run_vp05_adaptive_ibp.bat --smax 6 --hours 12 2>&1 | Tee-Object -FilePath log_vp05_adaptive_ibp.txt
```
Expected VP05_ADAPTIVE_IBP_NOT_CLOSURE; verify migration log and actual resource/term behavior.


### 2026-11-25 adaptive03 actual results and packed04 continuation

Actual log_vp05_adaptive_ibp.txt: all six s2 and three partial s3 migrations succeeded. All six s3 jobs complete, ranks 15115/15908/15908 for 69/196/200 at both points. s4 point0 stops at 12M term cap: sector69 cursor64998 rank40049 terms11996933 elapsed6158.05s; 196 cursor32813 rank25011 terms11998825 elapsed3276.81s; 200 cursor51110 rank37145 terms11999831 elapsed4132.30s. Total148921 completed rows, 66.86% of three point0 shells; point1 not begun. Max sampled Windows host RAM used13.595GiB. No exact rank or parent closure.

Packed04 implementation f6437b9, launcher a33b7dc, tests 4b87120. Preserve adaptive03 and all earlier outputs. Same field points, row order, static integral ordering, normalization and reduction. Original packed complexity keys exceed 64 bits; use interned uint32 IDs (full original keys retained in mapping) and uint32 coefficients, 8 bytes per fixed pivot term excluding metadata. Working row remains dict of original keys. Read old streamed JSON one row at a time, check SHA/count/observed s4 cursor/rank/terms, migrate to separate packed04 binary checkpoint with SHA256, little-endian arrays, atomic replacement. 60M term cap (not dynamically growing), 20k working fill cap unchanged, existing available RAM 8GiB guard, extra checks every256 elimination steps, 2GiB disk reserve plus checkpoint estimate. Save every5000 rows or 300s at row boundaries and handled stops. 12h budget sampled, checkpoint IO can exceed deadline. Start s4, preserve completed s2/s3 rather than duplicate; proceed to s6 per successful sector. No full source replay, symmetry/LI or cumulative rank closure. New tests compare old/new elimination on deterministic synthetic rows and binary roundtrip/corruption; tests not run in assistant environment, Windows performance unmeasured. Compression may trade CPU time for RAM.
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_packed_ibp -v
.\run_vp05_packed_ibp.bat --smax 6 --hours 12 2>&1 | Tee-Object -FilePath log_vp05_packed_ibp.txt
```
Expected VP05_PACKED_IBP_NOT_CLOSURE. Original checkpoints untouched; stale locks/temp require review.


## 2026-11-26 — Session handoff: packed04 time-budget stop; next native finite-field engine

### Canonical branch and working rules
- Repository Sanaxen/QEDCalc, branch feature/master-basis-initiate-only. This file is the canonical worklog. Treat implementation, verification, git commit(s), and worklog update as one work unit. Preserve existing mathematical evidence and completed checkpoints; no destructive reruns or manual file copying by user. Prefer a dedicated BAT invoked from Windows PowerShell, with bounded, resumable execution and captured log.
- Overall objective remains analytic three-loop QED vertex calculation from the diagrams, not adoption of an unexplained published answer. VP05 is still in Stage-2 special lightweight calculations / preparation for standard Stage-2 integration, not registered as a final master basis. The canonical 63-candidate inventory remains unchanged. Last reconciled local evidence: r9s5d2 26/26, r8s6d2 12/26, r8s5d3 19/26, total57/78. Restricted sector202 A/B exact identities and C restricted rank proof are preserved; B Step93 proof archive and original exact coefficients must not be modified. A/B/C scope and opaque M mapping limitations remain. Do not infer a 61-master basis or global closure from those restricted identities.

### Actual packed04 final log (log_vp05_packed_ibp.txt, 2026-11-26)
- Implementation f6437b930c145bd64bed541a90c91ab442d19ffd, launcher a33b7dc19c377e4aa214c197b10d0d78c89ecaa4, tests 4b87120994adb3a44d794a2b9185eb6c03c91563, preceding worklog commit 9e162f4714e419b43b717844e420f459ee684d2b.
- Final status VP05_PACKED_IBP_NOT_CLOSURE, blocked_sectors=[196], reason Time budget, not RAM/term/fill stop. No actual checkpoint bytes inspected remotely; saved-state validity is to be checked from the user's local files by the new program before migration. User reports run progressed normally.
- Sector69 s4 point0: 74250/74250, rank43732, terms15365823, payload122926584 bytes, peak host RAM13.5950393677 GiB, cumulative elapsed9093.1879338s. Point1: 74250/74250, rank43732, terms15368744, payload122949952 bytes, peak12.7088775635 GiB, elapsed10259.4565042s. Both points complete and equal rank.
- Sector196 s4 point0: 73949/74250, rank46175 (partial), terms37179224, payload297433792 bytes, peak13.3919677734 GiB, cumulative elapsed33127.7468104s, complete=false; only301 rows remain. Point1 not started. Sector200 s4 point0 still in adaptive03, cursor51110, rank37145, terms11999831; point1 not started. s5/s6 not started. Earlier s0–s3 complete at both points for all three sectors (independent shell ranks; 69:127/959/4363/15115; 196 and200:127/987/4553/15908).
- packed04 directory output/vp05_independent_ibp_packed04 contains sec69_s4_p0.bin, sec69_s4_p1.bin, sec196_s4_p0.bin as expected by code; actual files need local validation. Sector200 legacy checkpoint expected output/vp05_independent_ibp_adaptive03/sec200_s4_p0.stream. Original pilot01/compact02/adaptive03/packed04 artifacts are read-only inputs for subsequent engine. s4 completed + partial cursors total273559/445500 point-rows (61.4%), including adaptive03 sector200. No final ranks for sector196/200 s4.
- Time values for migrated point0 jobs include earlier runs (not fresh native benchmark). Host RAM values are sampled system-wide Windows cumulative maxima, some inherited from earlier runs; not Python RSS. No swap measurement for packed04. The arrays hold 8 bytes/term excluding key maps, row overhead and active working row. Current packed term cap60M and active-row fill cap20k. Previous stop was time, not cap. RAM pressure markedly improved; CPU elimination is the next optimization candidate, not yet profiled.
- Current kernel SHA256 09244783a9ce300ffbdd6b3e4c0f9eb216295eda9f7237b5c8e6ed513c85624b, field points (1000003,17,7), (1000033,19,11), tuples (prime,z,d). Row generation: exact shell s, r<=5 (3 positive lines, up to2 dots), all9 other exponents nonpositive, 15 IBPs per seed. One shell at a time, not cumulative row space. Source examples/three_loop_vp05_independent_ibp.py; ordering/key/rows in examples/three_loop_vp05_compact_ibp.py; legacy stream in examples/three_loop_vp05_adaptive_ibp.py; packed state in examples/three_loop_vp05_packed_ibp.py.
- Packed binary format: MAGIC b"VP05PACK4\n", JSON header newline (meta/cursor/rank/terms/keys/peak/elapsed), full integral keys as 10-byte little-endian integers, each pivot record <III (source row index, leading interned ID, length), uint32 little-endian ID array then uint32 coefficient array, final raw SHA256 digest of preceding bytes. Full keys are up to 76 bits (not uint64); order is max of full key with t/r/s prefix +12 five-bit exponents. Interned IDs are insertion order, NOT complexity order. Normalized leading coefficient1. Preserve row order, point, seed, pivot order, source indices. Completed checkpoints and checksums do not prove exact source identities.

### User-confirmed development environment (2026-11-26)
- Windows 11 + WSL2 Ubuntu, existing Python/SymPy on Windows, Kira 3.1/Fermat on WSL, existing memory constraints unchanged. User actually ran `wsl g++ --version` and reported: g++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0. No Visual Studio/MSVC needed; no apt installation required. User had initially tried sudo apt update in the wrong shell; this is resolved by g++ confirmation. Do not request installation or version again unless build demonstrates a specific missing dependency.
- Agreed direction: use existing WSL2 GCC C++ directly, not Numba-first, for the finite-field sparse elimination hot loop only. Python retains exact IBP generation, orchestration, validation and checkpoint handling. Do not rewrite all QEDCalc. No C++ implementation or benchmark yet; next session begins here. Do not claim speedup without measurements.

### Next work sequence (implementation pending)
1. Read current packed04 code and this worklog. Profile/benchmark representative existing Python elimination using a bounded, read-only clone of the sector196 s4 point0 checkpoint (cursor73949), and/or a tractable representative subset. Preserve the production checkpoint. Verify its SHA256, expected cursor/rank/terms and exact field/scope before use. Ensure no simultaneous native or old run.
2. Implement a small standard-library C++ executable compiled by the existing Ubuntu g++ (e.g. -O3, fixed C++ standard); dedicated BAT can invoke WSL build/benchmark/run. Avoid per-row Windows/WSL process launches or roundtrips. Use a bounded binary batch/stream interface, and persistent native state within each batch. Do not assume a Linux .so can be loaded directly into Windows Python. Prefer existing checkpoint compatibility through verified import/export; separate new output directory. Full key comparison must preserve original >64-bit order (e.g. unsigned __int128 in GCC or high/low pair, or a verified order-preserving mapping); uint32 interning IDs alone cannot be used for max-pivot order. Modular multiplication needs sufficiently wide intermediate (uint64 for current ~1M primes); normalize coefficients modulo prime. Keep exact same source rows, row cursor and selected source indices in the initial comparison. Preserve all completed results.
3. Add tests and run them: synthetic sparse rows including cancellation, dependent rows, >64-bit keys/order, modular arithmetic, binary I/O and corruption, timeout/resume, plus representative actual IBP rows with identical leading key, normalized coefficients, selected indices, rank and term count after each accepted row (not merely final rank). Compare Python and C++ on the SAME initial state and row batch, record elapsed and RAM/CPU, exclude compilation and import overhead or separately report them, and also report end-to-end cost. Only switch production if equivalence passes and measured performance justifies it. If unable to run the user's WSL environment from chat, say so and supply a dedicated local test/benchmark BAT.
4. For native WSL execution retain previous conservative WSL guard (RAM warn18/stop22 GiB, swap warn4/stop8 GiB, sampled monitor) and Windows available physical RAM reserve8GiB where applicable; enforce bounded term/fill limits, disk reserve and 12h budget, interruption-safe atomic checkpoints and exclusive run locks. Check actual monitor compatibility with native executable; do not blindly reuse Kira-specific process/log parsing. Guard stop must not promote incomplete artifacts. Checkpoint validation and migration must be non-destructive. Do not increase resource limits simply because native code is faster.
5. After verification, resume sector196 s4 point0 from73949, finish301 remaining rows; evaluate point1, then migrate sector200 s4 point0 from51110 and complete both points. Preserve sector69 s4 both complete. Continue s5/s6 in resumable bounded jobs only after comparison and resource evidence. Expected target still s6, but avoid spending days on rank-only calculations without testing their usefulness to Stage-2. Exact-shell finite-field ranks alone cannot establish cumulative row-space, target reduction, parent equivalence, symmetry/LI/zero-sector relations, generic rational identities, or canonical master basis. Plan target-oriented/cumulative reduction and exact certificates/coverage comparison against original Kira seed scope before claiming any closure. No registry promotion.
6. Commit code, actual verification results and updated worklog; give user one clear BAT launch and log capture. Until new engine is verified, the old packed04 command remains available as fallback (do not ask user to run it now unless explicitly needed). No background work promised.



### 2026-11-26 — Native finite-field benchmark phase 1

Implemented benchmark-only GCC C++17 reducer (7c7ef39; sampled WSL RAM/swap 6f067f1), Python comparison driver (9d96186; Windows guard bba4d66; scoped interruption cleanup dc89192), launcher 6f7d5c1. Uses full unsigned __int128 keys, ordered working row and immutable native pivot vectors, uint64 modular products; native state persists for a batch. Python validates packed04 checksum/structure and exact observed sector196 s4 p0 cursor73949/rank46175/terms37179224, pins kernel and point, exports identical rows, compares normalized coefficients (including lead), rank and term count after every source row, checks original SHA before/after. Synthetic dependent/cancellation/>64-bit and truncated-input checks run before actual benchmark. Default 64 consecutive remaining rows, max301; 25min reduction budget each side, sampled WSL18/22 GiB RAM and4/8 GiB swap warning/stop, Windows existing memory guard during native process, separate temporary directory and exclusive benchmark lock. No production checkpoint writes or promotion. Benchmark transport duplicates the pivot data (14 bytes per serialized term; native vector allocation larger); deliberately not the final optimized packed native storage. Reports compile/export/native process/reduction durations and sampled system memory, not exact CPU/RSS. Source indices implicit in batch order; no production resume yet. Stop old engines before benchmark; locks checked but not a cross-engine mutual exclusion mechanism. Local Windows/WSL execution and tests not run by assistant: container cannot resolve GitHub; no access to user checkpoint. First local execution performs build, synthetic tests, actual comparison; speedup unknown. On failure preserve original inputs, inspect log, do not promote. 
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
.\run_vp05_native_benchmark.bat 2>&1 | Tee-Object -FilePath log_vp05_native_benchmark.txt
```
Expected VP05_NATIVE_BENCHMARK_PASS_NOT_CLOSURE with synthetic_only=false. Next review actual comparison, optimize native representation if necessary, then build verified resumable native production path; no Stage-2 closure claim.

### 2026-11-26 — Native benchmark WSL path fix

User actual launch failed before compilation: wslpath received C:UsersyamatoDesktopQEDCalcexamplesvp05_native_benchmark.cpp (backslashes stripped by WSL shell). Fix abeaadf: Path.resolve().as_posix() for Windows path conversion, explicit wsl --exec for wslpath, GCC, native execution, malformed-input test and scoped pkill; adjusted executable argument index in cleanup. No production calculation occurred in failed run. Windows/WSL retest pending; run original benchmark BAT again after git pull. No closure or performance claim.

### 2026-11-26 — Actual native benchmark PASS

User supplied log_vp05_native_benchmark.txt. Build 3.7052826s; synthetic 5/5 rows equal, rank3 terms5, intentional truncated-input negative test rejected (PowerShell NativeCommandError is expected stderr; benchmark continued). Real sector196 s4 p0 64/64 rows equal, rank46194 terms37221447; Python reduce127.4756957s, native reduce+output10.997532265s, native process28.0555223s, export11.0403637s. Ratios 11.59x reduction, 4.54x process, 3.26x including export (excluding build/checkpoint validation). Sampled WSL peak2.178684GiB, swap0, Windows peak15.992386GiB. Final VP05_NATIVE_BENCHMARK_PASS_NOT_CLOSURE synthetic_only=false production_modified=false. Original packed04 cursor73949 remains unchanged; benchmark results not promoted. Next implement bounded resumable native production engine with verified import/export, atomic checkpoint and separate directory; first finish remaining301 sector196 rows, then point1 and sector200. Avoid repeated full pivot serialization, maintain original ordering and resource guards. No extrapolation of measured speedup to entire Stage-2, no closure claim. Native production not implemented yet.

### 2026-11-26 — Native05 production pilot: finish sector196 s4 p0

Implemented transactional driver 40e3eed, launcher adf56a0, import/corruption tests 36b35ac; negative-test stderr corrected 67a2c2e. Reuses measured C++ reducer unchanged. Scope deliberately restricted to remaining301 rows of sector196 s4 p0. Source packed04 read-only, SHA pinned, observed cursor/rank/terms checked. Separate native05 packed-format checkpoint with distinct metadata; complete batch output parsed and checked for key/leading coefficient/count/rank/terms and known 64-row endpoint (cursor74013 rank46194 terms37221447), saved atomically and reopened with packed loader. This is structural/count validation, not independent coefficient replay of all301 rows. Default one batch301 rows to avoid repeated transfer; optional --batch-rows and --max-batches allow bounded transaction/resume tests. Interrupted batch is recomputed, previous saved batches preserved; abrupt kill during write may leave stale tmp/lock requiring review. 25min native executable guard, Windows available RAM reserve, WSL18/22GiB RAM and4/8GiB swap, existing cap60M/fill20k and 4GiB free disk preflight; 12h scheduling budget not hard bound on all IO/validation. Native pivot representation is unchanged, not yet persistent across batches; no point1/sector200/s5/s6 scheduling in this pilot. Tests committed but not executed in user environment or assistant; actual execution pending. No family closure or registry promotion.
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_native_production -v
.\\run_vp05_native_production.bat 2>&1 | Tee-Object -FilePath log_vp05_native_production.txt
```
Expected VP05_NATIVE_PRODUCTION_COMPLETE_NOT_CLOSURE rows74250 source_unchanged=true after saved-state reload. Review actual rank, resource/time and checkpoint before expanding scope.

### 2026-11-26 — Native05 production pilot actual completion

User supplied log_vp05_native_production.txt: original cursor73949 rank46175 terms37179224 SHA256 81b6cdc7cdc770bcd49150925378bc09b25aa65c0cd04061968d32b0939655bd; synthetic 5/5 equal and VP05_NATIVE_NEGATIVE_TEST_PASS; remaining301 rows completed in one batch. Saved cursor74250 rank46280 terms37355607, native reduction+output48.857669437s, reported batch elapsed74.380829s (before checkpoint save, not entire wall clock), sampled WSL RAM2.177257538GiB swap0, Windows peak16.239471436GiB. Final VP05_NATIVE_PRODUCTION_COMPLETE_NOT_CLOSURE rows74250 expected74250 source_unchanged=true after structural/checksum reload. No separate unittest output supplied; no independent coefficient replay of all301 rows. Point0 complete only; point1 rank comparison pending. Native05 checkpoint must be preserved, not overwritten. Next implement persistent or larger bounded native batches with resumable atomic storage for sector196 point1 and sector200 both points; validate point0 rank46280 against point1, retain sector69 completed pair. No closure or registry promotion.

### 2026-11-26 — Native06 sequential s4 continuation

Implemented native06 C++ bounded batch variant 9920b7b (same reduction logic, batch cap 5000), driver 4ce35db, launcher 957068b, tests b49f1b5. Sequential jobs (196,p1), (200,p0 from adaptive03 cursor51110 rank37145 terms11999831), (200,p1). Completed sector69 pair and native05 sector196 p0 structurally reloaded and matched to actual recorded counts; native05 original source SHA pinned. Separate native06 directory, source digest in checkpoint metadata, atomic packed checkpoints per successful batch, original checkpoints read-only. Default 2000 rows/batch, configurable 64..5000; if successful native batch exceeds900s, halve subsequent batch size within same job. Existing 25min native guard and 12h overall scheduling budget; bounded but not hard wall clock limit for all IO. Interrupted/failed batch is not saved; previously committed batches retained. On native failure inspect logs before retrying with smaller batch; no automatic retry on unexplained failure. Native process retains pivots within a batch only, full pivot export/import per batch remains. Both primes supported in result parser, fresh-point first64 compared with Python; known point0 rank46280 required at sector196 p1 completion, both sector200 ranks must agree. Structural result checks, not full coefficient replay; no exact closure. Existing caps 60M terms, 20k active fill, 18/22GiB WSL RAM and 4/8GiB swap, Windows reserve, 4GiB disk preflight unchanged. Tests committed, not executed here; Windows/WSL integration pending. Scope is s4 only; do not start s5/s6 before review of actual resource/term evidence and utility for Stage-2.
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_native_batch -v
.\\run_vp05_native_batch.bat --hours 12 2>&1 | Tee-Object -FilePath log_vp05_native_batch.txt
```
Expected VP05_NATIVE06_S4_COMPLETE_NOT_CLOSURE or VP05_NATIVE06_PAUSED_NOT_CLOSURE; resume same command after normal budget stop, inspect stale locks/tmp or unexpected failure first. No registry promotion.

### 2026-11-26 — Native06 s4 actual completion; target-oriented stage ②-8a

User log log_vp05_native_batch.txt confirms 171640 additional source rows and final VP05_NATIVE06_S4_COMPLETE_NOT_CLOSURE, s4_complete=true, prior_unchanged=true. All six s4 points complete (445500 rows). Sector69 ranks43732/43732 terms15365823/15368744; 196 ranks46280/46280 terms37355607/37361354; 200 ranks46280/46280 terms18828945/18830204. Native06 batch elapsed before save sums: 196 p1 3635.9906744s, 200 p0 remaining802.4854285s, 200 p1 1284.4217999s; aggregate5722.8979028s excluding checkpoint saves, compilation/preflight/final audit. Sampled max WSL RAM2.2181778GiB, swap0, Windows RAM16.0832596GiB. First64 fresh rows matched Python at both point1 jobs. Existing source files unchanged per actual log; no remote bytes inspected. Local evidence 57/78 remains, no family closure.

Progress tracking agreed with user: ②-1 sector-local candidates; ②-2 sector203 limited exact; ②-3 sector202 limited exact; ②-4 non202 boundary verification incomplete until ②-10; ②-5 investigate Kira RAM; ②-6 independent IBP/native speedup; ②-7 s4 now complete; ②-8 necessary s5/s6 evaluation and computation; ②-9 target-oriented reduction and exact certificates; ②-10 fill parent/boundary gaps and opaque M identity (finish ②-4); ②-11 audit handoff to standard Stage-2 ③. No assertion of 63 final masters; no registry change.

New ②-8a target reuse probe a1f1d71, launcher d35bd32, tests d7da073. Read-only: reload all six s4 checkpoints with actual rank/term/cursor checks; load existing s2/s3 packed-from-stream relations, regenerate small s0/s1 pivot stores with known rank check, use actual standard manifest candidate/closure targets in exact sectors69/196/200 plus ten scalar/dot diagnostics each. Substitute highest integral using first available shell pivot (s0 first) then retain free terms; bounded2M term operations per target (sampled at pivot boundaries), fill20k and one-hour probe budget, host RAM guard. Reports target labels, direct pivot shells, remainder degree/sector, support and coefficient hashes per point, bounded sample of degree4..7 frontier, and two-point support comparison. Nonzero remainder is not irreducibility; independent shell pivots have not been merged into full cumulative echelon basis. Parent bitwise ancestry is not scope equivalence. No s5/s6 rows computed and no proof promotion. Existing outputs preserved. Tests added but not executed here; user environment verification pending. Review actual target and remainder evidence before selecting ②-8b/8c s5/s6 computation, including needed parent-induced targets not present in exact-sector manifest, cumulative rowspace dependencies and capacity. C++ persistent state optimization deferred until target scope established. No blanket full s5/s6 run yet.
```powershell
git pull --ff-only origin feature/master-basis-initiate-only
python -m unittest examples.test_three_loop_vp05_target_reuse_probe -v
.\\run_vp05_target_reuse_probe.bat 2>&1 | Tee-Object -FilePath log_vp05_target_reuse_probe.txt
```
Expected VP05_TARGET_REUSE_PROBE_NOT_CLOSURE with inputs_unchanged=true. No exact proof, closure, or registry promotion.

### 2026-11-26 — User requirement: transfer VP05 techniques to standard Stage-2 (deferred)

User explicitly requests that the techniques developed during VP05 be reused when run_three_loop_master_basis_all.bat resumes standard processing, including subsequent unfinished families. Do not implement this generalization now or divert the current VP05 ②-8a through ②-11 work. At the transition back to standard Stage-2 (③/④), review the standard controller and integrate verified reusable techniques before proceeding to other unfinished families (⑥). Required considerations: memory-efficient sparse/packed representations, efficient sector-local and target-oriented methods, reusable IBP relations and validated C++ finite-field acceleration where mathematically applicable; conservative RAM/swap and time-budget guards; safe termination, atomic checksummed checkpoints, preservation of prior results, appropriate resume and skipping completed work. Prefer existing Kira path for tractable jobs; use verified alternatives for heavy jobs according to evidence, not indiscriminately. Preserve mathematical conventions, seed/target scope and promotion audits; finite-field diagnostics alone never replace exact closure. Do not assume VP05-specific optimizations transfer without validation or raise resource limits automatically. Record implementation, verification, commits and worklog updates as one work unit. This entry records a future requirement only; no changes to the standard BAT/controller or current calculation scope in this commit.

### 2026-11-26 — ②-8a actual target reuse probe completed

User supplied log_vp05_target_reuse_probe.txt (100 nonblank records). Final VP05_TARGET_REUSE_PROBE_NOT_CLOSURE, inputs_unchanged=true, cumulative_rowspace_proven=false, parents_equivalent=false, s5_s6_executed=false. All six s4 inventories and lower shells reloaded/regenerated. For each of sectors69,196,200, exact-sector manifest candidate_targets=0 and closure_targets=0; only ten scalar/dot diagnostics per sector tested. 60 point-target outcomes all nonzero single-term same-sector degree0 remainders; 54 dot outcomes used only s0 pivots, six scalar outcomes no pivots; 30/30 paired support hashes match, all frontier counts zero. This confirms limited modular scalar/dot reduction only, not independence or exact identities. No evidence here that all s5/s6 rows are unnecessary or that parent reduction is solved. ②-8a complete; ②-8b next: obtain actual parent-induced integral demand from unresolved boundary seed/target scope, including numerator-bearing subsector terms, distinguish direct IBP generation from recursively induced demand, use existing pivots before expanding shells. Do not run blanket s5/s6 based on this probe; no change to 57/78 local evidence or 63 candidates. No new calculation implementation in this entry.

### 2026-11-26 — ②-8b parent demand inventory implementation

Implemented examples/three_loop_vp05_parent_demand.py (8619a9d, sparse pinch indexing 7824281), launcher 341ff80, unit tests 8f588c2. Scan manifest candidate/closure seeds within unresolved boundary masks for exact symbolic direct hard-sector terms. Separately enumerate one-line intermediate parents under r8s6d2/r8s5d3 envelopes and collect possible pinch terms after symbolic cancellation, with counts and first-source provenance. Potential envelope is not actual recursive Kira demand or reduction proof; direct scan is limited to in-envelope manifest seeds. No s5/s6 elimination, no existing checkpoint writes, no promotion. 2h default sampled time budget, 2M envelope rows, 200k distinct target cap, host memory guard, exclusive run lock, unique JSON artifact; timeout may yield explicitly incomplete envelope inventory, not resumable computation. Unit tests committed but not executed remotely; actual Windows run pending. Next review actual degree histograms and provenance, then evaluate existing s0-s4 coverage for selected demands before new elimination. Run git pull --ff-only origin feature/master-basis-initiate-only; python -m unittest examples.test_three_loop_vp05_parent_demand -v; .\\run_vp05_parent_demand.bat 2>&1 | Tee-Object -FilePath log_vp05_parent_demand.txt. Expected VP05_PARENT_DEMAND_NOT_CLOSURE; inspect envelope_complete. 57/78 evidence and 63 provisional candidates unchanged.

### 2026-11-26 — ②-8b actual parent demand partial envelope

User log log_vp05_parent_demand.txt: manifest direct scan finished2070 rows, 12 distinct hard-sector integrals: sec69 zero, sec196 seven (numerator degrees0:4,1:3; dot degrees0:1,1:6), sec200 five (numerator0:2,1:1,2:2; dot0:1,1:4). Potential envelope partial: r8s5d3 intermediate71/77 each675675 rows completed, 40590/15510 new targets; subsequent scan stopped with generic Envelope budget (row or time guard not distinguished). 64608 potential targets all sec69 so far; numerator0..5 counts35,314,1565,5688,16818,40188; dot0..4 counts705,5391,11232,19020,28260. Sec196/200 potential counts zero because scan incomplete, not absence of dependencies. Artifact output/vp05_parent_demand01/demand_1795660139834708900.json SHA256 3b54c0111b53042b612ef6ca92ff31013e94e5b11844d8e5e35b5b03a0d0f503; envelope_complete=false, recursive_demand_proven=false, full_closure_proven=false. Actual JSON not remotely inspected. ②-8b direct inventory complete, full recursive demand unresolved. Next prioritize SHA-pinned 12 direct targets and existing s0-s4 modular substitution, record actual remaining integral keys and coefficients, compare two points, then investigate parent-induced recursive dependencies and potential degree/dot coverage. Avoid blindly extending envelope or s5/s6 ranks; potential d4 already exceeds current d2 seed scope. No new code in this entry, 57/78 unchanged, no closure/promotion.

### 2026-11-26 — ②-8b direct demand reduction implementation

Implemented examples/three_loop_vp05_direct_demand.py ad46249, launcher 5b25d39, tests d6e43e7. Pin exact parent-demand artifact SHA256 3b54c0111b53042b612ef6ca92ff31013e94e5b11844d8e5e35b5b03a0d0f503, manifest/kernel identity; regenerate direct scan and compare complete provenance/counts (2070 rows,12 targets, sec196=7 sec200=5). Load existing s0-s4 pivots one sector/point at a time; deterministic triangular substitution, record full modular remainder exponents/coefficients and pivot shell/lead/factor trace; replay trace against saved normalized modular pivots, compare both point supports. Original symbolic source multipliers not reconstructed; not cumulative elimination, no irreducibility or generic rational identity assertion. One-hour sampled budget, 2M term operations per target,20k working fill, existing host memory guard, read-only prior inputs, unique atomic JSON and reload check. No intermediate resume for short diagnostic. No new s5/s6 calculation. Tests committed but not executed in assistant environment; actual local validation pending. Run git pull --ff-only origin feature/master-basis-initiate-only; python -m unittest examples.test_three_loop_vp05_direct_demand -v; .\\run_vp05_direct_demand.bat 2>&1 | Tee-Object -FilePath log_vp05_direct_demand.txt. Expected VP05_DIRECT_DEMAND_NOT_CLOSURE, targets12, point_results24; review actual remaining terms/support and recursive demand before expanding. 57/78 unchanged; no promotion.

### 2026-11-26 — Actual direct demand reduction PASS (②-8b)

User log log_vp05_direct_demand.txt: regenerated 2070 rows, 12 direct targets; all 24 point-target reductions completed with pivot_replay=true, 12/12 paired supports match, each remainder exactly one scalar integral in its original sector. Sector196 seven targets all reduce to I(0,0,1,0,0,0,1,1,0,0,0,0), using s0/s1 only (one scalar identity no pivots). Sector200 five targets all reduce to I(0,0,0,1,0,0,1,1,0,0,0,0), using s0/s1/s2 only. No s3/s4 substitution needed for these targets; no evidence of s5/s6 need within this direct scope. Max operations3897. Artifact output/vp05_direct_demand02/reduction_1795664268348935900.json SHA256 161d836d36820dc1fb6cd7ba1379a36b75823c88bd324cbf91d3ffd49df2e421. Final VP05_DIRECT_DEMAND_NOT_CLOSURE, inputs_unchanged=true, original_symbolic_replay=false, full_closure_proven=false. Remote artifact bytes not inspected. Neither scalar is in the 63 candidate list; do not declare them independent masters or alter candidate basis. Next prioritize exact symbolic identities for the eleven nontrivial direct targets using regenerated s0-s2 original IBP rows and verified source provenance, and investigate how scalar remnants relate to canonical candidates (sector symmetries, zero-sector/other relations) and recursive parent scope. Exact proof of direct targets alone does not close parent seeds. Keep ②-8b open pending recursive scope; no blanket s5/s6, no change to 57/78 local evidence. No new implementation in this entry.

### 2026-11-26 — Direct demand exact certificate pilot (②-8b / preparatory ②-9)

Implemented examples/three_loop_vp05_direct_exact.py e223688, saved-proof replay 79450fd, launcher b54c97d, tests fb5b6db. Pin observed direct reduction artifact SHA256 161d836d36820dc1fb6cd7ba1379a36b75823c88bd324cbf91d3ffd49df2e421; regenerate kernel and s0/s1 point0 pivots, load sector200 s2 point0. Recover only needed pivot ancestors using selected original row indices and exact modular pivot replay; lift along the same elimination path in QQ(z,d). If path diverges or pivot evaluation differs, report blocked rather than infer proof. Expand original IBP multipliers independently and compare full symbolic relation; check both observed finite-field specializations. Individual atomic JSON certificates and saved-source replay on rerun, preserve existing files. 12h sampled budget, 3000 memoized pivots, 200k symbolic support/aggregate term cap, 2M counted symbolic term operations, host RAM guard; not hard limits on individual symbolic operation time, no WSL/C++ use. Scalar inventory examines three-line unit-determinant loop momentum transformations and mass multiset matches against scalar candidate triples, flags possible massless scaleless factors; no automatic basis mapping or zero-sector decision. Tests committed but not executed here; Windows actual runtime unverified, exact symbolic path may fail or exceed caps. Run git pull --ff-only origin feature/master-basis-initiate-only; python -m unittest examples.test_three_loop_vp05_direct_exact -v; .\\run_vp05_direct_exact.bat --hours 12 2>&1 | Tee-Object -FilePath log_vp05_direct_exact.txt. Expected VP05_DIRECT_EXACT_NOT_CLOSURE with proved count (12 includes one trivial identity); inspect actual proofs and scalar inventory. Parent recursive scope still unresolved, 57/78 unchanged, no promotion or s5/s6 calculation.

### 2026-11-26 — Actual direct exact certificate results: 11/12

User log log_vp05_direct_exact.txt confirms 11/12 original symbolic replays, inputs_unchanged=true, full_closure_proven=false. Includes one trivial identity, hence 10 nontrivial proofs and one blocked. Sector196 in log order coefficients/multiplier counts: d-1/174, d-1/179, 1/0, d/2-1/4, d/2-1/3, blocked, d/2-1/3. Blocked target (0,0,2,0,-1,0,1,1,0,0,0,0): Exact remainder mismatch; diagnose actual rational remainder, including terms vanishing at specialized point; do not assume cause. Prior modular coefficients5 at d7 and9 at d11 suggest d-2 only, not proof. Sector200 all five exact: 2/108, d/2-1/2, (2*d**2-2*d-4)/d /811, 2*d-2/108, d/2-1/2. Preserve all 11 individual certificates, remote certificate bytes not inspected. Both scalar remnants sec196 and200 have unit determinant1 and three m2 propagators; both match existing candidate sec73 I(1,0,0,1,0,0,1,0,0,0,0,0). Next verify explicit affine loop momentum changes, propagator mapping and Jacobian to establish equality; no new master candidate inferred. Finish blocked target via exact remainder diagnostics and additional symbolic reductions or independent affine-factorization identity, distinguish IBP original-source certificate from alternative proof. Recursive parent dependencies remain unresolved; ②-8b open, ②-9 pilot only, 57/78 unchanged; no s5/s6 blanket run or registry promotion. No implementation changes in this entry.
