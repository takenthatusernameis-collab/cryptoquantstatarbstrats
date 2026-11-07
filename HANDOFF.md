# READ THIS FIRST — C129 INITIAL TASK (20261107T061241Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C127 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C128 DONE (20261107T061014Z/061241Z):** `VOLUME_RQA_LAMINARITY_SHOCK_MR` (RQA laminarity `%LAM` — fraction of off-diagonal recurrence points forming vertical lines of length `l >= l_min` on delay-embedded log-volume returns; m=2,tau=1,eps=0.5*std,W_RR=168,l_min=2, column-wise vertical runs; main diagonal excluded from denominator; fail-closed on degenerate/non-finite/zero-recurrence/no-qualifying-vertical-lines) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_laminarity_shock_mr_costed_oos_20261107T061014Z.json` (sha256 `258016d68656db86ba699ef7527fc7d9ae5d41be34526b984705ca51bbb4f47a`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=-1.0476659289082004`, `fee5_slip5=-1.9066659289082013`, `fee10_slip10=-2.7656659289082017`, `fee20_slip20=-4.483665928908201`, `fee40_slip40=-7.9196659289082`).
  - Script: `scripts/run_real_quote_volume_rqa_laminarity_shock_mr_costed_oos.py` (sha256 `b082181e3d0bf76062318705a8347565ea2fcc8c5af4780d3d48746ad32aa89f` — computed from bytes on disk).
  - Pre-stated distinctness (grep-zero before run): `%LAM|laminarity|trapping_time|TT_mean|rqa_tt|vert_line` over `scripts/ strategies/ backtest/ utils/` — recorded in OOS. Distinct from C125 %REC (density), C126 %DET (diagonal-line fraction), C127 L_MEAN (diagonal mean length), BDS, C104–C124. Uses vertical recurrence structure (laminar/stuck states).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T061203Z.json` (sha256 `c1ac49fd2e83330ab39354373d2ae37e8944ea0a9d15e16dfbafb00052fe380d`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Summary: `reports/campaign128_execution_summary_20261107T061241Z.json` (sha256 `3513f7a968bd76700708193d1c12da03f649f1f32ca17be011ecf90f7dfbdb5e`, SHAs from bytes on disk).
  - **Latest registry (C128 included):** `reports/strategy_edge_registry_20261107T061222Z.json` (sha256 `39daf4a30c7973d7b9cabdf4bcf1950424670ff5db70f02a8df003ab937fe12c`; supersedes C127 `reports/strategy_edge_registry_20261107T060613Z.json` sha `7b38b7010f2a7beefaf023945c55f65958e69e3a28ba88ca14faf9497a12fd29`; 19 entries; `edge_claim: NONE`).
  - Pytest: unavailable (`No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C128 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C128 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T061222Z.json` (sha `39daf4a3…`).
- **C129 is pre-selected (pre-stated, grep-verified 20261107T061241Z):** `VOLUME_RQA_TRAPPING_TIME_SHOCK_MR` — RQA trapping time `TT` (average length of qualifying **vertical** lines, `TT = (Σ l_k over vertical lines with l>=l_min) / N_vertical_lines`) on delay-embedded log-volume returns. Grep `trapping_time|TT_RQA|mean_vertical|rqa_entr|recurrence_entropy|rec_entr|recurrence_time` over `scripts/ strategies/ backtest/ utils/` returned hits **only in C128's own script/docstring** (self-reference to prior grep terms), and **no trapping-time/TT implementation** exists — reconfirm & record in OOS `pre_stated_distinctness` (exclude C128 self-doc hits or document them explicitly; fail-closed if ambiguous). Distinct from C128 %LAM (vertical-line *fraction* of recurrence points) — C129 is the *average length* of qualifying vertical lines (a laminar-duration measure, not a density/fraction), and distinct from C125–C127/BDS/C104–C124. Uses vertical recurrence structure.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C129 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C128 done — do NOT rerun. C129 is PENDING and must be executed.

### Step 0 — Readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'trapping_time|TT_RQA|mean_vertical|rqa_entr|recurrence_entropy|rec_entr|recurrence_time' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```

### Step 1 — Run C129 (PRIORITY 1)
1. **Feature (pre-stated, distinct, grep-verified):** `VOLUME_RQA_TRAPPING_TIME_SHOCK_MR`. On `r_t = ln(v_t)-ln(v_{t-1})` (log-volume changes), build delay embedding `X_i = (r_i, r_{i+tau})` with `m=2, tau=1` over trailing window `W_RR=168`. Recurrence matrix `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, else `0`; `eps = eps_scale * std(r_window)` with **pre-stated fixed** `eps_scale=0.5`. Find **vertical** lines (column-wise runs of 1s) with length `l >= l_min`, `l_min=2` (pre-stated). `TT = (Σ l_k over qualifying vertical lines) / N_qualifying_vertical_lines`. **Fail-closed** to `NaN`/no-signal on non-finite, degenerate std/eps, zero recurrence, or no qualifying vertical lines (state rule explicitly). Compute causally (rolling window).
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_trapping_time_shock_mr_costed_oos_<UTC>.json` and `scripts/run_real_quote_volume_rqa_trapping_time_shock_mr_costed_oos.py`. Reference prior registry `reports/strategy_edge_registry_20261107T061222Z.json` (sha `39daf4a30c7973d7b9cabdf4bcf1950424670ff5db70f02a8df003ab937fe12c`) and C128 OOS sha `258016d68656db86ba699ef7527fc7d9ae5d41be34526b984705ca51bbb4f47a`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T061222Z.json` (sha `39daf4a30c7973d7b9cabdf4bcf1950424670ff5db70f02a8df003ab937fe12c`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C124–C128 context and add C129 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign129_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C129 pre-selected above; reconfirm & record).
- **No status summary before >= 3 new concrete report artifacts exist for C129** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'trapping_time|TT_RQA|mean_vertical|rqa_entr|recurrence_entropy|rec_entr|recurrence_time' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C129 (RQA trapping time TT, spec above), emit C129 OOS, then complete Step 2. **Do not stop until Step 2 complete with >=3 new C129 artifacts.**
