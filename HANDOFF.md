# READ THIS FIRST — C128 INITIAL TASK (20261107T060636Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C126 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C127 DONE (20261107T060312Z/060523Z):** `VOLUME_RQA_AVG_DIAGLINE_SHOCK_MR` (RQA average diagonal line length `L_MEAN` on delay-embedded log-volume returns; m=2,tau=1,eps=0.5*std,W_RR=168,l_min=2; main diagonal excluded, k!=0) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_avg_diagline_shock_mr_costed_oos_20261107T060312Z.json` (sha256 `e124581738988c773c80708222036bdb9409fa420032040647d204412c18886f`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=-1.4196963082265097`, `fee5_slip5=-2.6056963082265105`, `fee10_slip10=-3.791696308226511`, `fee20_slip20=-6.163696308226511`, `fee40_slip40=-10.90769630822651`).
  - Script: `scripts/run_real_quote_volume_rqa_avg_diagline_shock_mr_costed_oos.py` (sha256 `965d67540a2c6db0825f7ccab3f24e6caa7eed00834e7ca48c9a88dbb52daeb6`).
  - Pre-stated distinctness (grep-zero before run): `average_diagonal|L_MEAN|mean_diag_line|rqa_lmean|diag_line_mean` over `scripts/ strategies/ backtest/ utils/` — recorded in OOS. Distinct from C126 %DET (diagonal-line point fraction), C125 %REC (density), BDS, C104–C124.
  - Ingest: `reports/real_feed_ingest_attempt_20261107T060514Z.json` (sha256 `7155a54e17ac0f5f509c01427a5171afb773c6ccfaaace230e14b7c8c99561a8`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Summary: `reports/campaign127_execution_summary_20261107T060523Z.json` (sha256 `78e4bfde9fbe514214307f0031389ec68b662c9090aaff9b044737d891d59bc7`, SHAs from bytes on disk).
  - **Latest registry (C127 included):** `reports/strategy_edge_registry_20261107T060613Z.json` (sha256 `7b38b7010f2a7beefaf023945c55f65958e69e3a28ba88ca14faf9497a12fd29`; supersedes C126 `reports/strategy_edge_registry_20261107T060021Z.json` sha `650bab78db4aed4e8d18f71bcc53a945700f8c3fce75d6d78b4a7b429cf3fd79`; 18 entries; `edge_claim: NONE`).
  - Pytest: unavailable (`No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C127 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C127 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T060613Z.json` (sha `7b38b701…`).
- **C128 is pre-selected (pre-stated, grep-verified 20261107T060636Z):** `VOLUME_RQA_LAMINARITY_SHOCK_MR` — RQA laminarity `%LAM` (fraction of recurrence points forming vertical lines of length `l >= l_min`) on delay-embedded log-volume returns. Grep `%LAM|laminarity|trapping_time|TT_mean|rqa_tt|vert_line` over `scripts/ strategies/ backtest/ utils/` returned **zero hits** at selection (reconfirm & record in OOS `pre_stated_distinctness`). Distinct from C125 %REC (density), C126 %DET (diagonal-line fraction), C127 L_MEAN (diagonal mean length), BDS, and all C104–C124 families. Uses **vertical** recurrence structure (laminar/stuck states), not diagonal predictability.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C128 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C127 done — do NOT rerun. C128 is PENDING and must be executed.

### Step 0 — Readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn '%LAM|laminarity|trapping_time|TT_mean|rqa_tt|vert_line' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```

### Step 1 — Run C128 (PRIORITY 1)
1. **Feature (pre-stated, distinct, grep-verified):** `VOLUME_RQA_LAMINARITY_SHOCK_MR`. On `r_t = ln(v_t)-ln(v_{t-1})` (log-volume changes), build delay embedding `X_i = (r_i, r_{i+tau})` with `m=2, tau=1` over trailing window `W_RR=168`. Recurrence matrix `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, else `0`; `eps = eps_scale * std(r_window)` with **pre-stated fixed** `eps_scale=0.5`. Find **vertical** lines (column-wise runs of 1s) with length `l >= l_min`, `l_min=2` (pre-stated). `%LAM = (Σ l_k over qualifying vertical lines) / (total recurrence points in R)` (off-diagonal/main-diagonal handling must be stated consistently and fail-closed; prefer excluding main diagonal from numerator/denominator and document). **Fail-closed** to `NaN`/no-signal on non-finite, degenerate std/eps, zero recurrence, or no qualifying vertical lines (state rule explicitly). Compute causally (rolling window).
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_laminarity_shock_mr_costed_oos_<UTC>.json` and `scripts/run_real_quote_volume_rqa_laminarity_shock_mr_costed_oos.py`. Reference prior registry `reports/strategy_edge_registry_20261107T060613Z.json` (sha `7b38b7010f2a7beefaf023945c55f65958e69e3a28ba88ca14faf9497a12fd29`) and C127 OOS sha `e124581738988c773c80708222036bdb9409fa420032040647d204412c18886f`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T060613Z.json` (sha `7b38b7010f2a7beefaf023945c55f65958e69e3a28ba88ca14faf9497a12fd29`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C124–C127 context and add C128 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign128_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C128 pre-selected above; reconfirm & record).
- **No status summary before >= 3 new concrete report artifacts exist for C128** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn '%LAM|laminarity|trapping_time|TT_mean|rqa_tt|vert_line' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C128 (RQA laminarity %LAM, spec above), emit C128 OOS, then complete Step 2. **Do not stop until Step 2 complete with >=3 new C128 artifacts.**
