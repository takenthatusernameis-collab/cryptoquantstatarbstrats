## READ THIS FIRST — C113 INITIAL TASK (20261107T010340Z, produced after C112 completion; this session takes ownership of the durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104 DONE: `VOLUME_WAVELET_ENTROPY_SHOCK_MR` → `oos_edge_proven=false`.
- C105 DONE: `VOLUME_HURST_RS_PERSISTENCE_MR` → `oos_edge_proven=false`.
- C106 DONE: `VOLUME_SAMPLE_ENTROPY_SHOCK_MR` → `oos_edge_proven=false`. Do NOT rerun.
- C107 DONE: `VOLUME_PERMUTATION_ENTROPY_SHOCK_MR` → `oos_edge_proven=false`. Do NOT rerun.
- C108 DONE: `VOLUME_SLOPE_ENTROPY_SHOCK_MR` → `oos_edge_proven=false`. Do NOT rerun.
- C109 DONE: `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` → `oos_edge_proven=false`. Do NOT rerun.
- C110 DONE: `VOLUME_BUBBLE_ENTROPY_SHOCK_MR` → `oos_edge_proven=false`. Do NOT rerun.
- C111 DONE: `VOLUME_SVD_ENTROPY_SHOCK_MR` → `oos_edge_proven=false`. Do NOT rerun.
- **C112 DONE: `VOLUME_FISHER_INFORMATION_SHOCK_MR` (Fisher Information amplitude form on binned log-volume returns, W_FI=168, BINS=20, fade shocks vs ALB=336) → `reports/real_quote_volume_fisher_information_shock_mr_costed_oos_20261107T001916Z.json` (sha256 `893fe91b513dc5a7f41e6d6104ce8d6d7eaf4bcd764091abade13905782a30f6`), script `scripts/run_real_quote_volume_fisher_information_shock_mr_costed_oos.py` (sha256 `bc5430e543db920e0d5ab2ce9a9c5b50cb70592e510daa7f54d4b3686b3131a1`), `oos_edge_proven=false`. Step 2 artifacts emitted: ingest `reports/real_feed_ingest_attempt_20261107T001929Z.json`, registry `reports/strategy_edge_registry_20261107T001929Z.json` (supersedes `20261107T001705Z.json`), summary `reports/campaign112_execution_summary_20261107T001929Z.json`. Do NOT rerun.**
- Latest registry: `reports/strategy_edge_registry_20261107T001929Z.json` — includes C104-C112; `edge_claim: NONE`.
- Latest ingest evidence: `reports/real_feed_ingest_attempt_20261107T001929Z.json` — `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT`, `rb_unblocked=true`. **DOES NOT BLOCK R-B.**
- Real data preconditions OK: `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}` and spot cache `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- pytest: module NOT installed in this env (`python3 -m pytest` → `No module named pytest`); counts carried forward from lineage (928 passed/1 skipped/0 failed) — **record honestly, do not fabricate**.

### NEXT FOCUS CAMPAIGN — C113 R-B `VOLUME_ATTENTION_ENTROPY_SHOCK_MR` (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104-C112 are done — do NOT rerun. C113 is PENDING and must be executed. C113 (`VOLUME_ATTENTION_ENTROPY_SHOCK_MR`) is DISTINCT from C112 (`VOLUME_FISHER_INFORMATION_SHOCK_MR`): C112 uses Fisher Information (amplitude form, PMF binning); C113 uses Attention Entropy (softmax attention distribution entropy over log-volume returns within a rolling window). Do not substitute Fisher Information for C113.

#### Step 0 — Grep-verify distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "attention_entropy\|AttentionEntropy" scripts/ reports/ 2>&1 | head -20
# Expect: NO existing C113 attention-entropy OOS script/report.
ls scripts/run_real_quote_volume_attention_entropy* reports/real_quote_volume_attention_entropy* 2>&1 | head
# Expect: no matches. If any C113 attention-entropy report exists, STOP and advance to C114 (see fallback ladder).
```

#### Step 1 — Implement + run C113 `VOLUME_ATTENTION_ENTROPY_SHOCK_MR` (PRIORITY 1)
1. Create `scripts/run_real_quote_volume_attention_entropy_shock_mr_costed_oos.py` mirroring `scripts/run_real_quote_volume_fisher_information_shock_mr_costed_oos.py` structure (imports, wf_windows, load_spot/load_volume, run_asset, main, sha256, fail-closed), **campaign 113**.
2. **Feature (pre-stated, distinct):** rolling Attention Entropy over window `W_ATT=168` on log-volume returns `r_t = log(v_t/v_{t-1})`. Within each window, for each position i compute attention scores `a_ij = softmax(r_i * r_j)` over all j in the window (dot product of scalar returns). Attention entropy `H_i = -sum_j a_ij * log(a_ij + 1e-12)`. Window feature = mean of `H_i` across positions. Fail-closed: handle degenerate/zero-variance windows (return NaN). Distinct from C112 Fisher Information and all prior entropy/complexity families (SVD/bubble/dispersion/permutation/sample/approximate/spectral/wavelet/DFA/Hurst/slope/LZ/Petrosian/Higuchi/Katz/turning-point/variance-ratio/OU/BDS).
3. **Signal (fail-closed MR):** `z = (AttnEnt - ALB_mean) / ALB_std`, baseline `ALB=336`. `shock = |z|`. `entry_z >= 1.5` -> if `z > 0` (high attention entropy / diffuse-flat shock) fade short (-1), if `z < 0` (low attention entropy / concentrated-sharp shock) fade long (+1); `exit_z < 0.5` or `max_hold=24` or flip. Execution `t -> t+1` (no lookahead). Apply only where real volume/spot bars exist.
4. **WF/costs/B&H (exact):** WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]` (bps fee, bps slippage), B&H same OOS windows. Real data only; full provenance + sha256.
5. Run and emit: `reports/real_quote_volume_attention_entropy_shock_mr_costed_oos_<UTC>.json`.

#### Step 2 — Registry + ingest evidence + pytest + summary (MANDATORY)
1. Nonspot ingest evidence: emit `reports/real_feed_ingest_attempt_<UTC>.json` (FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT if none; record searched patterns + found_real_artifacts=[]). Does NOT block R-B.
2. Pytest: `python3 -m pytest tests/ -q` (record counts/rc; if pytest missing record fail-closed note, do not fabricate).
3. Registry: emit `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T001929Z.json`, include C104-C113 (carry C104-C112, add C113). Set `edge_claim: NONE` unless edge rule holds.
4. Summary: emit `reports/campaign113_execution_summary_<UTC>.json` (artifacts + sha256s + nonspot blocker + edge claim + next campaign).

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify not duplicated before implementation.
- **No status summary before >= 3 new concrete report artifacts exist for C113** (C113 OOS report + ingest attempt + registry/summary — ensure >=3 new).
- **Heavy work mandatory:** implement + run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- C112 marked DONE with artifact/script SHAs; C104-C111 locked — no reruns.
- C113 feature pre-stated as Attention Entropy (distinct from C112 Fisher Information) + grep-verify step — prevents duplicate-family waste and rerun of C112.
- Nonspot ingest explicitly decoupled from R-B — prevents blocker-loop paralysis.
- "No status before >=3 new artifacts" + mandatory implementation/run — forces heavy work.
- Fallback ladder if C113 already exists: `VOLUME_ATTENTION_ENTROPY_SHOCK_MR` → `VOLUME_INCREMENT_ENTROPY_SHOCK_MR` → `VOLUME_PERMUTATION_VARIANCE_SHOCK_MR` → `VOLUME_FLUCTUATION_COMPLEXITY_SHOCK_MR` (grep-verify each) — no stalling.

### Immediate first action (do this in order)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "attention_entropy\|AttentionEntropy" scripts/ reports/ 2>&1 | head -15
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl 2>&1 | head
```
Then implement `scripts/run_real_quote_volume_attention_entropy_shock_mr_costed_oos.py` (C113 spec), run it, emit C113 OOS report, then Step 2 (ingest + pytest + registry + summary). **Do not stop until Step 2 complete with >=3 new C113 artifacts.**