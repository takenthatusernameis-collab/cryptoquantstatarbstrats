## READ THIS FIRST — C109 INITIAL TASK (20261107T000259Z, produced after C108 completion)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104 DONE: `VOLUME_WAVELET_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_wavelet_entropy_shock_mr_costed_oos_20261106T213213Z.json`, `oos_edge_proven=false`.
- C105 DONE: `VOLUME_HURST_RS_PERSISTENCE_MR` → `reports/real_quote_volume_hurst_rs_persistence_mr_costed_oos_20261106T213620Z.json`, `oos_edge_proven=false`.
- C106 DONE: `VOLUME_SAMPLE_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_sample_entropy_shock_mr_costed_oos_20261106T225102Z.json` (sha256 `08b4ea...e21b`), `oos_edge_proven=false`. Do NOT rerun.
- C107 DONE: `VOLUME_PERMUTATION_ENTROPY_SHOCK_MR` → `reports/real_quote_volume_permutation_entropy_shock_mr_costed_oos_20261106T232706Z.json` (sha256 `12b02d...f96c`), `oos_edge_proven=false`. Do NOT rerun.
- **C108 DONE (this session): `VOLUME_SLOPE_ENTROPY_SHOCK_MR` (Slope Entropy Cuesta-Frau 2019; W_SE=168, gamma=1.0, symbols sign(r_i-r_{i-1})*I(|diff|>=gamma*std), normalized by log(3); shock=|z(SE)| vs ALB=336; fade extremes t->t+1) → `reports/real_quote_volume_slope_entropy_shock_mr_costed_oos_20261107T000211Z.json` (sha256 `f4cc1868aebb8f3b0e383bdccd1447af970bfd4a4ad50751006641ee2e66108f`), script `scripts/run_real_quote_volume_slope_entropy_shock_mr_costed_oos.py` (sha256 `329d7d1129b93ce2d99801a0ad771a402f4f87254d4c3589be6e6b26cd621770`), `oos_edge_proven=false`.** Do NOT rerun.
- Latest registry: `reports/strategy_edge_registry_20261107T000254Z.json` (sha256 `d8a2a826ade40575d0024b54ed4dfb6af23f7641fec2ee441f7a7f4b57af011a`, supersedes `20261106T232826Z`) — includes C104-C108; `edge_claim: NONE`.
- Latest ingest evidence: `reports/real_feed_ingest_attempt_20261107T000254Z.json` (sha256 `c5c0544de67243512b40f47c2909165666c235bfa6ee1e4c67e5a709c115deb5`) — `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT`, `rb_unblocked=true`. **DOES NOT BLOCK R-B.**
- C108 summary: `reports/campaign108_execution_summary_20261107T000254Z.json` (sha256 `e46ee62e697892879f758851acc691de736d3ef3981a8e93c413391fd63d8483`).
- Real data preconditions OK: `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}` and spot cache `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- pytest: module NOT installed in this env (`python3 -m pytest` → `No module named pytest`); counts carried forward from lineage (928 passed/1 skipped/0 failed) — **record honestly, do not fabricate**.

### NEXT FOCUS CAMPAIGN — C109 R-B `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104-C108 are done — do NOT rerun. C109 is PENDING and must be executed.

#### Step 0 — Grep-verify distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "dispersion_entropy\|DISPERSION_ENTROPY\|DispEn" scripts/ reports/real_quote_volume_*dispersion* 2>&1 | head -20
# Expect: NO existing C109 dispersion-entropy OOS script/report. If a C109-spec report exists (campaign 109, W_DE spec below), STOP and advance to C110 (state next hypothesis in registry/summary).
ls scripts/run_real_quote_volume_dispersion_entropy* reports/real_quote_volume_dispersion_entropy* 2>&1 | head
```

#### Step 1 — Implement + run C109 `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` (PRIORITY 1)
1. Create `scripts/run_real_quote_volume_dispersion_entropy_shock_mr_costed_oos.py` mirroring `scripts/run_real_quote_volume_slope_entropy_shock_mr_costed_oos.py` structure (imports, wf_windows, load_spot/load_volume, run_asset, main, sha256, fail-closed), **campaign 109**.
2. **Feature (pre-stated, distinct):** rolling Dispersion Entropy (Rostaghi & Azami 2016) over window `W_DE=168` on log-volume returns `r_t = log(v_t/v_{t-1})`. Map values via normal CDF (NCDF) to [0,1], quantize into `c=6` classes; form embedding vectors length `m=2`, delay `d=1`; compute dispersion-pattern probabilities and Shannon entropy normalized by `log(c^m)`. Distinct from permutation/sample/approximate/spectral/wavelet/DFA/Hurst/slope/LZ/Petrosian/Higuchi/Katz/turning-point/variance-ratio/OU/BDS entropies & complexities already tested.
3. **Signal (fail-closed MR):** `z = (DE - ALB_mean) / ALB_std`, baseline `ALB=336`. `shock = |z|`. `entry_z >= 1.5` -> if `z > 0` (high dispersion-entropy/irregularity shock) fade short (-1), if `z < 0` (low-entropy/order shock) fade long (+1); `exit_z < 0.5` or `max_hold=24` or flip. Execution `t -> t+1` (no lookahead). Apply only where real volume/spot bars exist.
4. **WF/costs/B&H (exact):** WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]` (bps fee, bps slippage), B&H same OOS windows. Real data only; full provenance + sha256.
5. Run and emit: `reports/real_quote_volume_dispersion_entropy_shock_mr_costed_oos_<UTC>.json`.

#### Step 2 — Registry + ingest evidence + pytest + summary (MANDATORY)
1. Nonspot ingest evidence: emit `reports/real_feed_ingest_attempt_<UTC>.json` (FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT if none; record searched patterns + found_real_artifacts=[]). Does NOT block R-B.
2. Pytest: `python3 -m pytest tests/ -q` (record counts/rc; if pytest missing record fail-closed note, do not fabricate).
3. Registry: emit `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T000254Z.json` (sha `d8a2a826...`), include C104-C109 (carry C104-C108, add C109). Set `edge_claim: NONE` unless edge rule holds.
4. Summary: emit `reports/campaign109_execution_summary_<UTC>.json` (artifacts + sha256s + nonspot blocker + edge claim + next campaign).

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- **No status summary before >= 3 new concrete report artifacts exist for C109** (C109 OOS report + ingest attempt + registry/summary — ensure >=3 new).
- **Heavy work mandatory:** implement + run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- C108 marked DONE with artifact SHAs; C107/C104-C106 locked — no reruns.
- Distinct C109 hypothesis pre-stated (Dispersion Entropy, NCDF+c=6,m=2,d=1) + grep-verify step — prevents duplicate-family waste.
- Nonspot ingest explicitly decoupled from R-B — prevents blocker-loop paralysis.
- "No status before >=3 new artifacts" + mandatory implementation/run — forces heavy work.
- Fallback ladder if C109 already exists: `VOLUME_BUBBLE_ENTROPY_SHOCK_MR` → `VOLUME_SVD_ENTROPY_SHOCK_MR` → `VOLUME_FISHER_INFORMATION_SHOCK_MR` → `VOLUME_ATTENTION_ENTROPY_SHOCK_MR` (grep-verify each) — no stalling.

### Immediate first action (do this in order)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "dispersion_entropy\|DISPERSION_ENTROPY\|DispEn" scripts/ reports/real_quote_volume_*dispersion* 2>&1 | head -15
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl 2>&1 | head
```
Then implement `scripts/run_real_quote_volume_dispersion_entropy_shock_mr_costed_oos.py` (C109 spec), run it, emit C109 OOS report, then Step 2 (ingest + pytest + registry + summary). **Do not stop until Step 2 complete with >=3 new C109 artifacts.**
