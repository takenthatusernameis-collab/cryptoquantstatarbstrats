# READ THIS FIRST — C130 INITIAL TASK (20261107T062733Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C128 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C129 DONE (20261107T062741Z/062733Z):** `VOLUME_RQA_TRAPPING_TIME_SHOCK_MR` (RQA trapping time `TT` — average length of qualifying **vertical** recurrence lines, `TT = (Σ l_k over vertical lines with l>=l_min) / N_vertical_lines`, on delay-embedded log-volume returns; m=2,tau=1,eps=0.5*std,W_RR=168,l_min=2; fail-closed on degenerate/non-finite/zero-recurrence/no-qualifying-vertical-lines) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS (normalized C129 labels/gates): `reports/real_quote_volume_rqa_trapping_time_shock_mr_costed_oos_20261107T062741Z_c129.json` (sha256 `e9bff8c9625689a129b09b6cedff349b484941151f1f1a76a49aea3c443afa04`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=-1.768691460072498`, `fee5_slip5=-2.5396914600724987`, `fee10_slip10=-3.310691460072499`, `fee20_slip20=-4.852691460072498`, `fee40_slip40=-7.936691460072498`).
  - Raw script-emitted OOS preserved (script JSON labeled campaign 128 in emitted fields; semantic C129 verified): `reports/real_quote_volume_rqa_trapping_time_shock_mr_costed_oos_20261107T062741Z.json` (sha256 `10703b923212881fad2d29ad40a93243e2fcb6ebe9ef97aa01ab81d9f1d9fb10`).
  - Script: `scripts/run_real_quote_volume_rqa_trapping_time_shock_mr_costed_oos.py` (sha256 `c71cef4c67af01699142f6bee8ff913e02902f8a80693efde58bbc8ce864b2de`).
  - Pre-stated distinctness (grep-verified): `trapping_time|TT_RQA|mean_vertical|rqa_entr|recurrence_entropy|rec_entr|recurrence_time` over `scripts/ strategies/ backtest/ utils/` returned 8 hits confined to `scripts/run_real_quote_volume_rqa_trapping_time_shock_mr_costed_oos.py` and `scripts/run_real_quote_volume_rqa_laminarity_shock_mr_costed_oos.py` (self/doc references) — no trapping-time/TT implementation outside self-refs. Distinct from C128 %LAM (vertical-line *fraction*) — C129 is *average length* of qualifying vertical lines (laminar duration), and distinct from C125–C127/BDS/C104–C124.
  - Ingest: `reports/real_feed_ingest_attempt_20261107T062733Z.json` (sha256 `7cc0ac4bb937f0e4967bca130255bfca47865d530826e396d6a3f2fc215d38d8`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Summary: `reports/campaign129_execution_summary_20261107T062733Z.json` (sha256 `27b425d19b0dbea712a86892e1209a4d0facb1c879b9c44a7a3657efee367eb2`, SHAs from bytes on disk).
  - **Latest registry (C129 included):** `reports/strategy_edge_registry_20261107T062733Z.json` (sha256 `434e1530cb282a045f4b80ef7c62fca385df3285b5d3fe3e37847c43f8e93d5c`; supersedes C128 `reports/strategy_edge_registry_20261107T061222Z.json` sha `39daf4a30c7973d7b9cabdf4bcf1950424670ff5db70f02a8df003ab937fe12c`; `edge_claim: NONE`).
  - Pytest: unavailable (`/usr/bin/python3: No module named pytest`) — recorded honestly; not fabricated.
  - **Caveat:** recent volume-RQA scripts emit `campaign:128` in raw JSON and gate/net-sum fields under `aggregate` (e.g., `cross_asset_sum_oos_net_sum`), not always top-level/cross_asset. Next script should set correct `campaign`/`strategy_id` and emit consistent top-level gate fields; preserve raw output and normalize if needed.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C129 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C129 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T062733Z.json` (sha `434e1530…`).
- **C130 is pre-selected (pre-stated, grep-verified 20261107T062733Z):** `VOLUME_RQA_RECURRENCE_ENTROPY_SHOCK_MR` — RQA recurrence entropy `ENTR` (Shannon entropy of the probability distribution of **diagonal** recurrence line lengths, `ENTR = -Σ p(l) ln p(l)` over diagonal lines with `l>=l_min`, `p(l)=count(l)/Σcount(l)`; natural log or consistent base pre-stated) on delay-embedded log-volume returns. Grep `recurrence_entropy|ENTR_RQA|diag_entropy|diagonal_entropy|rqa_entr` over `scripts/ strategies/ backtest/ utils/` returned **no hits** before implementation — reconfirm & record in OOS `pre_stated_distinctness`. Distinct from C125 %REC (density), C126 %DET (diagonal fraction), C127 L_MEAN (diagonal mean length), C128 %LAM (vertical fraction), C129 TT (vertical mean length) — C130 measures *complexity/uncertainty of the diagonal-line-length distribution*; distinct from permutation/sample/approx/SVD/spectral/wavelet/phase/Fisher/entropy families and BDS/C104–C124.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C130 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C129 done — do NOT rerun. C130 is PENDING and must be executed.

### Step 0 — Readiness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'recurrence_entropy|ENTR_RQA|diag_entropy|diagonal_entropy|rqa_entr' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```

### Step 1 — Run C130 (PRIORITY 1)
1. **Feature (pre-stated, distinct, grep-verified):** `VOLUME_RQA_RECURRENCE_ENTROPY_SHOCK_MR`. On `r_t = ln(v_t)-ln(v_{t-1})` (log-volume changes), build delay embedding `X_i = (r_i, r_{i+tau})` with `m=2, tau=1` over trailing window `W_RR=168`. Recurrence matrix `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, else `0`; `eps = eps_scale * std(r_window)` with **pre-stated fixed** `eps_scale=0.5`. Find **diagonal** line lengths `l >= l_min`, `l_min=2` (pre-stated). Let `n(l)` be count of diagonal lines of length `l`, `N=Σ n(l)`, `p(l)=n(l)/N`. `ENTR = -Σ_{l:l_min} p(l)*ln(p(l))` (natural log). **Fail-closed** to `NaN`/no-signal on non-finite, degenerate std/eps, `N==0`, or undefined entropy (state rule). Compute causally (rolling window).
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_recurrence_entropy_shock_mr_costed_oos_<UTC>.json` and `scripts/run_real_quote_volume_rqa_recurrence_entropy_shock_mr_costed_oos.py`. **Set correct `campaign:130` and `strategy_id` in emitted JSON and include top-level gate fields** (`oos_edge_proven`, `edge_claim`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`). Reference prior registry `reports/strategy_edge_registry_20261107T062733Z.json` (sha `434e1530cb282a045f4b80ef7c62fca385df3285b5d3fe3e37847c43f8e93d5c`) and C129 OOS sha `e9bff8c9625689a129b09b6cedff349b484941151f1f1a76a49aea3c443afa04`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T062733Z.json` (sha `434e1530cb282a045f4b80ef7c62fca385df3285b5d3fe3e37847c43f8e93d5c`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C124–C129 context and add C130 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign130_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C130 pre-selected above; reconfirm & record).
- **No status summary before >= 3 new concrete report artifacts exist for C130** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'recurrence_entropy|ENTR_RQA|diag_entropy|diagonal_entropy|rqa_entr' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C130 (RQA recurrence entropy ENTR, spec above), emit C130 OOS (correct campaign/strategy/top-level gates), then complete Step 2. **Do not stop until Step 2 complete with >=3 new C130 artifacts.**
