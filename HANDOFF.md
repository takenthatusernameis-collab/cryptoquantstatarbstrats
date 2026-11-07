## READ THIS FIRST — C108 INITIAL TASK (20261106T235915Z, produced by handoff agent)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104 DONE: `VOLUME_WAVELET_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_20261106T213213Z.json`, `oos_edge_proven=false`.
- C105 DONE: `VOLUME_HURST_RS_PERSISTENCE_MR` → `reports/real_quote_volume_hurst_rs_persistence_mr_costed_oos_20261106T213620Z.json`, `oos_edge_proven=false`.
- C106 DONE: `VOLUME_SAMPLE_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_sample_entropy_shock_mr_costed_oos_20261106T225102Z.json` (sha256 `08b4ea...e21b`), `oos_edge_proven=false`. Do NOT rerun.
- **C107 DONE: `VOLUME_PERMUTATION_ENTROPY_SHOCK_MR` (PE order d=3, delay tau=1, W_PE=168) → `reports/real_quote_volume_permutation_entropy_shock_mr_costed_oos_20261106T232706Z.json` (sha256 `12b02d...f96c`), `oos_edge_proven=false`.** Do NOT rerun.
- Latest registry: `reports/strategy_edge_registry_20261106T232826Z.json` (supersedes 20261106T204555Z) — includes C104-C107; `edge_claim: NONE`. C107 summary: `reports/campaign107_execution_summary_20261106T232844Z.json`.
- Latest ingest evidence: `reports/real_feed_ingest_attempt_20261106T232607Z.json` — `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT`, `rb_unblocked=true`. **DOES NOT BLOCK R-B.**
- Real data preconditions OK: `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}` and spot cache present.
- pytest: 928 passed / 1 skipped / 0 failed, rc=0 (carried forward per registry note; pytest not installed in env — record honestly if still missing).

### NEXT FOCUS CAMPAIGN — C108 R-B `VOLUME_SLOPE_ENTROPY_SHOCK_MR` (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104-C107 are done — do NOT rerun. C108 is PENDING and must be executed.

#### Step 0 — Grep-verify distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "slope_entropy\|SLOPE_ENTROPY" scripts/ reports/real_quote_volume_*slope* 2>&1 | head -20
# Expect: NO existing C108 slope-entropy OOS script/report (only this handoff mention is acceptable after write). If a C108-spec report exists (campaign 108, W_SE spec below), STOP and advance to C109 (state next hypothesis in registry/summary).
ls scripts/run_real_quote_volume_slope_entropy* reports/real_quote_volume_slope_entropy* 2>&1 | head
```

#### Step 1 — Implement + run C108 `VOLUME_SLOPE_ENTROPY_SHOCK_MR` (PRIORITY 1)
1. Create `scripts/run_real_quote_volume_slope_entropy_shock_mr_costed_oos.py` mirroring `scripts/run_real_quote_volume_sample_entropy_shock_mr_costed_oos.py` structure (imports, wf_windows, load_spot/load_volume, run_asset, main, sha256, fail-closed), **campaign 108**.
2. **Feature (pre-stated, distinct):** rolling Slope Entropy (Cuesta-Frau 2019) over window `W_SE=168` on log-volume returns `r_t = log(v_t/v_{t-1})`. For each window compute consecutive slope symbols `s_i = sign(r_{i} - r_{i-1}) * I(|r_{i}-r_{i-1}| >= gamma*std(window))` with `gamma=1.0` (3 symbols: -1,0,+1); compute Shannon entropy of symbol distribution (normalized by log(3)). Distinct from permutation/sample/approximate/spectral/wavelet/DFA/Hurst/LZ/Petrosian/Higuchi/Katz/turning-point/variance-ratio/OU/BDS entropies & complexities already tested.
3. **Signal (fail-closed MR):** `z = (SE - ALB_mean) / ALB_std`, baseline `ALB=336`. `shock = |z|`. `entry_z >= 1.5` -> if `z > 0` (high slope-entropy/irregularity shock) fade short (-1), if `z < 0` (low-entropy/order shock) fade long (+1); `exit_z < 0.5` or `max_hold=24` or flip. Execution `t -> t+1` (no lookahead). Apply only where real volume/spot bars exist.
4. **WF/costs/B&H (exact):** WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]` (bps fee, bps slippage), B&H same OOS windows. Real data only; full provenance + sha256.
5. Run and emit: `reports/real_quote_volume_slope_entropy_shock_mr_costed_oos_<UTC>.json`.

#### Step 2 — Registry + ingest evidence + pytest + summary (MANDATORY)
1. Nonspot ingest evidence: emit `reports/real_feed_ingest_attempt_<UTC>.json` (FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT if none; record searched patterns + found_real_artifacts=[]). Does NOT block R-B.
2. Pytest: `python -m pytest tests/ -q` (record counts/rc; if pytest missing record fail-closed note, do not fabricate).
3. Registry: emit `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261106T232826Z.json`, include C104-C108 (carry C104-C107 entries, add C108). Set `edge_claim: NONE` unless edge rule holds.
4. Summary: emit `reports/campaign108_execution_summary_<UTC>.json` (artifacts + sha256s + nonspot blocker + edge claim + next campaign).

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- **No status summary before >= 3 new concrete report artifacts exist for C108** (C108 OOS report + ingest attempt + registry/summary — ensure >=3 new).
- **Heavy work mandatory:** implement + run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- Stale C107 handoff replaced with timestamped C108 directive — no agent can claim C107 is pending.
- Distinct C108 hypothesis pre-stated + grep-verify step — prevents duplicate-family waste.
- Nonspot ingest explicitly decoupled from R-B — prevents blocker-loop paralysis.
- "No status before >=3 new artifacts" + mandatory implementation/run — forces heavy work.
- If C108 already exists when grep-verified, agent must advance to next untested hypothesis (e.g. `VOLUME_DISPERSION_ENTROPY_SHOCK_MR`, then `VOLUME_BUBBLE_ENTROPY_SHOCK_MR`, `VOLUME_SVD_ENTROPY_SHOCK_MR`, `VOLUME_FISHER_INFORMATION_SHOCK_MR`) — no stalling.

### Immediate first action (do this in order)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "slope_entropy\|SLOPE_ENTROPY" scripts/ reports/real_quote_volume_*slope* 2>&1 | head -15
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json 2>&1 | head
```
Then implement `scripts/run_real_quote_volume_slope_entropy_shock_mr_costed_oos.py` (C108 spec), run it, emit C108 OOS report, then Step 2 (ingest + pytest + registry + summary). **Do not stop until Step 2 complete with >=3 new C108 artifacts.**
