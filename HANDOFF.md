# READ THIS FIRST — C141 INITIAL TASK (20261107T085403Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

**Readiness verified 20261107T085403Z:** `numpy,scipy,pandas` importable; required caches present (`volume_1h_full.{pkl,provenance.json}`, `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`); pytest unavailable (honest, `/usr/bin/python3: No module named pytest`); C141 primary candidate must be grep-zero in `scripts/ strategies/ backtest/ utils/` before implementation.

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C139 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C140 DONE (20261107T085403Z):** `VOLUME_RQA_RR_OVER_TT_RATIO_SHOCK_MR` (RQA ratio `RATIO_RR_TT = %RR/TT_mean`, recurrence density normalized by trapping time / mean vertical-line length, `l>=l_min` main-diagonal excluded; delay-embedded log-volume returns `m=2,tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`; fail-closed on `TT_mean<=0`/no qualifying vertical lines/offdiag<=0/degenerate/non-finite/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_rr_over_tt_ratio_shock_mr_costed_oos_20261107T085403Z.json` (sha256 `85a1780d7dd319bd248db2cfa2344de273ba1831f7d53d98dc63efeeff6ea7ad`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=-0.16059517212766627`, `fee5_slip5=-0.48659517212766656`, `fee10_slip10=-0.8125951721276666`, `fee20_slip20=-1.4645951721276664`, `fee40_slip40=-2.7685951721276667`). RQA computed every 2 bars (causal forward-hold) — disclosed.
  - Script: `scripts/run_real_quote_volume_rqa_rr_over_tt_ratio_shock_mr_costed_oos.py` (sha256 `2327347af4c59b085f160ae1fe9eb07e2f9bb95ebbd261fc284b00cfd84edfa5`; `campaign:140`, `strategy_id: VOLUME_RQA_RR_OVER_TT_RATIO_SHOCK_MR`, top-level gate fields).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T085403Z.json` (sha256 `803f9d709778c33c52c24bcbb803b3db7b3626c0eff89973ead9458ab6c91cae`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry superseding C139: `reports/strategy_edge_registry_20261107T085403Z.json` (sha256 `15e9bf32492dfb02a736746b70753362293d42ec184fb908dc4f1f376733c28d`; supersedes `reports/strategy_edge_registry_20261107T081548Z.json` sha `329b291627ff6b3236f2d14de1efff1c4d5ed20c8b558d826e5df4ac6055338c`; `edge_claim: NONE`; C137–C140 context/entries).
  - Summary: `reports/campaign140_execution_summary_20261107T085403Z.json` (sha256 `fb4eac95b231cb5d464e605b7577fc7996d445fa10d13d5e767b78838416e1fe`; SHAs computed from bytes on disk; internal artifact SHAs verified).
  - Distinctness (grep-verified pre-implementation, zero non-self hits): `rr_over_tt|rr_tt_ratio|rqa_ratio_rr_tt|RR_OVER_TT` over `scripts/ strategies/ backtest/ utils/` returned 0 hits — distinct from C125 `%RR` direct, C128 `%LAM`/TT-family direct (`rqa_trapping_time*` exists but ratio ID/feature distinct), C130 ENTR direct, C133–C139 RQA ratios (`%DET/%RR,%LAM/%DET,%LAM/%RR,%RR/%DET,%DET/%LAM,%RR/%LAM`); C140 trades ratio `%RR/TT_mean`.
  - C139 OOS ref: `reports/real_quote_volume_rqa_rr_over_lam_ratio_shock_mr_costed_oos_20261107T081548Z.json` (sha256 `3dcbe5b1c237d7fb5b87bc127084e2174806135f13b6f94fc9c0719d872530fd`).
  - Pytest: unavailable (`/usr/bin/python3: No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C140 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C140 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T085403Z.json` (sha `15e9bf32492dfb02a736746b70753362293d42ec184fb908dc4f1f376733c28d`).
- **C141 pre-selected (MUST grep-verify zero hits in `scripts/ strategies/ backtest/ utils/` before implementation):** Primary candidate `VOLUME_RQA_ENTR_OVER_RR_RATIO_SHOCK_MR` — ratio `ENTR / %RR` (RQA diagonal-line entropy ENTR normalized by recurrence rate) on delay-embedded log-volume returns, `m=2, tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`, fail-closed to NaN/no-signal when `%RR<=0`, no qualifying diagonal-line length distribution, ENTR undefined/non-finite, offdiag/recurrence degenerate, or undefined. **Collision guard (primary):** grep `entr_over_rr|entr_rr_ratio|rqa_ratio_entr_rr|ENTR_OVER_RR` must be 0 before implementation; distinct from C125 `%RR` direct, C130 ENTR direct, and C133–C140 RQA ratios (`%DET/%RR,%LAM/%DET,%LAM/%RR,%RR/%DET,%DET/%LAM,%RR/%LAM,%RR/TT`). If collision appears, pick next distinct alternative: `VOLUME_RQA_DET_OVER_TT_RATIO_SHOCK_MR` (`%DET/TT_mean`, fail-closed on `TT_mean<=0`/no qualifying vertical lines) — grep-verify `det_over_tt|det_tt_ratio|DET_OVER_TT` zero. Second alternative: `VOLUME_RQA_LAM_OVER_TT_RATIO_SHOCK_MR` (`%LAM/TT_mean`) — grep-verify `lam_over_tt|LAM_OVER_TT` zero. **Pre-state chosen alternative, record grep-zero, justify distinctness in OOS `pre_stated_distinctness`**.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C141 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C140 done — do NOT rerun. C141 is PENDING and must be executed.

### Step 0 — Readiness + distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
# primary candidate grep (must be 0 non-self before implementation); if not 0, apply collision guard and pick/verify alternative
grep -rn 'entr_over_rr\|entr_rr_ratio\|rqa_ratio_entr_rr\|ENTR_OVER_RR' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Record grep result (or any alternative) in OOS `pre_stated_distinctness`.

### Step 1 — Run C141 (PRIORITY 1)
1. **Feature (pre-stated primary, grep-verify/disambiguate):** `VOLUME_RQA_ENTR_OVER_RR_RATIO_SHOCK_MR` (or verified alternative per collision guard). On `r_t = ln(v_t)-ln(v_{t-1})`, delay embedding `X_i=(r_i,r_{i+tau})`, `m=2, tau=1`, trailing `W_RR=168`. `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, `eps = 0.5*std(r_window)` fixed. Compute `%RR = (offdiag recurrence sum)/(M*(M-1))` (M embedded points). Compute `ENTR` = Shannon entropy of the diagonal-line length distribution (qualifying diagonal lines `l>=l_min=2`, main diagonal excluded), using the standard RQA definition (normalized or raw Shannon entropy — pre-state which is used and keep fixed; fail-closed on empty/undefined distribution). **Fail-closed** to `NaN`/no-signal if `%RR<=0`, no qualifying diagonal-line lengths, ENTR undefined/non-finite, offdiag/recurrence degenerate. `RATIO_ENTR_RR = ENTR / %RR`. Causal trailing only.
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. Use `RATIO_ENTR_RR` (or chosen alternative ratio) as the feature. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_entr_over_rr_ratio_shock_mr_costed_oos_<UTC>.json` (or alternative name) and corresponding script in `scripts/`. **Set correct `campaign:141` and `strategy_id` in emitted JSON and include top-level gate fields** (`oos_edge_proven`, `edge_claim`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`). Reference prior registry `reports/strategy_edge_registry_20261107T085403Z.json` (sha `15e9bf32492dfb02a736746b70753362293d42ec184fb908dc4f1f376733c28d`) and C140 OOS sha `85a1780d7dd319bd248db2cfa2344de273ba1831f7d53d98dc63efeeff6ea7ad`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T085403Z.json` (sha `15e9bf32492dfb02a736746b70753362293d42ec184fb908dc4f1f376733c28d`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C138–C140 context and add C141 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign141_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C141 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete report artifacts exist for C141** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'entr_over_rr\|entr_rr_ratio\|rqa_ratio_entr_rr\|ENTR_OVER_RR' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C141 (primary `VOLUME_RQA_ENTR_OVER_RR_RATIO_SHOCK_MR`, grep-verify before implementation) per spec; emit C141 OOS (correct `campaign:141`/`strategy_id`/top-level gates, include `pre_stated_distinctness` with grep evidence), then complete Step 2. **Do not stop until Step 2 complete with >=3 new C141 artifacts. No status-only response.**
