# READ THIS FIRST — C131 INITIAL TASK (20261107T065319Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C130 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C130 DONE (20261107T065053Z):** `VOLUME_RQA_RECURRENCE_ENTROPY_SHOCK_MR` (RQA recurrence entropy `ENTR = -Σ p(l) ln p(l)` over the Shannon distribution of **diagonal** recurrence line lengths `l>=l_min`, `p(l)=count(l)/N`, natural log, on delay-embedded log-volume returns; m=2,tau=1,eps=0.5*std,W_RR=168,l_min=2; fail-closed on degenerate/non-finite/zero-recurrence/N==0/undefined-entropy) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_recurrence_entropy_shock_mr_costed_oos_20261107T065053Z.json` (sha256 `9c1d8b38f90fca82cdb93269cdaf24fa531c211e2468a2aa47e0efd1f48ad326`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=-1.447763975116383`, `fee5_slip5=-2.630763975116384`, `fee10_slip10=-3.8137639751163848`, `fee20_slip20=-6.1797639751163835`, `fee40_slip40=-10.911763975116385`).
  - Script: `scripts/run_real_quote_volume_rqa_recurrence_entropy_shock_mr_costed_oos.py` (sha256 `8fa1ea708a720a61639a0cfc07c3f2a116c4dce6cab90a631ddcdabe5f9b16d9`; emits correct `campaign:130`, `strategy_id: VOLUME_RQA_RECURRENCE_ENTROPY_SHOCK_MR`, top-level gate fields `oos_edge_proven`/`edge_claim_top`/`any_exposure_oos`/`all_cost_slices_positive_oos_net_sum_top`/`all_cost_slices_beat_bh_mean_rule_top`/`cross_asset_oos_net_sums`).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T065319Z.json` (sha256 `c53c7d57d03f44195f34c1ab06643ec6a691f64c7abed030ede7de744d1f77b6`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry superseding C129: `reports/strategy_edge_registry_20261107T065319Z.json` (sha256 `b6447577552832216adc6e5882248454d49ec1c5e802239def183ce546cc5149`; supersedes `reports/strategy_edge_registry_20261107T062733Z.json` sha `434e1530cb282a045f4b80ef7c62fca385df3285b5d3fe3e37847c43f8e93d5c`; `edge_claim: NONE`; C130 entry appended).
  - Summary: `reports/campaign130_execution_summary_20261107T065319Z.json` (sha256 `2a1e4eb6df8baeec747226a78621e9068f19614c4b3739a3571aebbb8b4707e0`; SHAs from bytes on disk).
  - Distinctness (grep-verified pre-implementation): `recurrence_entropy|ENTR_RQA|diag_entropy|diagonal_entropy|rqa_entr` over `scripts/ strategies/ backtest/ utils/` returned 0 hits — no recurrence-entropy/ENTR implementation outside self-refs. Distinct from C125 %REC, C126 %DET, C127 L_MEAN, C128 %LAM, C129 TT, BDS, and C104–C124 families.
  - Pytest: unavailable (`/usr/bin/python3: No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C130 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C130 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T065319Z.json` (sha `b6447577…`).
- **C131 is pre-selected (pre-stated):** `VOLUME_RQA_MAXDIAGLINE_DIVERGENCE_SHOCK_MR` — RQA max diagonal line length `L_MAX` and its inverse divergence `DIV = 1/L_MAX` (divergence ≈ max-Lyapunov proxy) over qualifying **diagonal** recurrence lines `l>=l_min` (main diagonal excluded, both upper/lower k!=0), `eps = 0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`, delay embedding m=2,tau=1 on log-volume returns; fail-closed to NaN/no-signal on non-finite, degenerate std/eps, N==0, or undefined. Grep `l_max|max_diag|divergence|rqa_lmax|rqa_div|max_diagonal_line|max_line_length` over `scripts/ strategies/ backtest/ utils/` must return **0 hits** before implementation — reconfirm & record in OOS `pre_stated_distinctness`. Distinct from C125 %REC, C126 %DET, C127 L_MEAN (mean, not max), C128 %LAM, C129 TT, C130 ENTR — C131 measures the *extreme* diagonal-line length (longest predictable structure / divergence), not the mean or entropy. Distinct from permutation/sample/approx/SVD/spectral/wavelet/phase/Fisher/entropy families and BDS/C104–C124.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C131 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C130 done — do NOT rerun. C131 is PENDING and must be executed.

### Step 0 — Readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'l_max|max_diag|divergence|rqa_lmax|rqa_div|max_diagonal_line|max_line_length' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```

### Step 1 — Run C131 (PRIORITY 1)
1. **Feature (pre-stated, distinct, grep-verified):** `VOLUME_RQA_MAXDIAGLINE_DIVERGENCE_SHOCK_MR`. On `r_t = ln(v_t)-ln(v_{t-1})`, build delay embedding `X_i = (r_i, r_{i+tau})` with `m=2, tau=1` over trailing window `W_RR=168`. Recurrence matrix `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, else `0`; `eps = eps_scale * std(r_window)` with **pre-stated fixed** `eps_scale=0.5`. Find **diagonal** line lengths `l >= l_min`, `l_min=2` (pre-stated), excluding main diagonal (both upper/lower k!=0). `L_MAX = max(l)` over qualifying diagonal lines; `DIV = 1/L_MAX` (divergence; fail-closed to NaN/no-signal if `N==0` lines or `L_MAX<=0`). **Fail-closed** to `NaN`/no-signal on non-finite, degenerate std/eps, `N==0`, or undefined (state rule). Compute causally (rolling window).
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. Use `DIV` as the feature (divergence shocks). `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_maxdiagline_divergence_shock_mr_costed_oos_<UTC>.json` and `scripts/run_real_quote_volume_rqa_maxdiagline_divergence_shock_mr_costed_oos.py`. **Set correct `campaign:131` and `strategy_id` in emitted JSON and include top-level gate fields** (`oos_edge_proven`, `edge_claim`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`). Reference prior registry `reports/strategy_edge_registry_20261107T065319Z.json` (sha `b6447577552832216adc6e5882248454d49ec1c5e802239def183ce546cc5149`) and C130 OOS sha `9c1d8b38f90fca82cdb93269cdaf24fa531c211e2468a2aa47e0efd1f48ad326`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T065319Z.json` (sha `b6447577552832216adc6e5882248454d49ec1c5e802239def183ce546cc5149`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C124–C130 context and add C131 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign131_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C131 pre-selected above; reconfirm & record).
- **No status summary before >= 3 new concrete report artifacts exist for C131** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'l_max|max_diag|divergence|rqa_lmax|rqa_div|max_diagonal_line|max_line_length' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C131 (RQA max diagonal line length L_MAX / divergence DIV, spec above), emit C131 OOS (correct campaign/strategy/top-level gates), then complete Step 2. **Do not stop until Step 2 complete with >=3 new C131 artifacts.**
