## READ THIS FIRST — C110 INITIAL TASK (20261107T000715Z, produced after C109 completion)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104 DONE: `VOLUME_WAVELET_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_20261106T213213Z.json`, `oos_edge_proven=false`.
- C105 DONE: `VOLUME_HURST_RS_PERSISTENCE_MR` → `reports/real_quote_volume_hurst_rs_persistence_mr_costed_oos_20261106T213620Z.json`, `oos_edge_proven=false`.
- C106 DONE: `VOLUME_SAMPLE_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_sample_entropy_shock_mr_costed_oos_20261106T225102Z.json` (sha256 `08b4ea8b5e0b9ada11e463255b61e6d42976f12eda61de7ed33fd520a7fde21b`), `oos_edge_proven=false`. Do NOT rerun.
- C107 DONE: `VOLUME_PERMUTATION_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_permutation_entropy_shock_mr_costed_oos_20261106T232706Z.json` (sha256 `12b02d9f91b8c37dd2518c99626320b638773a6d085e74b4967bdf493659f96c`), `oos_edge_proven=false`. Do NOT rerun.
- C108 DONE: `VOLUME_SLOPE_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_slope_entropy_shock_mr_costed_oos_20261107T000211Z.json` (sha256 `f4cc1868aebb8f3b0e383bdccd1447af970bfd4a4ad50751006641ee2e66108f`), `oos_edge_proven=false`. Do NOT rerun.
- **C109 DONE (this session): `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` (Dispersion Entropy Rostaghi & Azami 2016; W_DE=168, NCDF window z-score→[0,1], c=6 classes, m=2, d=1, Shannon entropy normalized by log(c^m); shock=|z(DE)| vs ALB=336; fade extremes t->t+1) → `reports/real_quote_volume_dispersion_entropy_shock_mr_costed_oos_20261107T000606Z.json` (sha256 `6068210ad5c2e1911e891c94bc3609e6ddc3c0ee8a3bc4b038ebcbe64b9119c5`), script `scripts/run_real_quote_volume_dispersion_entropy_shock_mr_costed_oos.py` (sha256 `7b7372504699988991ad59396f5f014c464adc2a65443204c0025e16aca61d75`), `oos_edge_proven=false`.** Do NOT rerun.
- Latest registry: `reports/strategy_edge_registry_20261107T000648Z.json` (sha256 `658954a37951775fc797baebb2efe73631b874a63af0481c8b8c17d4d4a791c0`, supersedes `20261107T000254Z` sha `d8a2a826...`) — includes C104-C109; `edge_claim: NONE`.
- Latest ingest evidence: `reports/real_feed_ingest_attempt_20261107T000648Z.json` (sha256 `2c91eaaf82d66ec0a4310642876b81e74680e9fd2ea425d1bd554596fc57a5a8`) — `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT`, `rb_unblocked=true`. **DOES NOT BLOCK R-B.**
- C109 summary: `reports/campaign109_execution_summary_20261107T000648Z.json` (sha256 `0e6732fb754355f5d0e6f04dd15c4bb2e8cbfcf1f6007bd82f7950bf48e1c7e2`).
- Real data preconditions OK: `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}` and spot cache `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- pytest: module NOT installed in this env (`python3 -m pytest` → `No module named pytest`); counts carried forward from lineage (928 passed/1 skipped/0 failed) — **record honestly, do not fabricate**.

### NEXT FOCUS CAMPAIGN — C110 R-B `VOLUME_BUBBLE_ENTROPY_SHOCK_MR` (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104-C109 are done — do NOT rerun. C110 is PENDING and must be executed.

#### Step 0 — Grep-verify distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "bubble_entropy\|BUBBLE_ENTROPY\|BubbleEn" scripts/ reports/real_quote_volume_*bubble* 2>&1 | head -20
# Expect: NO existing C110 bubble-entropy OOS script/report. If a C110-spec report exists (campaign 110, W_BE/m spec below), STOP and advance to C111 (VOLUME_SVD_ENTROPY_SHOCK_MR; grep-verify).
ls scripts/run_real_quote_volume_bubble_entropy* reports/real_quote_volume_bubble_entropy* 2>&1 | head
```

#### Step 1 — Implement + run C110 `VOLUME_BUBBLE_ENTROPY_SHOCK_MR` (PRIORITY 1)
1. Create `scripts/run_real_quote_volume_bubble_entropy_shock_mr_costed_oos.py` mirroring `scripts/run_real_quote_volume_dispersion_entropy_shock_mr_costed_oos.py` structure (imports, wf_windows, load_spot/load_volume, run_asset, main, sha256, fail-closed), **campaign 110**.
2. **Feature (pre-stated, distinct):** rolling Bubble Entropy (Manis et al. 2017) over window `W_BE=168` on log-volume returns `r_t = log(v_t/v_{t-1})`. Compute embedding vectors length `m=2` and `m=3` (delay 1). For each m, count swaps needed to sort each embedded vector (bubble-sort swap count) as the complexity measure; form swap-count probability distributions `p_m`, `p_{m+1}` and compute Rényi entropy of order 2 (Collision Entropy) `H2 = -log2(sum(p_i^2))` (normalized by `log2` of number of possible swap states). `BubbleEn = (H2_{m+1} - H2_m) / log2((m+1)/ (m-1))` (standard normalization; be explicit in code/comments). Distinct from dispersion/permutation/sample/approximate/spectral/wavelet/DFA/Hurst/slope/LZ/Petrosian/Higuchi/Katz/turning-point/variance-ratio/OU/BDS.
3. **Signal (fail-closed MR):** `z = (BE - ALB_mean) / ALB_std`, baseline `ALB=336`. `shock = |z|`. `entry_z >= 1.5` -> if `z > 0` (high bubble-entropy/irregularity shock) fade short (-1), if `z < 0` (low-entropy/order shock) fade long (+1); `exit_z < 0.5` or `max_hold=24` or flip. Execution `t -> t+1` (no lookahead). Apply only where real volume/spot bars exist.
4. **WF/costs/B&H (exact):** WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]` (bps fee, bps slippage), B&H same OOS windows. Real data only; full provenance + sha256.
5. Run and emit: `reports/real_quote_volume_bubble_entropy_shock_mr_costed_oos_<UTC>.json`.

#### Step 2 — Registry + ingest evidence + pytest + summary (MANDATORY)
1. Nonspot ingest evidence: emit `reports/real_feed_ingest_attempt_<UTC>.json` (FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT if none; record searched patterns + found_real_artifacts=[]). Does NOT block R-B.
2. Pytest: `python3 -m pytest tests/ -q` (record counts/rc; if pytest missing record fail-closed note, do not fabricate).
3. Registry: emit `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T000648Z.json` (sha `658954a3...`), include C104-C110 (carry C104-C109, add C110). Set `edge_claim: NONE` unless edge rule holds.
4. Summary: emit `reports/campaign110_execution_summary_<UTC>.json` (artifacts + sha256s + nonspot blocker + edge claim + next campaign).

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- **No status summary before >= 3 new concrete report artifacts exist for C110** (C110 OOS report + ingest attempt + registry/summary — ensure >=3 new).
- **Heavy work mandatory:** implement + run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- C109 marked DONE with artifact SHAs; C104-C108 locked — no reruns.
- Distinct C110 hypothesis pre-stated (Bubble Entropy, swap-count distributions m=2,3, Rényi/Collision H2 difference) + grep-verify step — prevents duplicate-family waste.
- Nonspot ingest explicitly decoupled from R-B — prevents blocker-loop paralysis.
- "No status before >=3 new artifacts" + mandatory implementation/run — forces heavy work.
- Fallback ladder if C110 already exists: `VOLUME_SVD_ENTROPY_SHOCK_MR` → `VOLUME_FISHER_INFORMATION_SHOCK_MR` → `VOLUME_ATTENTION_ENTROPY_SHOCK_MR` → `VOLUME_INCREMENT_ENTROPY_SHOCK_MR` (grep-verify each) — no stalling.

### Immediate first action (do this in order)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "bubble_entropy\|BUBBLE_ENTROPY\|BubbleEn" scripts/ reports/real_quote_volume_*bubble* 2>&1 | head -15
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl 2>&1 | head
```
Then implement `scripts/run_real_quote_volume_bubble_entropy_shock_mr_costed_oos.py` (C110 spec), run it, emit C110 OOS report, then Step 2 (ingest + pytest + registry + summary). **Do not stop until Step 2 complete with >=3 new C110 artifacts.**
