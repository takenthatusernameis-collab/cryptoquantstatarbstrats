# READ THIS FIRST — C134 INITIAL TASK (20261107T071212Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C133 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C133 DONE (20261107T071212Z):** `VOLUME_RQA_DET_OVER_RR_RATIO_SHOCK_MR` (RQA ratio `RATIO_DET_RR = %DET/%RR`: diagonal-line determinism normalized by off-diagonal recurrence density; `%RR = (offdiag sum)/(M*(M-1))`, `%DET = (points in qualifying diagonal lines l>=l_min, main diagonal excluded)/(offdiag sum)` over delay-embedded log-volume returns `m=2,tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`; fail-closed on `%RR<=0`/offdiag<=0/non-finite/degenerate/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_det_over_rr_ratio_shock_mr_costed_oos_20261107T071212Z.json` (sha256 `ee4e2bc22de6ef65b1c230927e85a3a5322873f2a34a082315680f405a730e80`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=1.3002789426043142`, `fee5_slip5=0.041278942604313085`, `fee10_slip10=-1.2177210573956874`, `fee20_slip20=-3.7357210573956867`, `fee40_slip40=-8.771721057395686`).
  - Script: `scripts/run_real_quote_volume_rqa_det_over_rr_ratio_shock_mr_costed_oos.py` (sha256 `445874a18f46ef80ca55608e97f0c0841747c19dcaf18b2f51849f1aa160a81d`; emits `campaign:133`, `strategy_id: VOLUME_RQA_DET_OVER_RR_RATIO_SHOCK_MR`, top-level gate fields).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T071021Z.json` (sha256 `21690356415b1c6adba8e09d6b8bde46a2302203eb00a4eb09810fdd6ad1f6e8`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry superseding C132: `reports/strategy_edge_registry_20261107T071212Z.json` (sha256 `dcb3712281d9cbfb19d9fcf71651d5aa89ab10281f564c708b4244beab92131d`; supersedes `reports/strategy_edge_registry_20261107T070514Z.json` sha `bcd7a44806e2a4e7bb01ce560a9dc275bb7314cd21bf0946b1693913721be3f0`; `edge_claim: NONE`; C133 entry appended).
  - Summary: `reports/campaign133_execution_summary_20261107T071212Z.json` (sha256 `1c9116a3b1b73e330f32ece63a7d75d3dd63319374ef16054f3c25424a4b64e2`; SHAs from bytes on disk).
  - Distinctness (grep-verified pre-implementation, zero hits): `det_over_rr|det_rec_ratio|rqa_ratio_det_rec|ratio_det_rr|DET_OVER_RR` over `scripts/ strategies/ backtest/ utils/` returned 0 hits — distinct from C125 %REC (direct %RR shock) and C126 %DET (direct %DET shock); C133 trades the *ratio* %DET/%RR. Distinct from C127-C132 (L_MEAN, %LAM, TT, ENTR, diagonal DIV/L_MAX, vertical DIV_V/L_MAX_V).
  - C132 OOS ref: `reports/real_quote_volume_rqa_maxvertline_divergence_shock_mr_costed_oos_20261107T070514Z.json` (sha256 `602db16aa5d5874547b278ebd13b85772ea4ebfc236f8cd40e68cda76b5f3466`).
  - Pytest: unavailable (`/usr/bin/python3: No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.
- State: `research_state/state.yaml` updated to C133 done / C134 next (20261107T071212Z).

## Bottlenecks removed (this handoff)
- C133 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C133 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T071212Z.json` (sha `dcb3712281d9cbfb19d9fcf71651d5aa89ab10281f564c708b4244beab92131d`).
- **C134 pre-selected (must grep-verify + disambiguate):** Primary candidate `VOLUME_RQA_LAM_OVER_DET_RATIO_SHOCK_MR` — ratio `%LAM/%DET` (laminarity / vertical-line fraction normalized by determinism / diagonal-line fraction) on delay-embedded log-volume returns, `m=2, tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`, fail-closed to NaN/no-signal when `%DET==0` or undefined/non-finite/degenerate/zero off-diagonal recurrence. **Collision guard (REQUIRED):** C126 implemented `%DET` shock and C128 `%LAM` shock; C133 implemented `%DET/%RR` ratio — this is a *different ratio* `%LAM/%DET` as the traded feature; grep MUST confirm no prior `lam_over_det|lam_det_ratio|rqa_ratio_lam_det|LAM_OVER_DET` implementation before running. If any non-self hit exists, pick the next distinct alternative: `VOLUME_RQA_VERT_HORIZ_LINE_MAX_RATIO_SHOCK_MR` — `L_MAX_V / L_MAX` (max vertical / max diagonal line length ratio) with `eps=0.5*std`, `m=2,tau=1,W_RR=168,l_min=2`, fail-closed on `L_MAX<=0`/undefined; grep `vert_horiz_line_ratio|maxv_over_maxd|lmaxv_over_lmax|VERT_HORIZ_LINE_MAX_RATIO`. If still colliding, choose another genuinely distinct RQA composite (e.g., `RR_TIMES_DET` normalized differently, or `%LAM/%RR`) — **pre-state the chosen alternative, record grep-zero, and justify distinctness in OOS `pre_stated_distinctness`**.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C134 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C133 done — do NOT rerun. C134 is PENDING and must be executed.

### Step 0 — Readiness + distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
# primary candidate grep (must be 0 non-self before implementation); if not 0, apply collision guard and pick/verify alternative
grep -rn 'lam_over_det\|lam_det_ratio\|rqa_ratio_lam_det\|LAM_OVER_DET' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Record the grep result and the final chosen feature in the OOS `pre_stated_distinctness`.

### Step 1 — Run C134 (PRIORITY 1)
1. **Feature (pre-stated primary, grep-verified/disambiguated):** `VOLUME_RQA_LAM_OVER_DET_RATIO_SHOCK_MR` (or verified alternative per collision guard). On `r_t = ln(v_t)-ln(v_{t-1})`, delay embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`. `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, `eps = 0.5*std(r_window)` fixed. Compute `%DET = (sum of points in qualifying diagonal lines l>=l_min, main diagonal excluded)/(sum offdiag R)` and `%LAM = (sum of points in qualifying vertical lines l>=l_min, main diagonal excluded)/(sum offdiag R)` with `l_min=2`. `RATIO_LAM_DET = %LAM / %DET` (**fail-closed** to `NaN`/no-signal if `%DET<=0`, offdiag sum<=0, non-finite, degenerate/undefined). Causal trailing only.
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. Use `RATIO_LAM_DET` as the feature. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_lam_over_det_ratio_shock_mr_costed_oos_<UTC>.json` (or alternative name) and corresponding script in `scripts/`. **Set correct `campaign:134` and `strategy_id` in emitted JSON and include top-level gate fields** (`oos_edge_proven`, `edge_claim`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`). Reference prior registry `reports/strategy_edge_registry_20261107T071212Z.json` (sha `dcb3712281d9cbfb19d9fcf71651d5aa89ab10281f564c708b4244beab92131d`) and C133 OOS sha `ee4e2bc22de6ef65b1c230927e85a3a5322873f2a34a082315680f405a730e80`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T071212Z.json` (sha `dcb3712281d9cbfb19d9fcf71651d5aa89ab10281f564c708b4244beab92131d`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C124–C133 context and add C134 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign134_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C134 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete report artifacts exist for C134** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'lam_over_det\|lam_det_ratio\|rqa_ratio_lam_det\|LAM_OVER_DET' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then (if grep-zero / no collision) implement/run C134 (`VOLUME_RQA_LAM_OVER_DET_RATIO_SHOCK_MR`, spec above) or the verified alternative; emit C134 OOS (correct campaign/strategy/top-level gates), then complete Step 2. **Do not stop until Step 2 complete with >=3 new C134 artifacts.**
