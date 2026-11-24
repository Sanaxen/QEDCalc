

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
