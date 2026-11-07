## READ THIS FIRST — C111 INITIAL TASK (20261107T001203Z, produced after C110 completion)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104 DONE: `VOLUME_WAVELET_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_20261106T213213Z.json`, `oos_edge_proven=false`.
- C105 DONE: `VOLUME_HURST_RS_PERSISTENCE_MR` → `reports/real_quote_volume_hurst_rs_persistence_mr_costed_oos_20261106T213620Z.json`, `oos_edge_proven=false`.
- C106 DONE: `VOLUME_SAMPLE_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_sample_entropy_shock_mr_costed_oos_20261106T225102Z.json` (sha256 `08b4ea8b5e0b9ada11e463255b61e6d42976f12eda61de7ed33fd520a7fde21b`), `oos_edge_proven=false`. Do NOT rerun.
- C107 DONE: `VOLUME_PERMUTATION_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_permutation_entropy_shock_mr_costed_oos_20261106T232706Z.json` (sha256 `12b02d9f91b8c37dd2518c99626320b638773a6d085e74b4967bdf493659f96c`), `oos_edge_proven=false`. Do NOT rerun.
- C108 DONE: `VOLUME_SLOPE_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_slope_entropy_shock_mr_costed_oos_20261107T000211Z.json` (sha256 `f4cc1868aebb8f3b0e383bdccd1447af970bfd4a4ad50751006641ee2e66108f`), `oos_edge_proven=false`. Do NOT rerun.
- C109 DONE: `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_dispersion_entropy_shock_mr_costed_oos_20261107T000606Z.json` (sha256 `6068210ad5c2e1911e891c94bc3609e6ddc3c0ee8a3bc4b038ebcbe64b9119c5`), script sha `7b7372504699988991ad59396f5f014c464adc2a65443204c0025e16aca61d75`, `oos_edge_proven=false`. Do NOT rerun.
- **C110 DONE (this session): `VOLUME_BUBBLE_ENTROPY_SHOCK_MR` (Bubble Entropy Manis et al. 2017; W_BE=168, swap-count distributions m=2,3 delay=1, Renyi-2/collision H2 normalized by log2(N_m), BubbleEn=(H2_3-H2_2)/log2(3); fade shocks vs ALB=336 baseline) → `reports/real_quote_volume_bubble_entropy_shock_mr_costed_oos_20261107T001005Z.json` (sha256 `248d74d4953f959479e4eb99e70be4bb4e457cc40d92c108c1154870284de184`), script `scripts/run_real_quote_volume_bubble_entropy_shock_mr_costed_oos.py` (sha256 `d3ca4f20e28a3eb41b819bdb6851aaee2a5bf0c0343fa6d3a85e84d5f6006711`), `oos_edge_proven=false`.** Do NOT rerun.
- C110 Step 2 artifacts: ingest `reports/real_feed_ingest_attempt_20261107T001203Z.json` (sha `14fdfd7b37861d3c336166a07362dc7c42adb6ab820194290bbd0c9deae42f0f`, FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT, rb_unblocked=true), registry `reports/strategy_edge_registry_20261107T001203Z.json` (sha `112754acd792d4401203fa3c086d63480aad7866baa53a980a6ca93c8a60cd29`, supersedes `20261107T000648Z`), summary `reports/campaign110_execution_summary_20261107T001203Z.json` (sha `5883d0416e13c1ce4472140c1ee11e2ad0d2c6328a5d6c1874db6eec0865bdee`).
- Latest registry: `reports/strategy_edge_registry_20261107T001203Z.json` (sha `112754acd792d4401203fa3c086d63480aad7866baa53a980a6ca93c8a60cd29`) — includes C104-C110; `edge_claim: NONE`.
- Latest ingest evidence: `reports/real_feed_ingest_attempt_20261107T001203Z.json` — `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT`, `rb_unblocked=true`. **DOES NOT BLOCK R-B.**
- Real data preconditions OK: `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}` and spot cache `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- pytest: module NOT installed in this env (`python3 -m pytest` → `No module named pytest`); counts carried forward from lineage (928 passed/1 skipped/0 failed) — **record honestly, do not fabricate**.

### NEXT FOCUS CAMPAIGN — C111 R-B `VOLUME_SVD_ENTROPY_SHOCK_MR` (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104-C110 are done — do NOT rerun. C111 is PENDING and must be executed.

#### Step 0 — Grep-verify distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "svd_entropy\|SVD_ENTROPY\|SvdEn" scripts/ reports/real_quote_volume_*svd* 2>&1 | head -20
# Expect: NO existing C111 svd-entropy OOS script/report. If a C111-spec report exists (campaign 111, W_SVD/m spec below), STOP and advance to C112 (VOLUME_FISHER_INFORMATION_SHOCK_MR; grep-verify).
ls scripts/run_real_quote_volume_svd_entropy* reports/real_quote_volume_svd_entropy* 2>&1 | head
```

#### Step 1 — Implement + run C111 `VOLUME_SVD_ENTROPY_SHOCK_MR` (PRIORITY 1)
1. Create `scripts/run_real_quote_volume_svd_entropy_shock_mr_costed_oos.py` mirroring `scripts/run_real_quote_volume_bubble_entropy_shock_mr_costed_oos.py` structure (imports, wf_windows, load_spot/load_volume, run_asset, main, sha256, fail-closed), **campaign 111**.
2. **Feature (pre-stated, distinct):** rolling Singular Value Decomposition entropy over window `W_SVD=168` on log-volume returns `r_t = log(v_t/v_{t-1})`. Form trajectory/Hankel embedding from the window, compute singular values `s_1..s_k`, normalize `p_i = s_i / sum(s)`, compute Shannon/SVD entropy `H = -sum(p_i log p_i)` normalized by `log(k)`. Distinct from bubble/dispersion/permutation/sample/approximate/spectral/wavelet/DFA/Hurst/slope/LZ/Petrosian/Higuchi/Katz/turning-point/variance-ratio/OU/BDS entropies.
3. **Signal (fail-closed MR):** `z = (SVDEn - ALB_mean) / ALB_std`, baseline `ALB=336`. `shock = |z|`. `entry_z >= 1.5` -> if `z > 0` (high SVD-entropy/complexity shock) fade short (-1), if `z < 0` (low-entropy/order shock) fade long (+1); `exit_z < 0.5` or `max_hold=24` or flip. Execution `t -> t+1` (no lookahead). Apply only where real volume/spot bars exist.
4. **WF/costs/B&H (exact):** WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]` (bps fee, bps slippage), B&H same OOS windows. Real data only; full provenance + sha256.
5. Run and emit: `reports/real_quote_volume_svd_entropy_shock_mr_costed_oos_<UTC>.json`.

#### Step 2 — Registry + ingest evidence + pytest + summary (MANDATORY)
1. Nonspot ingest evidence: emit `reports/real_feed_ingest_attempt_<UTC>.json` (FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT if none; record searched patterns + found_real_artifacts=[]). Does NOT block R-B.
2. Pytest: `python3 -m pytest tests/ -q` (record counts/rc; if pytest missing record fail-closed note, do not fabricate).
3. Registry: emit `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T001203Z.json` (sha `112754acd792d4401203fa3c086d63480aad7866baa53a980a6ca93c8a60cd29`), include C104-C111 (carry C104-C110, add C111). Set `edge_claim: NONE` unless edge rule holds.
4. Summary: emit `reports/campaign111_execution_summary_<UTC>.json` (artifacts + sha256s + nonspot blocker + edge claim + next campaign).

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- **No status summary before >= 3 new concrete report artifacts exist for C111** (C111 OOS report + ingest attempt + registry/summary — ensure >=3 new).
- **Heavy work mandatory:** implement + run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- C110 marked DONE with artifact/script SHAs; C104-C109 locked — no reruns.
- Distinct C111 hypothesis pre-stated (SVD entropy, trajectory singular values, Shannon entropy normalized) + grep-verify step — prevents duplicate-family waste.
- Nonspot ingest explicitly decoupled from R-B — prevents blocker-loop paralysis.
- "No status before >=3 new artifacts" + mandatory implementation/run — forces heavy work.
- Fallback ladder if C111 already exists: `VOLUME_FISHER_INFORMATION_SHOCK_MR` → `VOLUME_ATTENTION_ENTROPY_SHOCK_MR` → `VOLUME_INCREMENT_ENTROPY_SHOCK_MR` → `VOLUME_PERMUTATION_VARIANCE_SHOCK_MR` (grep-verify each) — no stalling.

### Immediate first action (do this in order)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "svd_entropy\|SVD_ENTROPY\|SvdEn" scripts/ reports/real_quote_volume_*svd* 2>&1 | head -15
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl 2>&1 | head
```
Then implement `scripts/run_real_quote_volume_svd_entropy_shock_mr_costed_oos.py` (C111 spec), run it, emit C111 OOS report, then Step 2 (ingest + pytest + registry + summary). **Do not stop until Step 2 complete with >=3 new C111 artifacts.**
