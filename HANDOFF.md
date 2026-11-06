## READ THIS FIRST — C107 INITIAL TASK (20261106T232205Z, produced by handoff agent)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104 DONE: `VOLUME_WAVELET_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_20261106T213213Z.json`, `oos_edge_proven=false`.
- C105 DONE: `VOLUME_HURST_RS_PERSISTENCE_MR` → `reports/real_quote_volume_hurst_rs_persistence_mr_costed_oos_20261106T213620Z.json`, `oos_edge_proven=false`.
- **C106 DONE: `VOLUME_SAMPLE_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_sample_entropy_shock_mr_costed_oos_20261106T225102Z.json`, `oos_edge_proven=false`.** Do NOT rerun C106. Not yet reflected in latest registry.
- **C107 PENDING: `VOLUME_PERMUTATION_ENTROPY_SHOCK_MR` (permutation entropy over ordinal patterns, order d=3, delay tau=1, window W_PE=168).** `scripts/run_real_quote_volume_permutation_entropy_shock_mr_costed_oos.py` EXISTS but implements the stale campaign-58 spec (W=48, cost grid 0-20bps, campaign 58) — NOT the C107 spec. The C107 report (`real_quote_volume_permutation_entropy_shock_mr_costed_oos_20261106*.json`, campaign 107, W_PE=168, cost grid 0-40bps) does NOT exist. **EXECUTE FIRST:** reimplement to C107 spec and run.
- Latest registry `reports/strategy_edge_registry_20261106T213828Z.json` records only campaigns 104/105 — **stale**, missing C106/C107. Must be regenerated in Step 3.
- Nonspot ingest: `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT`. **DOES NOT BLOCK R-B.**
- Real data preconditions OK: `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}` and spot cache present.
- pytest: 928 passed / 1 skipped / 0 failed, rc=0 (recorded in latest registry).

### NEXT FOCUS CAMPAIGN — C107 THEN REGISTRY (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** Do not skip C107. C106 is already done — do not rerun it.

#### Step 1 — C107 R-B `VOLUME_PERMUTATION_ENTROPY_SHOCK_MR` (PRIORITY 1)
1. Grep-verify: `scripts/run_real_quote_volume_permutation_entropy_shock_mr_costed_oos.py` EXISTS but is the stale campaign-58 implementation (W=48, cost grid 0-20bps). `reports/real_quote_volume_permutation_entropy_shock_mr_costed_oos_20261106T042953Z.json` is campaign 58, NOT campaign 107. Do not count it as C107.
2. Reimplement `scripts/run_real_quote_volume_permutation_entropy_shock_mr_costed_oos.py` to the C107 spec mirroring `scripts/run_real_quote_volume_sample_entropy_shock_mr_costed_oos.py` structure (imports, wf_windows, load_spot/load_volume, run_asset, main, sha256, fail-closed), campaign 107.
   - Feature: rolling permutation entropy (ordinal patterns order d=3, delay tau=1) over window `W_PE` (e.g. 168) on log-volume returns. Distinct from spectral/wavelet/sample/approximate entropy.
   - Signal: shock = `|z(PE)|` vs baseline `ALB` (e.g. 336), entry_z>=1.5 -> high PE shock fades short (-1), low fades long (+1), exit_z<0.5 or max_hold (24) or flip; execution t->t+1.
3. Run with WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.
4. Emit `reports/real_quote_volume_permutation_entropy_shock_mr_costed_oos_<UTC>.json`.

#### Step 2 — Registry + ingest evidence + pytest + execution summaries (MANDATORY)
1. Nonspot ingest evidence: emit `reports/real_feed_ingest_attempt_<UTC>.json` (FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT if none).
2. Pytest: `python -m pytest tests/ -q` (record counts/rc).
3. Registry: emit `reports/strategy_edge_registry_<UTC>.json` superseding latest, include C106 + C107 results (fix stale registry).
4. Summaries: emit `reports/campaign107_execution_summary_<UTC>.json`.

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- **No status summary before >= 3 new concrete report artifacts exist.**
- **Heavy work mandatory:** implement + run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed
- C106 already done — do not rerun; proceed directly to C107.
- Stale registry (missing C106/C107) — regenerate in Step 2.
- Nonspot ingest blocker decoupled from R-B.
- Force heavy work: implementation required, not analysis-only.

### Immediate first action (do this in order)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -c "permutation_entropy" scripts/run_real_quote_volume_permutation_entropy_shock_mr_costed_oos.py  # expect >0 (stale C58 impl)
ls reports/real_quote_volume_permutation_entropy_shock_mr_costed_oos_20261106T*.json  # only C58 report at 042953Z exists; no C107 report
python -c "import numpy,scipy,pandas" && echo "deps_ok" || true
```
Then reimplement C107 script to W_PE=168 / cost grid 0-40bps / campaign 107, run it, emit artifacts, then Step 2. Do not stop until Step 2 complete with >=3 new artifacts.
(End of file)
