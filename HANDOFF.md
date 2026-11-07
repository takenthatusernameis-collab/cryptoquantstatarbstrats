# READ THIS FIRST — C133 INITIAL TASK (20261107T070514Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C132 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C132 DONE (20261107T070514Z):** `VOLUME_RQA_MAXVERTLINE_DIVERGENCE_SHOCK_MR` (RQA max vertical line length `L_MAX_V` and divergence `DIV_V = 1/L_MAX_V` over qualifying **vertical** recurrence lines `l>=l_min`, main diagonal excluded, `l_min=2`, `eps = 0.5*std(r_window)` fixed, `W_RR=168`, delay embedding m=2,tau=1 on log-volume returns; fail-closed on degenerate/non-finite/zero-recurrence/N==0/L_MAX_V<=0/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_maxvertline_divergence_shock_mr_costed_oos_20261107T070514Z.json` (sha256 `602db16aa5d5874547b278ebd13b85772ea4ebfc236f8cd40e68cda76b5f3466`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=0.10311354933613992`, `fee5_slip5=-0.5068864506638606`, `fee10_slip10=-1.116886450663861`, `fee20_slip20=-2.3368864506638607`, `fee40_slip40=-4.77688645066386`).
  - Script: `scripts/run_real_quote_volume_rqa_maxvertline_divergence_shock_mr_costed_oos.py` (sha256 `ab151bc3cd181dfacb60bacbfd75259ee9e72e0e281825ca410bcede93136f1d`; emits correct `campaign:132`, `strategy_id: VOLUME_RQA_MAXVERTLINE_DIVERGENCE_SHOCK_MR`, top-level gate fields).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T070514Z.json` (sha256 `aaea583c3b02a0b2d9a18301d3a771dd35c4b42cae8c6f5b90d13944076281e7`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry superseding C131: `reports/strategy_edge_registry_20261107T070514Z.json` (sha256 `bcd7a44806e2a4e7bb01ce560a9dc275bb7314cd21bf0946b1693913721be3f0`; supersedes `reports/strategy_edge_registry_20261107T065559Z.json` sha `d45248d5de6fc4759e2ee0dfb1b8b9ab77fbde2089838d6da5d903a57558cc58`; `edge_claim: NONE`; C132 entry appended).
  - Summary: `reports/campaign132_execution_summary_20261107T070514Z.json` (sha256 `0dc035893f74a1bf10aa3a5ce608d9e2436dfe232948260bf33563e147f31460`; SHAs from bytes on disk).
  - Distinctness (grep-verified pre-implementation, self-only): `v_max|max_vert|vert_div|rqa_vmax|rqa_vdiv|max_vertical_line|max_vert_length|vertical_line_length` over `scripts/ strategies/ backtest/ utils/` returned 0 hits outside C132 script — no prior max-vertical-line/divergence implementation. Distinct from C125 %REC, C126 %DET, C127 L_MEAN (diagonal mean), C128 %LAM (vertical fraction), C129 TT (vertical mean), C130 ENTR (diagonal entropy), C131 DIV (diagonal max/divergence) — C132 measures the *extreme vertical-line length* (laminar/stuck divergence proxy), different orientation/statistic.
  - C131 OOS ref: `reports/real_quote_volume_rqa_maxdiagline_divergence_shock_mr_costed_oos_20261107T065559Z.json` (sha256 `d7433ccc04fbfbdf2639d6fdc26a96a3f1463268fd0cd5ec6b9a704b7ceac49c`).
  - Pytest: unavailable (`/usr/bin/python3: No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.
- State: `research_state/state.yaml` updated to C132 done / C133 next (20261107T070514Z).

## Bottlenecks removed (this handoff)
- C132 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C132 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T070514Z.json` (sha `bcd7a44806e2a4e7bb01ce560a9dc275bb7314cd21bf0946b1693913721be3f0`).
- **C133 pre-selected (must grep-verify + disambiguate):** Primary candidate `VOLUME_RQA_DET_OVER_RR_RATIO_SHOCK_MR` — ratio `RATIO_DET_RR = %DET / %RR` (diagonal-line predictability normalized by recurrence density) on delay-embedded log-volume returns, `m=2, tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`, fail-closed to NaN/no-signal when `%RR==0` or undefined/non-finite/degenerate. **Collision guard (REQUIRED):** C125 implemented `VOLUME_RQA_RECURRENCE_RATE_SHOCK_MR` (%RR shock) and C126 `VOLUME_RQA_DETERMINISM_SHOCK_MR` (%DET shock) — this is a *ratio of those quantities as the traded feature*; grep MUST confirm no prior `det_over_rr|det_rec_ratio|rqa_ratio_det_rec|%DET/%RR ratio feature/signal` implementation before running. If any non-self hit exists, pick the next distinct alternative: `VOLUME_RQA_LAM_OVER_DET_RATIO_SHOCK_MR` (`%LAM/%DET`) and grep `lam_over_det|lam_det_ratio|rqa_ratio_lam_det`; if still colliding, choose another genuinely distinct RQA composite (e.g., `VERT_HORIZ_LINE_MAX_RATIO` max-vertical/max-diagonal line length ratio, grep `vert_horiz_line_ratio|maxv_over_maxd`) — **pre-state the chosen alternative, record grep-zero, and justify distinctness in OOS `pre_stated_distinctness`**.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C133 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C132 done — do NOT rerun. C133 is PENDING and must be executed.

### Step 0 — Readiness + distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
# primary candidate grep (must be 0 non-self before implementation); if not 0, apply collision guard and pick/verify alternative
grep -rn 'det_over_rr\|det_rec_ratio\|rqa_ratio_det_rec\|ratio_det_rr\|DET_OVER_RR' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Record the grep result and the final chosen feature in the OOS `pre_stated_distinctness`.

### Step 1 — Run C133 (PRIORITY 1)
1. **Feature (pre-stated primary, grep-verified/disambiguated):** `VOLUME_RQA_DET_OVER_RR_RATIO_SHOCK_MR` (or verified alternative per collision guard). On `r_t = ln(v_t)-ln(v_{t-1})`, delay embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`. `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, `eps = 0.5*std(r_window)` fixed. Compute off-diagonal `%RR = (sum offdiag R)/(M*(M-1))`; compute `%DET = (sum of points in qualifying diagonal lines l>=l_min, main diagonal excluded)/(sum offdiag R)` with `l_min=2`. `RATIO_DET_RR = %DET / %RR` (or equivalent stable form `%DET/%RR` over off-diagonal base; **fail-closed** to `NaN`/no-signal if `%RR<=0`/non-finite/degenerate/undefined). Causal trailing only.
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. Use `RATIO_DET_RR` as the feature. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_det_over_rr_ratio_shock_mr_costed_oos_<UTC>.json` (or alternative name) and corresponding script in `scripts/`. **Set correct `campaign:133` and `strategy_id` in emitted JSON and include top-level gate fields** (`oos_edge_proven`, `edge_claim`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`). Reference prior registry `reports/strategy_edge_registry_20261107T070514Z.json` (sha `bcd7a44806e2a4e7bb01ce560a9dc275bb7314cd21bf0946b1693913721be3f0`) and C132 OOS sha `602db16aa5d5874547b278ebd13b85772ea4ebfc236f8cd40e68cda76b5f3466`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T070514Z.json` (sha `bcd7a44806e2a4e7bb01ce560a9dc275bb7314cd21bf0946b1693913721be3f0`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C124–C132 context and add C133 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign133_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C133 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete report artifacts exist for C133** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'det_over_rr\|det_rec_ratio\|rqa_ratio_det_rec\|ratio_det_rr\|DET_OVER_RR' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then (if grep-zero / no collision) implement/run C133 (`VOLUME_RQA_DET_OVER_RR_RATIO_SHOCK_MR`, spec above) or the verified alternative; emit C133 OOS (correct campaign/strategy/top-level gates), then complete Step 2. **Do not stop until Step 2 complete with >=3 new C133 artifacts.**
