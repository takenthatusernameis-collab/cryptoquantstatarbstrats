## READ THIS FIRST — C116 INITIAL TASK (20261107T011622Z, produced after C115 completion; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

### Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

### Verified current state (do not rerun unchanged)
- C104-C114 DONE → `oos_edge_proven=false` (see registry chain). Do NOT rerun.
- **C115 DONE (20261107T011622Z):** `VOLUME_PERMUTATION_VARIANCE_SHOCK_MR` (Bandt-Pompe ordinal patterns `m=4`, `tau=1` over log-volume returns `r_t=log(v_t/v_{t-1})` within `W_PV=168`; PMF `p` over `m!` patterns, `PV_raw = Var(p)*24`, normalized by `(m!-1)/(m!)^2 = 23/576` to [0,1]-like and clipped; fail-closed on non-finite/degenerate windows; fade shocks vs `ALB=336`, `entry_z>=1.5`, `exit_z<0.5`, `max_hold=24`, exec `t->t+1`; WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS). Distinctness grep-verified before impl (`permutation_variance/PermutationVariance` absent in scripts/reports). Distinct from permutation-entropy families and C104-C114.
  - OOS: `reports/real_quote_volume_permutation_variance_shock_mr_costed_oos_20261107T011457Z.json` (sha256 `89fcc7ef8a3e46cca630c8c7ebe4f9f1daa6dfdc1f88541987b8f84f288ea807`) — **`oos_edge_proven=false`**.
  - Script: `scripts/run_real_quote_volume_permutation_variance_shock_mr_costed_oos.py` (sha256 `20906dbb527728755ad901e37682fd36ff510bb3c4e45cbdb1d3b76cbd23024c`).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T011622Z.json` (sha256 `665115ac33325fc667b14a274251c745f730b29737019828e48568a17f66a67c`) — `FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT`, `rb_unblocked=true`. **Does NOT block R-B.**
  - Registry: `reports/strategy_edge_registry_20261107T011622Z.json` (sha256 `8671a00563e585535bdd3631260fd2874ecd2cff731fface7cf250f16e06b647`, supersedes `20261107T011022Z` sha `ffcacca26a732efbab8ab908ed43aceb3cb4cecb3724960ea46117eacdbeeabe`) — `edge_claim: NONE`.
  - Summary: `reports/campaign115_execution_summary_20261107T011622Z.json` (sha256 `d0fded8821e4838600cc40bb813af938afaa77679d848d25ddcb27aa31dd425f`).
- Real data preconditions OK: `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` present.
- pytest: **not installed** in this env (`python3 -m pytest` → `No module named pytest`, rc=1). Record honestly; do not fabricate. Lineage counts carried forward (928 passed/1 skipped/0 failed).

### NEXT FOCUS CAMPAIGN — C116 R-B `VOLUME_FLUCTUATION_COMPLEXITY_SHOCK_MR` (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104-C115 done — do NOT rerun. C116 is PENDING and must be executed. `VOLUME_FLUCTUATION_COMPLEXITY_SHOCK_MR` must be DISTINCT from prior families (permutation variance, increment/attention/Fisher Information, SVD/bubble/dispersion/permutation-entropy sample/approximate/spectral/wavelet/DFA/Hurst/slope/LZ/Petrosian/Higuchi/Katz/turning-point/variance-ratio/OU/BDS, etc.). Grep-verify before impl.

#### Step 0 — Grep-verify distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "fluctuation_complexity\|FluctuationComplexity" scripts/ reports/ 2>&1 | head -20
ls scripts/run_real_quote_volume_fluctuation_complexity* reports/real_quote_volume_fluctuation_complexity* 2>&1 | head
# If any existing C116 fluctuation-complexity OOS script/report exists, STOP and advance to C117 fallback (VOLUME_RANGE_ENTROPY_SHOCK_MR).
```

#### Step 1 — Implement + run C116 `VOLUME_FLUCTUATION_COMPLEXITY_SHOCK_MR` (PRIORITY 1)
1. Create `scripts/run_real_quote_volume_fluctuation_complexity_shock_mr_costed_oos.py` mirroring `scripts/run_real_quote_volume_permutation_variance_shock_mr_costed_oos.py` (imports, wf_windows, load_spot/load_volume, run_asset, main, sha256, fail-closed), **campaign 116**.
2. **Feature (pre-stated, distinct):** rolling Fluctuation Complexity (FC) over `W_FC=168` on log-volume returns `r_t`. Quantize returns into `Q=10` equal-width bins over the window range (fail-closed on degenerate/zero-range/non-finite). Build adjacent-symbol transition matrix `T_{ij}=P(s_t=i, s_{t+1}=j)` and marginals `p_i=P(s_t=i)`. Compute FC as the Jensen–Shannon-like fluctuation complexity: `FC = sum_{i,j} T_{ij} * (log2(T_{ij}/p_i) - log2(T_{ij}/p_j))^?` — use the standard Bates & Shepard / Lamberti-style net-information-gain form: for transitions with `T_{ij}>0`, `fc_contrib = T_{ij} * (log(T_{ij}/p_i) - log(T_{ij}/p_j))^2` summed (or equivalently `sum T_{ij}*(log(p_j/p_i))^2` over observed transitions); normalize by a stable factor (e.g., `log(Q)^2` or max over window) and state normalization explicitly in artifact. Fail-closed on non-finite/degenerate.
3. **Signal (fail-closed MR):** `z = (FC - ALB_mean) / ALB_std`, `ALB=336`. `shock=|z|`. `entry_z >= 1.5` → `z > 0` fade short (-1), `z < 0` fade long (+1); `exit_z < 0.5` or `max_hold=24` or flip. Exec `t -> t+1` (no lookahead). Real volume/spot bars only.
4. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
5. Run and emit: `reports/real_quote_volume_fluctuation_complexity_shock_mr_costed_oos_<UTC>.json`.

#### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest: `reports/real_feed_ingest_attempt_<UTC>.json` (FAIL_CLOSED_BLOCKED_NO_REAL_ARTIFACT if none; searched patterns + found_real_artifacts=[]). Does NOT block R-B.
2. Pytest: `python3 -m pytest tests/ -q` (record rc/output honestly; do not fabricate).
3. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `strategy_edge_registry_20261107T011622Z.json` (sha `8671a00563e585535bdd3631260fd2874ecd2cff731fface7cf250f16e06b647`), include C111-C116. `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign116_execution_summary_<UTC>.json` (artifacts + sha256s + blocker + edge claim + next campaign).

### Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

### Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Reference `reports/real_feed_unblock_status_20261106T130243Z.json` and latest registry in outputs.
- Pre-state distinctness; grep-verify before implementation.
- **No status summary before >= 3 new concrete report artifacts exist for C116** (OOS + ingest + registry/summary — ensure >=3).
- **Heavy work mandatory:** implement + run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

### Bottlenecks removed (this handoff)
- C115 marked DONE with SHAs; C104-C114 locked — no reruns.
- C116 feature pre-stated + grep-verify — prevents duplicate-family waste.
- Nonspot ingest decoupled from R-B — prevents blocker-loop paralysis.
- "No status before >=3 new artifacts" + mandatory impl/run — forces heavy work.
- Fallback ladder if C116 exists: `VOLUME_FLUCTUATION_COMPLEXITY_SHOCK_MR` → `VOLUME_RANGE_ENTROPY_SHOCK_MR` → `VOLUME_CUMULATIVE_RESIDUAL_ENTROPY_SHOCK_MR` → `VOLUME_DISPERSION_ENTROPY_SHOCK_MR` (grep-verify each).

### Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rl "fluctuation_complexity\|FluctuationComplexity" scripts/ reports/ 2>&1 | head -15
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl 2>&1 | head
```
Then implement `scripts/run_real_quote_volume_fluctuation_complexity_shock_mr_costed_oos.py` (C116 spec), run it, emit OOS report, then Step 2. **Do not stop until Step 2 complete with >=3 new C116 artifacts.**
