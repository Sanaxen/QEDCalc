

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
