# READ THIS FIRST — C139 INITIAL TASK (20261107T081029Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

**Readiness verified 20261107T081029Z:** `numpy,scipy,pandas` importable; required caches present (`volume_1h_full.{pkl,provenance.json}`, `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`); pytest unavailable (honest, `No module named pytest`); C139 primary grep-zero in `scripts/ strategies/ backtest/ utils/`.

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C137 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C138 DONE (20261107T081029Z):** `VOLUME_RQA_DET_OVER_LAM_RATIO_SHOCK_MR` (RQA ratio `RATIO_DET_LAM = %DET/%LAM`, determinism normalized by laminarity, delay-embedded log-volume returns `m=2,tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`; fail-closed on `%LAM<=0`/offdiag<=0/non-finite/degenerate/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS (canonical corrected): `reports/real_quote_volume_rqa_det_over_lam_ratio_shock_mr_costed_oos_20261107T080909Z.json` (sha256 `77f3acea4e53ef3ea63ced8d26d68e5f1adc8883c4ad01aedec54d66849d47ca`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=1.221652275372969`, `fee5_slip5=0.4666522753729683`, `fee10_slip10=-0.28834772462703223`, `fee20_slip20=-1.7983477246270319`, `fee40_slip40=-4.818347724627031`). RQA computed every 2 bars (causal forward-hold) — disclosed. (An earlier 080433Z artifact had C137-copied metadata; compute logic was correct `%DET/%LAM`; corrected canonical emitted.)
  - Script: `scripts/run_real_quote_volume_rqa_det_over_lam_ratio_shock_mr_costed_oos.py` (sha256 `b331cc9d1aa3a3f2e346bf5b2675175398e0ad8dc475ceb900f1be6fa59d1046`; `campaign:138`, `strategy_id: VOLUME_RQA_DET_OVER_LAM_RATIO_SHOCK_MR`, top-level gate fields).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T080923Z.json` (sha256 `a4bd143a7cac6a2a7f4b970295a42adf1546e693051cb0e02a0966476d05c4c3`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry superseding C137: `reports/strategy_edge_registry_20261107T081009Z.json` (sha256 `ebca08c085d91a93ea29a6d33c414898cd0a06d74b9cf055de76bd971476f8e0`; supersedes `reports/strategy_edge_registry_20261107T080222Z.json` sha `0afcf580807f83dc82519ffbd8dac1283bb17621d2a813abad9ec33f8a73e5c3`; `edge_claim: NONE`; C136–C138 context/entries).
  - Summary: `reports/campaign138_execution_summary_20261107T081029Z.json` (sha256 `784e7b03be6f87c1678a9f1b40594a3600f767b4bd3eb2affbd87534a517af9a`; SHAs computed from bytes on disk; internal artifact SHAs verified).
  - Distinctness (grep-verified pre-implementation, zero non-self hits): `det_over_lam|det_lam_ratio|rqa_ratio_det_lam|DET_OVER_LAM` over `scripts/ strategies/ backtest/ utils/` returned 0 hits — distinct from C126 `%DET` direct, C128 `%LAM` direct, C133 `%DET/%RR`, C134 `%LAM/%DET` (inverse), C136 `%LAM/%RR`, C137 `%RR/%DET`; C138 trades ratio `%DET/%LAM`.
  - C137 OOS ref: `reports/real_quote_volume_rqa_rr_over_det_ratio_shock_mr_costed_oos_20261107T080021Z.json` (sha256 `0acefbc7dfdaf656291ffad9d6900f483800707bc7878c7f2503baa6a9414f37`).
  - Pytest: unavailable (`/usr/bin/python3: No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C138 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C138 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T081009Z.json` (sha `ebca08c085d91a93ea29a6d33c414898cd0a06d74b9cf055de76bd971476f8e0`).
- **C139 pre-selected (grep-VERIFIED 20261107T081029Z, zero hits in `scripts/ strategies/ backtest/ utils/`):** Primary candidate `VOLUME_RQA_RR_OVER_LAM_RATIO_SHOCK_MR` — ratio `%RR/%LAM` (recurrence density normalized by laminarity) on delay-embedded log-volume returns, `m=2, tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`, fail-closed to NaN/no-signal when `%LAM<=0` or undefined/non-finite/degenerate/zero off-diagonal recurrence. **Collision guard PASSED:** C125 `%RR` direct, C128 `%LAM` direct, C133 `%DET/%RR`, C134 `%LAM/%DET`, C136 `%LAM/%RR`, C137 `%RR/%DET`, C138 `%DET/%LAM`; this trades *ratio* `%RR/%LAM` — grep confirmed 0 hits for `rr_over_lam|rr_lam_ratio|rqa_ratio_rr_lam|RR_OVER_LAM`. If collision appears, pick next distinct alternative: `VOLUME_RQA_TT_OVER_DET_RATIO_SHOCK_MR` (`%TT/%DET`, trapping time normalized by determinism) — verify no `tt_over_det|tt_det_ratio` collision; fail-closed on `%DET<=0`. **Pre-state chosen alternative, record grep-zero, justify distinctness in OOS `pre_stated_distinctness`**.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C139 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C138 done — do NOT rerun. C139 is PENDING and must be executed.

### Step 0 — Readiness + distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
# primary candidate grep (must be 0 non-self before implementation); if not 0, apply collision guard and pick/verify alternative
grep -rn 'rr_over_lam\|rr_lam_ratio\|rqa_ratio_rr_lam\|RR_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Primary candidate expected distinct (grep-verified 20261107T081029Z); record grep result (or any alternative) in OOS `pre_stated_distinctness`.

### Step 1 — Run C139 (PRIORITY 1)
1. **Feature (pre-stated primary, grep-verified/disambiguated):** `VOLUME_RQA_RR_OVER_LAM_RATIO_SHOCK_MR` (or verified alternative per collision guard). On `r_t = ln(v_t)-ln(v_{t-1})`, delay embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`. `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, `eps = 0.5*std(r_window)` fixed. Compute `%RR = (offdiag recurrence sum)/(M*(M-1))` (or standard RQA %RR definition, keep consistent with prior codebase; fail-closed on offdiag/degenerate). Compute `%LAM = (points in qualifying vertical lines l>=l_min=2, main diagonal excluded)/(offdiag sum)`. `RATIO_RR_LAM = %RR / %LAM` (**fail-closed** to `NaN`/no-signal if `%LAM<=0`, offdiag/undefined/non-finite/degenerate). Causal trailing only.
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. Use `RATIO_RR_LAM` as the feature. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_rr_over_lam_ratio_shock_mr_costed_oos_<UTC>.json` (or alternative name) and corresponding script in `scripts/`. **Set correct `campaign:139` and `strategy_id` in emitted JSON and include top-level gate fields** (`oos_edge_proven`, `edge_claim`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`). Reference prior registry `reports/strategy_edge_registry_20261107T081009Z.json` (sha `ebca08c085d91a93ea29a6d33c414898cd0a06d74b9cf055de76bd971476f8e0`) and C138 OOS sha `77f3acea4e53ef3ea63ced8d26d68e5f1adc8883c4ad01aedec54d66849d47ca`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T081009Z.json` (sha `ebca08c085d91a93ea29a6d33c414898cd0a06d74b9cf055de76bd971476f8e0`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C137–C138 context and add C139 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign139_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C139 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete report artifacts exist for C139** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'rr_over_lam\|rr_lam_ratio\|rqa_ratio_rr_lam\|RR_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C139 (`VOLUME_RQA_RR_OVER_LAM_RATIO_SHOCK_MR`, primary, grep-verify before implementation) per spec; emit C139 OOS (correct `campaign:139`/`strategy_id`/top-level gates, include `pre_stated_distinctness` with grep evidence), then complete Step 2. **Do not stop until Step 2 complete with >=3 new C139 artifacts. No status-only response.**
