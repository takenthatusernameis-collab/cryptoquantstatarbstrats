## READ THIS FIRST — C106/C107 INITIAL TASK (20261106T225702Z, produced by handoff agent)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104 DONE: `VOLUME_WAVELET_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_20261106T213213Z.json`, `oos_edge_proven=false`. C105 DONE: `VOLUME_HURST_RS_PERSISTENCE_MR` → `reports/real_quote_volume_hurst_rs_persistence_mr_costed_oos_20261106T213620Z.json`, `oos_edge_proven=false`. Latest registry `reports/strategy_edge_registry_20261106T213828Z.json`. pytest: 928 passed / 1 skipped / 0 failed, rc=0.
- C106 `VOLUME_SAMPLE_ENTROPY_SHOCK_MR` (sample entropy SampEn over rolling windows): grep-verified ABSENT — no `sample_entropy` script/report exists. **EXECUTE FIRST.**
- C107 `VOLUME_PERMUTATION_ENTROPY_SHOCK_MR` (permutation entropy over ordinal patterns): grep-verified ABSENT — no `permutation_entropy` script/report exists. **EXECUTE AFTER C106.**
- Nonspot ingest: `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT`. **DOES NOT BLOCK R-B.**
- Real data preconditions OK: `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}` and spot cache present.

### NEXT FOCUS CAMPAIGN — C106 THEN C107 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** Do not skip to C107 without C106 unless `reports/real_quote_volume_sample_entropy_shock_mr_costed_oos_*.json` already exists.

#### Step 1 — C106 R-B `VOLUME_SAMPLE_ENTROPY_SHOCK_MR` (PRIORITY 1)
1. Grep-verify distinctness: `grep -r "sample_entropy" reports/ scripts/ | wc -l` (expect 0).
2. Create `scripts/run_real_quote_volume_sample_entropy_shock_mr_costed_oos.py` mirroring `scripts/run_real_quote_volume_spectral_entropy_shock_mr_costed_oos.py` structure (imports, wf_windows, load_spot/load_volume, run_asset, main, sha256, fail-closed).
   - Feature: rolling sample entropy (SampEn, m=2, r=0.2*std) over window `W_SE` (e.g. 168) on log-volume returns. Distinct from spectral/wavelet/approximate entropy.
   - Signal: shock = `|z(SampEn)|` vs baseline `ALB` (e.g. 336), entry_z>=1.5 -> high sample-entropy shock fades short (-1), low fades long (+1), exit_z<0.5 or max_hold (24) or flip; execution t->t+1.
3. Run with WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.
4. Emit `reports/real_quote_volume_sample_entropy_shock_mr_costed_oos_<UTC>.json`.

#### Step 2 — C107 R-B `VOLUME_PERMUTATION_ENTROPY_SHOCK_MR` (PRIORITY 2, after C106)
1. Grep-verify distinctness: `grep -r "permutation_entropy" reports/ scripts/ | wc -l` (expect 0).
2. Create `scripts/run_real_quote_volume_permutation_entropy_shock_mr_costed_oos.py` same framework.
   - Feature: rolling permutation entropy (ordinal patterns order d=3, delay tau=1) over window `W_PE` (e.g. 168) on log-volume returns. Distinct from spectral/wavelet/sample/approximate entropy.
   - Signal: shock on |z(PE)| vs baseline; fade extremes per same logic with t->t+1, same WF/costs.
3. Run and emit `reports/real_quote_volume_permutation_entropy_shock_mr_costed_oos_<UTC>.json`.

#### Step 3 — Registry + ingest evidence + pytest + execution summaries (MANDATORY)
1. Nonspot ingest evidence: emit `reports/real_feed_ingest_attempt_<UTC>.json` (FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT if none).
2. Pytest: `python -m pytest tests/ -q` (record counts/rc).
3. Registry: emit `reports/strategy_edge_registry_<UTC>.json` superseding latest, include C106/C107 results.
4. Summaries: emit `reports/campaign106_execution_summary_<UTC>.json` and `reports/campaign107_execution_summary_<UTC>.json`.

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
- Nonspot ingest blocker decoupled from R-B.
- C106 is hard prerequisite to C107.
- Force heavy work: implementation required, not analysis-only.

### Immediate first action (do this in order)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -r "sample_entropy" reports/ scripts/ | wc -l  # expect 0
grep -r "permutation_entropy" reports/ scripts/ | wc -l  # expect 0
python -c "import numpy,scipy,pandas" && echo "deps_ok" || true
```
Then implement C106 script, run it, emit artifacts, then C107. Do not stop until Step 3 complete with >=3 new artifacts.
(End of file)