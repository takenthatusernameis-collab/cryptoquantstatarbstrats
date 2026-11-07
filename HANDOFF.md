# READ THIS FIRST — C136 INITIAL TASK (20261107T073351Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C135 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C135 DONE (20261107T073351Z):** `VOLUME_RQA_VERT_HORIZ_LINE_MAX_RATIO_SHOCK_MR` (RQA ratio `RATIO_VH_MAX = L_MAX_V/L_MAX`: max vertical / max diagonal qualifying line length, `l_min=2`, main diagonal excluded, over delay-embedded log-volume returns `m=2,tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`; fail-closed on `L_MAX<=0`/offdiag<=0/non-finite/degenerate/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_vert_horiz_line_max_ratio_shock_mr_costed_oos_20261107T073351Z.json` (sha256 `880b3ad88c4ccaf41a1cb83c763e68055243ff07cdb49c4f25eb477fef3f62b3`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=-0.9236394459078964`, `fee5_slip5=-1.684639445907897`, `fee10_slip10=-2.445639445907897`, `fee20_slip20=-3.9676394459078974`, `fee40_slip40=-7.011639445907896`). RQA computed every 2 bars (causal forward-hold) — disclosed.
  - Script: `scripts/run_real_quote_volume_rqa_vert_horiz_line_max_ratio_shock_mr_costed_oos.py` (sha256 `06157da0bcd8c05c650f3bad78bb15b02d2a3f3747f41201d45c2f40d2bb9768`; `campaign:135`, `strategy_id: VOLUME_RQA_VERT_HORIZ_LINE_MAX_RATIO_SHOCK_MR`, top-level gate fields).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T073351Z.json` (sha256 `ac054477b816a8dfd5624811e9841422bc7c93b25d379c2db2dead686862be99`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry superseding C134: `reports/strategy_edge_registry_20261107T073351Z.json` (sha256 `6064587862ee3458a14ac23f552f48fac0c08500933330d377a581d7e4d4f77f`; supersedes `reports/strategy_edge_registry_20261107T072710Z.json` sha `f09e6018b538197dece7e300e59b24220ffc03e82d2a401a578d318674c817fa`; `edge_claim: NONE`; C135 entry appended).
  - Summary: `reports/campaign135_execution_summary_20261107T073351Z.json` (sha256 `5cc58481d7bed722e24ef289f44d5a7759d3a520b15212e90c899f02fa4f156f`; SHAs from bytes on disk).
  - Distinctness (grep-verified pre-implementation, zero non-self hits): `vert_horiz_line_ratio|maxv_over_maxd|lmaxv_over_lmax|VERT_HORIZ_LINE_MAX_RATIO|LAM_MAX_OVER_DET_MAX` over `scripts/ strategies/ backtest/ utils/` returned 0 hits (HANDOFF/state refs only repo-wide) — distinct from C131 `DIV=1/L_MAX` and C132 `DIV_V=1/L_MAX_V` (inverses) and C133/C134 point-density ratios; C135 trades maximal line-length ratio `L_MAX_V/L_MAX`.
  - C134 OOS ref: `reports/real_quote_volume_rqa_lam_over_det_ratio_shock_mr_costed_oos_20261107T072710Z.json` (sha256 `47828e281ce07ec115970851c5bcb33687414382efe804b9692a6501cb69fc6c`).
  - Pytest: unavailable (`/usr/bin/python3: No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.
- State: `research_state/state.yaml` updated to C135 done / C136 next (20261107T073351Z).

## Bottlenecks removed (this handoff)
- C135 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C135 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T073351Z.json` (sha `6064587862ee3458a14ac23f552f48fac0c08500933330d377a581d7e4d4f77f`).
- **C136 pre-selected (must grep-verify + disambiguate):** Primary candidate `VOLUME_RQA_LAM_OVER_RR_RATIO_SHOCK_MR` — ratio `%LAM/%RR` (laminarity normalized by recurrence density) on delay-embedded log-volume returns, `m=2, tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`, fail-closed to NaN/no-signal when `%RR<=0` or undefined/non-finite/degenerate/zero off-diagonal recurrence. **Collision guard (REQUIRED):** C125 trades `%RR` direct, C128 `%LAM` direct, C133 `%DET/%RR`, C134 `%LAM/%DET`; this trades *ratio* `%LAM/%RR` — grep MUST confirm no prior `lam_over_rr|lam_rr_ratio|rqa_ratio_lam_rr|LAM_OVER_RR` implementation before running. If any non-self hit exists, pick next distinct alternative: `VOLUME_RQA_RR_OVER_DET_RATIO_SHOCK_MR` — ratio `%RR/%DET` (recurrence density normalized by determinism; distinct from C125 %RR, C126 %DET, C133 %DET/%RR inverse form, C134 %LAM/%DET) same spec, fail-closed on `%DET<=0`; grep `rr_over_det|rr_det_ratio|rqa_ratio_rr_det|RR_OVER_DET`. If still colliding, choose another genuinely distinct RQA composite — **pre-state the chosen alternative, record grep-zero, and justify distinctness in OOS `pre_stated_distinctness`**.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C136 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C135 done — do NOT rerun. C136 is PENDING and must be executed.

### Step 0 — Readiness + distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
# primary candidate grep (must be 0 non-self before implementation); if not 0, apply collision guard and pick/verify alternative
grep -rn 'lam_over_rr|lam_rr_ratio|rqa_ratio_lam_rr|LAM_OVER_RR' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Record the grep result and the final chosen feature in the OOS `pre_stated_distinctness`.

### Step 1 — Run C136 (PRIORITY 1)
1. **Feature (pre-stated primary, grep-verified/disambiguated):** `VOLUME_RQA_LAM_OVER_RR_RATIO_SHOCK_MR` (or verified alternative per collision guard). On `r_t = ln(v_t)-ln(v_{t-1})`, delay embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`. `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, `eps = 0.5*std(r_window)` fixed. Compute `%RR = (offdiag recurrence sum) / (M*(M-1))`, `%LAM = (points in qualifying vertical lines l>=l_min=2, main diagonal excluded)/(offdiag sum)`. `RATIO_LAM_RR = %LAM / %RR` (**fail-closed** to `NaN`/no-signal if `%RR<=0`, offdiag/undefined/non-finite/degenerate). Causal trailing only.
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. Use `RATIO_LAM_RR` as the feature. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_lam_over_rr_ratio_shock_mr_costed_oos_<UTC>.json` (or alternative name) and corresponding script in `scripts/`. **Set correct `campaign:136` and `strategy_id` in emitted JSON and include top-level gate fields** (`oos_edge_proven`, `edge_claim`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`). Reference prior registry `reports/strategy_edge_registry_20261107T073351Z.json` (sha `6064587862ee3458a14ac23f552f48fac0c08500933330d377a581d7e4d4f77f`) and C135 OOS sha `880b3ad88c4ccaf41a1cb83c763e68055243ff07cdb49c4f25eb477fef3f62b3`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T073351Z.json` (sha `6064587862ee3458a14ac23f552f48fac0c08500933330d377a581d7e4d4f77f`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C134–C135 context and add C136 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign136_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C136 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete report artifacts exist for C136** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'lam_over_rr|lam_rr_ratio|rqa_ratio_lam_rr|LAM_OVER_RR' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then (if grep-zero / no collision) implement/run C136 (`VOLUME_RQA_LAM_OVER_RR_RATIO_SHOCK_MR`, spec above) or the verified alternative; emit C136 OOS (correct campaign/strategy/top-level gates), then complete Step 2. **Do not stop until Step 2 complete with >=3 new C136 artifacts.**
