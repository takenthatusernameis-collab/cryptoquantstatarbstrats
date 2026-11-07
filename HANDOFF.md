# READ THIS FIRST — C135 INITIAL TASK (20261107T072710Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C134 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C134 DONE (20261107T072710Z):** `VOLUME_RQA_LAM_OVER_DET_RATIO_SHOCK_MR` (RQA ratio `RATIO_LAM_DET = %LAM/%DET`: laminarity / vertical-line fraction normalized by determinism / diagonal-line fraction; `%DET = (points in qualifying diagonal lines l>=l_min, main diagonal excluded)/(offdiag sum)`, `%LAM = (points in qualifying vertical lines l>=l_min, main diagonal excluded)/(offdiag sum)` over delay-embedded log-volume returns `m=2,tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`; fail-closed on `%DET<=0`/offdiag<=0/non-finite/degenerate/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_lam_over_det_ratio_shock_mr_costed_oos_20261107T072710Z.json` (sha256 `47828e281ce07ec115970851c5bcb33687414382efe804b9692a6501cb69fc6c`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=-0.9588038589960146`, `fee5_slip5=-1.7978038589960152`, `fee10_slip10=-2.6368038589960157`, `fee20_slip20=-4.314803858996015`, `fee40_slip40=-7.670803858996015`). RQA computed every 2 bars (causal forward-hold) for runtime — disclosed in params.
  - Script: `scripts/run_real_quote_volume_rqa_lam_over_det_ratio_shock_mr_costed_oos.py` (sha256 `ef7091c3420eb80542b4222e1b473207731fc18988cbcf6745d4e755ba4fc9d7`; `campaign:134`, `strategy_id: VOLUME_RQA_LAM_OVER_DET_RATIO_SHOCK_MR`, top-level gate fields).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T072710Z.json` (sha256 `9d554593bffa5abdb22143b1435d5d5f03de678aa9867f28f3ce148eed6e8ba3`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry superseding C133: `reports/strategy_edge_registry_20261107T072710Z.json` (sha256 `f09e6018b538197dece7e300e59b24220ffc03e82d2a401a578d318674c817fa`; supersedes `reports/strategy_edge_registry_20261107T071212Z.json` sha `dcb3712281d9cbfb19d9fcf71651d5aa89ab10281f564c708b4244beab92131d`; `edge_claim: NONE`; C134 entry appended).
  - Summary: `reports/campaign134_execution_summary_20261107T072710Z.json` (sha256 `7e247f6e02daeff6d5ef98c5c9d9e1d92a627ccc0e469c62c5e6b0eab7fbf99c`; SHAs from bytes on disk).
  - Distinctness (grep-verified pre-implementation, zero hits): `lam_over_det|lam_det_ratio|rqa_ratio_lam_det|LAM_OVER_DET` over `scripts/ strategies/ backtest/ utils/` returned 0 hits — distinct from C126 %DET and C128 %LAM (direct shocks) and C133 %DET/%RR (det/recurrence ratio); C134 trades %LAM/%DET.
  - C133 OOS ref: `reports/real_quote_volume_rqa_det_over_rr_ratio_shock_mr_costed_oos_20261107T071212Z.json` (sha256 `ee4e2bc22de6ef65b1c230927e85a3a5322873f2a34a082315680f405a730e80`).
  - Pytest: unavailable (`/usr/bin/python3: No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present (note: spot `.provenance.json` for that hash not present; C133/C134 used `.meta.json` + validated volume provenance).
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.
- State: `research_state/state.yaml` updated to C134 done / C135 next (20261107T072710Z).

## Bottlenecks removed (this handoff)
- C134 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C134 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T072710Z.json` (sha `f09e6018b538197dece7e300e59b24220ffc03e82d2a401a578d318674c817fa`).
- **C135 pre-selected (must grep-verify + disambiguate):** Primary candidate `VOLUME_RQA_VERT_HORIZ_LINE_MAX_RATIO_SHOCK_MR` — ratio `L_MAX_V / L_MAX` (max vertical / max diagonal line length) on delay-embedded log-volume returns, `m=2, tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`, fail-closed to NaN/no-signal when `L_MAX<=0` or undefined/non-finite/degenerate/zero off-diagonal recurrence. **Collision guard (REQUIRED):** C131 implemented `DIV=1/L_MAX` (diagonal max divergence) and C132 `DIV_V=1/L_MAX_V` (vertical max divergence); this trades the *ratio* `L_MAX_V/L_MAX` (laminar vs deterministic maximal structure) — grep MUST confirm no prior `vert_horiz_line_ratio|maxv_over_maxd|lmaxv_over_lmax|VERT_HORIZ_LINE_MAX_RATIO|LAM_MAX_OVER_DET_MAX` implementation before running. If any non-self hit exists, pick next distinct alternative: `VOLUME_RQA_LAM_OVER_RR_RATIO_SHOCK_MR` — ratio `%LAM/%RR` (laminarity normalized by recurrence density; distinct from C128 %LAM direct, C125 %RR direct, C133 %DET/%RR, C134 %LAM/%DET) with same RQA spec, fail-closed on `%RR<=0`/undefined; grep `lam_over_rr|lam_rr_ratio|rqa_ratio_lam_rr|LAM_OVER_RR`. If still colliding, choose another genuinely distinct RQA composite — **pre-state the chosen alternative, record grep-zero, and justify distinctness in OOS `pre_stated_distinctness`**.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C135 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C134 done — do NOT rerun. C135 is PENDING and must be executed.

### Step 0 — Readiness + distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
# primary candidate grep (must be 0 non-self before implementation); if not 0, apply collision guard and pick/verify alternative
grep -rn 'vert_horiz_line_ratio|maxv_over_maxd|lmaxv_over_lmax|VERT_HORIZ_LINE_MAX_RATIO|LAM_MAX_OVER_DET_MAX' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Record the grep result and the final chosen feature in the OOS `pre_stated_distinctness`.

### Step 1 — Run C135 (PRIORITY 1)
1. **Feature (pre-stated primary, grep-verified/disambiguated):** `VOLUME_RQA_VERT_HORIZ_LINE_MAX_RATIO_SHOCK_MR` (or verified alternative per collision guard). On `r_t = ln(v_t)-ln(v_{t-1})`, delay embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`. `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, `eps = 0.5*std(r_window)` fixed. Compute `L_MAX` = maximum qualifying diagonal line length (`l>=l_min=2`, main diagonal excluded) and `L_MAX_V` = maximum qualifying vertical line length (`l>=l_min=2`, main diagonal excluded). `RATIO_VH_MAX = L_MAX_V / L_MAX` (**fail-closed** to `NaN`/no-signal if `L_MAX<=0`, offdiag/undefined/non-finite/degenerate). Causal trailing only.
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. Use `RATIO_VH_MAX` as the feature. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_vert_horiz_line_max_ratio_shock_mr_costed_oos_<UTC>.json` (or alternative name) and corresponding script in `scripts/`. **Set correct `campaign:135` and `strategy_id` in emitted JSON and include top-level gate fields** (`oos_edge_proven`, `edge_claim`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`). Reference prior registry `reports/strategy_edge_registry_20261107T072710Z.json` (sha `f09e6018b538197dece7e300e59b24220ffc03e82d2a401a578d318674c817fa`) and C134 OOS sha `47828e281ce07ec115970851c5bcb33687414382efe804b9692a6501cb69fc6c`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T072710Z.json` (sha `f09e6018b538197dece7e300e59b24220ffc03e82d2a401a578d318674c817fa`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C133–C134 context and add C135 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign135_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C135 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete report artifacts exist for C135** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'vert_horiz_line_ratio|maxv_over_maxd|lmaxv_over_lmax|VERT_HORIZ_LINE_MAX_RATIO|LAM_MAX_OVER_DET_MAX' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then (if grep-zero / no collision) implement/run C135 (`VOLUME_RQA_VERT_HORIZ_LINE_MAX_RATIO_SHOCK_MR`, spec above) or the verified alternative; emit C135 OOS (correct campaign/strategy/top-level gates), then complete Step 2. **Do not stop until Step 2 complete with >=3 new C135 artifacts.**
