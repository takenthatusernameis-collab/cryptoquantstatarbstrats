# READ THIS FIRST — C127 INITIAL TASK (20261107T060218Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C125 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C126 DONE (20261107T055735Z, Step 2 artifacts 20261107T060021Z):** `VOLUME_RQA_DETERMINISM_SHOCK_MR` (RQA %DET = diagonal-line recurrence fraction on delay-embedded log-volume returns; m=2,tau=1,eps=0.5*std,W_RR=168,l_min=2) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_determinism_shock_mr_costed_oos_20261107T055735Z.json` (sha256 `fa17cbb405d6839f2038e1a73905422741ebf211b2c3576ff789e9e8b5b42283`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; sums `fee0_slip0=-2.0807358291848397`, `fee5_slip5=-3.351735829184841`, `fee10_slip10=-4.622735829184841`, `fee20_slip20=-7.164735829184841`, `fee40_slip40=-12.24873582918484`).
  - Script: `scripts/run_real_quote_volume_rqa_determinism_shock_mr_costed_oos.py` (sha256 `b384ad5edfb378e59c6dd4e3665aa49e52631c8635ca3df7994f902e7631c24b`).
  - Pre-stated distinctness: grep `recurrence_determinism|%DET|laminarity|%LAM|rqa_det` over `scripts/ strategies/ backtest/ utils/` returned **zero hits** before C126 implementation (verified 20261107T050614Z, recorded in OOS). Distinct from C125 %REC (recurrence density; no diagonal-line structure), BDS correlation-integral dependence, and C104–C124 families.
  - Ingest: `reports/real_feed_ingest_attempt_20261107T060021Z.json` (sha256 `bd65fbcdaaf73f71c648c11a2bcb16da3fc84bb8cab10cf9653a95ab71cfea24`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry (latest, C126 included): `reports/strategy_edge_registry_20261107T060021Z.json` (sha256 `650bab78db4aed4e8d18f71bcc53a945700f8c3fce75d6d78b4a7b429cf3fd79`; supersedes C125 registry `20261107T050326Z` sha `afc423bfb3e50e3d7821ffd70f2f7539aef8eadd2714dfd075f1b526dd98766d`; `edge_claim: NONE`).
  - Summary: `reports/campaign126_execution_summary_20261107T060021Z.json` (sha256 `e12ac05f81fcde3461fd5e10312f366f249d5f9f1aff62ac213468503ab10d8e`, SHAs computed from bytes on disk).
  - Pytest: unavailable (`No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C126 marked DONE with disk-verified SHAs; C104–C126 locked — no reruns. Latest registry carried forward: `strategy_edge_registry_20261107T060021Z.json` (sha `650bab78…`).
- **C127 family pre-selected & grep-verified clean (20261107T060218Z):** `VOLUME_RQA_AVG_DIAGLINE_SHOCK_MR` — RQA average diagonal line length `L_MEAN` = (sum of lengths of all diagonal lines with `l >= l_min` in the recurrence matrix) / (count of such diagonal lines) on delay-embedded log-volume returns. Grep `average_diagonal|L_MEAN|mean_diag_line|rqa_lmean|diag_line_mean` over `scripts/ strategies/ backtest/ utils/` must return **zero implementation hits before run** (reconfirm & record in OOS `pre_stated_distinctness`; note self-references only after implementation). Distinct from C126 `%DET` (diagonal-line point fraction, not mean line length) and C125 `%REC` (density, no line structure); distinct from BDS and all C104–C124 families.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C127 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C126 done — do NOT rerun. C127 is PENDING and must be executed.

### Step 0 — Readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'average_diagonal|L_MEAN|mean_diag_line|rqa_lmean|diag_line_mean' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```

### Step 1 — Run C127 (PRIORITY 1)
1. **Feature (pre-stated, distinct, grep-verified):** `VOLUME_RQA_AVG_DIAGLINE_SHOCK_MR`. On `r_t = ln(v_t)-ln(v_{t-1})` (log-volume changes), build delay embedding `X_i = (r_i, r_{i+tau})` with `m=2, tau=1` over trailing window `W_RR=168`. Recurrence matrix `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, else `0`; `eps = eps_scale * std(r_window)` with **pre-stated fixed** `eps_scale=0.5`. Find diagonal lines (excluding main diagonal, both upper/lower `k!=0`) with length `l >= l_min`, `l_min=2` (pre-stated). `L_MEAN = (Σ l_k) / N_lines` over qualifying lines. **Fail-closed** to `NaN`/no-signal on non-finite, degenerate std/eps, zero recurrence, or no qualifying diagonal lines. Compute causally (rolling window).
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_avg_diagline_shock_mr_costed_oos_<UTC>.json` and `scripts/run_real_quote_volume_rqa_avg_diagline_shock_mr_costed_oos.py`. Reference prior registry `reports/strategy_edge_registry_20261107T060021Z.json` (sha `650bab78db4aed4e8d18f71bcc53a945700f8c3fce75d6d78b4a7b429cf3fd79`) and C126 OOS sha `fa17cbb405d6839f2038e1a73905422741ebf211b2c3576ff789e9e8b5b42283`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T060021Z.json` (sha `650bab78db4aed4e8d18f71bcc53a945700f8c3fce75d6d78b4a7b429cf3fd79`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C123–C126 and add C127 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign127_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C127 pre-selected above; reconfirm & record).
- **No status summary before >= 3 new concrete report artifacts exist for C127** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'average_diagonal|L_MEAN|mean_diag_line|rqa_lmean|diag_line_mean' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C127 (RQA average diagonal line length L_MEAN, spec above), emit C127 OOS, then complete Step 2. **Do not stop until Step 2 complete with >=3 new C127 artifacts.**
