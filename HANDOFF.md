## READ THIS FIRST — C115 INITIAL TASK (20261107T011235Z, produced after C114 completion; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104-C113 DONE → `oos_edge_proven=false` (see registry chain). Do NOT rerun.
- **C114 DONE (20261107T011022Z):** `VOLUME_INCREMENT_ENTROPY_SHOCK_MR` (normalized Shannon entropy of quantized increment symbols `d_t=r_t-r_{t-1}` over log-volume returns, `W_INC=168`, `Q=10` equal-width bins, norm `log(Q)`, fail-closed on degenerate/zero-range/non-finite; fade shocks vs `ALB=336`, `entry_z>=1.5`, `exit_z<0.5`, `max_hold=24`, exec `t->t+1`; WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS). Distinctness grep-verified before impl (`increment_entropy/IncrementEntropy` absent in scripts/reports).
  - OOS: `reports/real_quote_volume_increment_entropy_shock_mr_costed_oos_20261107T011021Z.json` (sha256 `de01ac8b96b8453ab728205d4d94e1939405d1b25f6bb43e91e2c307626d19d9`) — **`oos_edge_proven=false`**.
  - Script: `scripts/run_real_quote_volume_increment_entropy_shock_mr_costed_oos.py` (sha256 `e6718f9fd1ac4eb43d84b10acf96b444f8a2251ec9476ddf542ada414fdef140`).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T011022Z.json` (sha256 `d1d83d4633e4955925496708b9a8c68c5f159e3cb0c4d3bb00437c5e060de8e4`) — `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT`, `rb_unblocked=true`. **Does NOT block R-B.**
  - Registry: `reports/strategy_edge_registry_20261107T011022Z.json` (sha256 `ffcacca26a732efbab8ab908ed43aceb3cb4cecb3724960ea46117eacdbeeabe`, supersedes `20261107T010750Z` sha `0224302615240cf7303ecfae51c1b7b69857153916087473327bcfe3d86a01dd`) — `edge_claim: NONE`.
  - Summary: `reports/campaign114_execution_summary_20261107T011022Z.json` (sha256 `99cf0e1c2d75b97fbace44ff8147306b72a70847763418830b2ca9c9c3df309d`).
- Real data preconditions OK: `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- pytest: **not installed** in this env (`python3 -m pytest` → `No module named pytest`, rc=1). C114 recorded fail-closed note; lineage counts carried forward (928 passed/1 skipped/0 failed) — **record honestly, do not fabricate**.

### NEXT FOCUS CAMPAIGN — C115 R-B `VOLUME_PERMUTATION_VARIANCE_SHOCK_MR` (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104-C114 done — do NOT rerun. C115 is PENDING and must be executed. `VOLUME_PERMUTATION_VARIANCE_SHOCK_MR` must be DISTINCT from prior families (increment/attention/Fisher Information, SVD/bubble/dispersion/permutation-entropy sample/approximate/spectral/wavelet/DFA/Hurst/slope/LZ/Petrosian/Higuchi/Katz/turning-point/variance-ratio/OU/BDS, etc.). Grep-verify before impl.

#### Step 0 — Grep-verify distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "permutation_variance\|PermutationVariance" scripts/ reports/ 2>&1 | head -20
ls scripts/run_real_quote_volume_permutation_variance* reports/real_quote_volume_permutation_variance* 2>&1 | head
# If any existing C115 permutation-variance OOS script/report exists, STOP and advance to C116 fallback (VOLUME_FLUCTUATION_COMPLEXITY_SHOCK_MR).
```

#### Step 1 — Implement + run C115 `VOLUME_PERMUTATION_VARIANCE_SHOCK_MR` (PRIORITY 1)
1. Create `scripts/run_real_quote_volume_permutation_variance_shock_mr_costed_oos.py` mirroring `scripts/run_real_quote_volume_increment_entropy_shock_mr_costed_oos.py` (imports, wf_windows, load_spot/load_volume, run_asset, main, sha256, fail-closed), **campaign 115**.
2. **Feature (pre-stated, distinct):** rolling Permutation Variance over `W_PV=168` on log-volume returns `r_t`. Use embedding order `m=4`, delay `tau=1` (Bandt-Pompe ordinal patterns, `m!` patterns). For each window, obtain ordinal-pattern indices; compute PMF `p` over patterns and Permutation Variance `PV = Var(p) * m!` (or equivalently variance of pattern probabilities scaled to be comparable; normalize by `(m!-1)/(m!)^2` or `1/m!` as a stable [0,1]-like scale — state normalization explicitly in artifact; fail-closed on non-finite/degenerate). Distinct from permutation *entropy* families.
3. **Signal (fail-closed MR):** `z = (PV - ALB_mean) / ALB_std`, `ALB=336`. `shock=|z|`. `entry_z >= 1.5` → `z > 0` fade short (-1), `z < 0` fade long (+1); `exit_z < 0.5` or `max_hold=24` or flip. Exec `t -> t+1` (no lookahead). Real volume/spot bars only.
4. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
5. Run and emit: `reports/real_quote_volume_permutation_variance_shock_mr_costed_oos_<UTC>.json`.

#### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT if none; searched patterns + found_real_artifacts=[]). Does NOT block R-B.
2. Pytest: `python3 -m pytest tests/ -q` (record rc/output honestly; do not fabricate).
3. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T011022Z.json` (sha `ffcacca26a732efbab8ab908ed43aceb3cb4cecb3724960ea46117eacdbeeabe`), include C111-C115. `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign115_execution_summary_<UTC>.json` (artifacts + sha256s + blocker + edge claim + next campaign).

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify before implementation.
- **No status summary before >= 3 new concrete report artifacts exist for C115** (OOS + ingest + registry/summary — ensure >=3).
- **Heavy work mandatory:** implement + run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- C114 marked DONE with SHAs; C104-C113 locked — no reruns.
- C115 feature pre-stated + grep-verify — prevents duplicate-family waste.
- Nonspot ingest decoupled from R-B — prevents blocker-loop paralysis.
- "No status before >=3 new artifacts" + mandatory impl/run — forces heavy work.
- Fallback ladder if C115 exists: `VOLUME_PERMUTATION_VARIANCE_SHOCK_MR` → `VOLUME_FLUCTUATION_COMPLEXITY_SHOCK_MR` → `VOLUME_RANGE_ENTROPY_SHOCK_MR` → `VOLUME_CUMULATIVE_RESIDUAL_ENTROPY_SHOCK_MR` (grep-verify each).

### Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "permutation_variance\|PermutationVariance" scripts/ reports/ 2>&1 | head -15
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl 2>&1 | head
```
Then implement `scripts/run_real_quote_volume_permutation_variance_shock_mr_costed_oos.py` (C115 spec), run it, emit OOS report, then Step 2. **Do not stop until Step 2 complete with >=3 new C115 artifacts.**
