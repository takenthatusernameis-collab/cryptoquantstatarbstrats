# READ THIS FIRST — C142 INITIAL TASK (20261107T090753Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

**Readiness re-verified 20261107T090753Z:** `numpy,scipy,pandas` importable; required caches present (`volume_1h_full.{pkl,provenance.json}`, `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`); pytest unavailable (honest, `/usr/bin/python3: No module named pytest`); C142 primary candidate grep-zero in `scripts/ strategies/ backtest/ utils/` before implementation.

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C141 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C141 DONE (20261107T090342Z):** `VOLUME_RQA_ENTR_OVER_RR_RATIO_SHOCK_MR` (RQA ratio `RATIO_ENTR_RR = ENTR/%RR`, diagonal-line entropy normalized by recurrence rate, `l>=l_min` main diagonal excluded / `k!=0`; raw Shannon entropy, natural log, **not** normalized by `ln(K)`, pre-stated fixed consistent with C130; delay-embedded log-volume returns `m=2,tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`; fail-closed on `%RR<=0`/no qualifying diagonal lines `N==0`/ENTR undefined/non-finite/offdiag-recurrence degenerate/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_entr_over_rr_ratio_shock_mr_costed_oos_20261107T090342Z.json` (sha256 `2c1513ac8bf1142d622f52c5e076fa44706ad728ceb786d9fd99b74f7b66d746`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=0.45336506664510956`, `fee5_slip5=0.0503650666451092`, `fee10_slip10=-0.3526349333548909`, `fee20_slip20=-1.1586349333548909`, `fee40_slip40=-2.7706349333548905`). RQA computed every 2 bars (causal forward-hold) — disclosed.
  - Script: `scripts/run_real_quote_volume_rqa_entr_over_rr_ratio_shock_mr_costed_oos.py` (sha256 `8066bf1797b31fb6d311915bd2c2b0913951a702821c215a9bde8a9491b053d5`; `campaign:141`, `strategy_id: VOLUME_RQA_ENTR_OVER_RR_RATIO_SHOCK_MR`, top-level gate fields).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T090342Z.json` (sha256 `af2839caaee45d39c915c6491ed6bb4a43ca461059eb1f44af0a6cb4c9695448`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry superseding C140: `reports/strategy_edge_registry_20261107T090342Z.json` (sha256 `0fcfc9410fadb171b621a959029dccb4ec891fc8dd2543d3f7c1db8252706fa4`; supersedes `reports/strategy_edge_registry_20261107T085403Z.json` sha `15e9bf32492dfb02a736746b70753362293d42ec184fb908dc4f1f376733c28d`; `edge_claim: NONE`; C137–C141 context/entries).
  - Summary: `reports/campaign141_execution_summary_20261107T090342Z.json` (sha256 `2f548fbadcf3f25676e7aed5a83cbf3a17b0a52584accc3c988ccbc51a6c8bc6`; SHAs computed from bytes on disk).
  - Distinctness (grep-verified pre-implementation, zero non-self hits): `entr_over_rr|entr_rr_ratio|rqa_ratio_entr_rr|ENTR_OVER_RR` over `scripts/ strategies/ backtest/ utils/` returned 0 hits — distinct from C125 `%RR` direct, C130 ENTR direct, and C133–C140 RQA ratios (`%DET/%RR,%LAM/%DET,%LAM/%RR,%RR/%DET,%DET/%LAM,%RR/%LAM,%RR/TT`); C141 trades ratio `ENTR/%RR`. Primary candidate used.
  - C140 OOS ref: `reports/real_quote_volume_rqa_rr_over_tt_ratio_shock_mr_costed_oos_20261107T085403Z.json` (sha256 `85a1780d7dd319bd248db2cfa2344de273ba1831f7d53d98dc63efeeff6ea7ad`).
  - Pytest: unavailable (`/usr/bin/python3: No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C141 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C141 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T090342Z.json` (sha `0fcfc9410fadb171b621a959029dccb4ec891fc8dd2543d3f7c1db8252706fa4`).
- **state.yaml was stale (updated 20261107T082011Z, claimed latest_campaign_done C139 / next C140). Sync it to authoritative state: latest_campaign_done C141, next_campaign C142, registry sha `0fcfc9410fadb171b621a959029dccb4ec891fc8dd2543d3f7c1db8252706fa4`.** Remove this stale-state bottleneck before/while executing C142.
- **C142 pre-selected (MUST grep-verify zero hits in `scripts/ strategies/ backtest/ utils/` before implementation):** Primary candidate `VOLUME_RQA_DET_OVER_TT_RATIO_SHOCK_MR` — ratio `%DET / TT_mean` (RQA diagonal-line determinism normalized by trapping time / mean vertical-line length) on delay-embedded log-volume returns, `m=2, tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`, fail-closed to NaN/no-signal when `TT_mean<=0`, no qualifying vertical lines, `%DET` undefined/non-finite, offdiag/recurrence degenerate, or undefined. **Collision guard (primary):** grep `det_over_tt|det_tt_ratio|rqa_ratio_det_tt|DET_OVER_TT` must be 0 before implementation; distinct from C126 `%DET` direct, C128/C129 `TT`/`%LAM`-family direct context, and C133–C141 RQA ratios (`%DET/%RR,%LAM/%DET,%LAM/%RR,%RR/%DET,%DET/%LAM,%RR/%LAM,%RR/TT,ENTR/%RR`). If collision appears, pick next distinct alternative: `VOLUME_RQA_LAM_OVER_TT_RATIO_SHOCK_MR` (`%LAM/TT_mean`, fail-closed on `TT_mean<=0`/no qualifying vertical lines) — grep-verify `lam_over_tt|lam_tt_ratio|LAM_OVER_TT` zero. Second alternative: `VOLUME_RQA_ENTR_OVER_DET_RATIO_SHOCK_MR` (`ENTR/%DET`, fail-closed on `%DET<=0`/no qualifying diagonal lines; raw Shannon ENTR natural log, not normalized by `ln(K)`, pre-stated fixed consistent with C130) — grep-verify `entr_over_det|ENTR_OVER_DET` zero. **Pre-state chosen alternative, record grep-zero, justify distinctness in OOS `pre_stated_distinctness`**.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C142 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C141 done — do NOT rerun. C142 is PENDING and must be executed.

### Step 0 — Readiness + distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
# primary candidate grep (must be 0 non-self before implementation); if not 0, apply collision guard and pick/verify alternative
grep -rn 'det_over_tt\|det_tt_ratio\|rqa_ratio_det_tt\|DET_OVER_TT' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
# sync stale state.yaml to authoritative C141-done / C142-next state
```
Record grep result (or any alternative) in OOS `pre_stated_distinctness`.

### Step 1 — Run C142 (PRIORITY 1)
1. **Feature (pre-stated primary, grep-verify/disambiguate):** `VOLUME_RQA_DET_OVER_TT_RATIO_SHOCK_MR` (or verified alternative per collision guard). On `r_t = ln(v_t)-ln(v_{t-1})`, delay embedding `X_i=(r_i,r_{i+tau})`, `m=2, tau=1`, trailing `W_RR=168`. `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, `eps = 0.5*std(r_window)` fixed. Compute `%DET = (sum of diagonal-line points for qualifying diagonal lines l>=l_min=2, main diagonal excluded, k!=0) / (offdiag recurrence sum)` (or standard RQA %DET definition — pre-state which is used and keep fixed; fail-closed on offdiag/recurrence sum <= 0 or undefined). Compute `TT_mean` = mean length of qualifying vertical lines (`l>=l_min=2`, main diagonal excluded) — RQA trapping time notion. **Fail-closed** to `NaN`/no-signal if `TT_mean<=0`, no qualifying vertical lines, `%DET` undefined/non-finite, offdiag/recurrence degenerate, or undefined. `RATIO_DET_TT = %DET / TT_mean`. Causal trailing only.
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. Use `RATIO_DET_TT` (or chosen alternative ratio) as the feature. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_det_over_tt_ratio_shock_mr_costed_oos_<UTC>.json` (or alternative name) and corresponding script in `scripts/`. **Set correct `campaign:142` and `strategy_id` in emitted JSON and include top-level gate fields** (`oos_edge_proven`, `edge_claim`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`). Reference prior registry `reports/strategy_edge_registry_20261107T090342Z.json` (sha `0fcfc9410fadb171b621a959029dccb4ec891fc8dd2543d3f7c1db8252706fa4`) and C141 OOS sha `2c1513ac8bf1142d622f52c5e076fa44706ad728ceb786d9fd99b74f7b66d746`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T090342Z.json` (sha `0fcfc9410fadb171b621a959029dccb4ec891fc8dd2543d3f7c1db8252706fa4`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C138–C141 context and add C142 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign142_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C142 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete report artifacts exist for C142** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'det_over_tt\|det_tt_ratio\|rqa_ratio_det_tt\|DET_OVER_TT' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C142 (primary `VOLUME_RQA_DET_OVER_TT_RATIO_SHOCK_MR`, grep-verify before implementation) per spec; emit C142 OOS (correct `campaign:142`/`strategy_id`/top-level gates, include `pre_stated_distinctness` with grep evidence), then complete Step 2. **Do not stop until Step 2 complete with >=3 new C142 artifacts. No status-only response.**
