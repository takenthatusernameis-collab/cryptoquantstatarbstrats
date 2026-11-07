# READ THIS FIRST — C137 INITIAL TASK (20261107T075536Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

**Readiness verified 20261107T075708Z:** `numpy,scipy,pandas` importable; required caches present (`volume_1h_full.{pkl,provenance.json}`, `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`); pytest unavailable (honest); C137 primary grep-zero in `scripts/ strategies/ backtest/ utils/`; git clean.

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C135 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C136 DONE (20261107T075344Z):** `VOLUME_RQA_LAM_OVER_RR_RATIO_SHOCK_MR` (RQA ratio `RATIO_LAM_RR = %LAM/%RR`, laminarity normalized by recurrence density, delay-embedded log-volume returns `m=2,tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`; fail-closed on `%RR<=0`/offdiag<=0/non-finite/degenerate/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_lam_over_rr_ratio_shock_mr_costed_oos_20261107T075344Z.json` (sha256 `1e9e562d79d561b4266f6bb3bf5fe447e99668787f76d63519af1cb7b57b99cc`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=-0.5457203642045207`, `fee5_slip5=-1.3637203642045215`, `fee10_slip10=-2.181720364204522`, `fee20_slip20=-3.8177203642045217`, `fee40_slip40=-7.0897203642045215`). RQA computed every 2 bars (causal forward-hold) — disclosed.
  - Script: `scripts/run_real_quote_volume_rqa_lam_over_rr_ratio_shock_mr_costed_oos.py` (sha256 `9ace00977e21551cf071eafe8bcdafeefb02469e2abf60b613233101d80d5d2f`; `campaign:136`, `strategy_id: VOLUME_RQA_LAM_OVER_RR_RATIO_SHOCK_MR`, top-level gate fields).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T075344Z.json` (sha256 `ce00bee8007a0b165e0cbeb88f932606e211dd6c4fa1e2162e2c1ab881dbf89e`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry superseding C135: `reports/strategy_edge_registry_20261107T075344Z.json` (sha256 `0c199afadd2a2aea7032bacef2997622402e883567d36d48153dd1376c033b3d`; supersedes `reports/strategy_edge_registry_20261107T073351Z.json` sha `6064587862ee3458a14ac23f552f48fac0c08500933330d377a581d7e4d4f77f`; `edge_claim: NONE`; C136 entry appended).
  - Summary: `reports/campaign136_execution_summary_20261107T075344Z.json` (sha256 `0a789a55ae2076a77190c480eaf52bc0dc04a607a67e00442b53e4f58f2d7cf1`; SHAs from bytes on disk).
  - Distinctness (grep-verified pre-implementation, zero non-self hits): `lam_over_rr|lam_rr_ratio|rqa_ratio_lam_rr|LAM_OVER_RR` over `scripts/ strategies/ backtest/ utils/` returned 0 hits (HANDOFF/state refs only repo-wide) — distinct from C125 `%RR` direct, C128 `%LAM` direct, C133 `%DET/%RR`, C134 `%LAM/%DET`; C136 trades laminarity/recurrence-density ratio `%LAM/%RR`.
  - C135 OOS ref: `reports/real_quote_volume_rqa_vert_horiz_line_max_ratio_shock_mr_costed_oos_20261107T073351Z.json` (sha256 `880b3ad88c4ccaf41a1cb83c763e68055243ff07cdb49c4f25eb477fef3f62b3`).
  - Pytest: unavailable (`/usr/bin/python3: No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.
- State: `research_state/state.yaml` updated to C136 done / C137 next (20261107T075536Z).

## Bottlenecks removed (this handoff)
- C136 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C136 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T075344Z.json` (sha `0c199afadd2a2aea7032bacef2997622402e883567d36d48153dd1376c033b3d`).
- **C137 pre-selected (grep-VERIFIED 20261107T075708Z, zero non-self hits in `scripts/ strategies/ backtest/ utils/`):** Primary candidate `VOLUME_RQA_RR_OVER_DET_RATIO_SHOCK_MR` — ratio `%RR/%DET` (recurrence density normalized by determinism) on delay-embedded log-volume returns, `m=2, tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`, fail-closed to NaN/no-signal when `%DET<=0` or undefined/non-finite/degenerate/zero off-diagonal recurrence. **Collision guard PASSED:** C125 trades `%RR` direct, C126 `%DET` direct, C133 `%DET/%RR` (inverse form), C134 `%LAM/%DET`, C136 `%LAM/%RR`; this trades *ratio* `%RR/%DET` — grep confirmed 0 hits for `rr_over_det|rr_det_ratio|rqa_ratio_rr_det|RR_OVER_DET`. If a future agent sees a collision, pick next distinct alternative: `VOLUME_RQA_TRAPPING_TIME_RATIO_SHOCK_MR` — verify no `trapping_time_ratio|tt_ratio` collision; same spec, fail-closed. **Pre-state chosen alternative, record grep-zero, justify distinctness in OOS `pre_stated_distinctness`**.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C137 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C136 done — do NOT rerun. C137 is PENDING and must be executed.

### Step 0 — Readiness + distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
# primary candidate grep (must be 0 non-self before implementation); if not 0, apply collision guard and pick/verify alternative
grep -rn 'rr_over_det|rr_det_ratio|rqa_ratio_rr_det|RR_OVER_DET' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head  # verified 0 hits 20261107T075708Z
```
Primary candidate verified distinct; record grep result (or any alternative) in OOS `pre_stated_distinctness`.

### Step 1 — Run C137 (PRIORITY 1)
1. **Feature (pre-stated primary, grep-verified/disambiguated):** `VOLUME_RQA_RR_OVER_DET_RATIO_SHOCK_MR` (or verified alternative per collision guard). On `r_t = ln(v_t)-ln(v_{t-1})`, delay embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`. `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, `eps = 0.5*std(r_window)` fixed. Compute `%RR = (offdiag recurrence sum) / (M*(M-1))`, `%DET = (points in qualifying diagonal lines l>=l_min=2, main diagonal excluded)/(offdiag sum)`. `RATIO_RR_DET = %RR / %DET` (**fail-closed** to `NaN`/no-signal if `%DET<=0`, offdiag/undefined/non-finite/degenerate). Causal trailing only.
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. Use `RATIO_RR_DET` as the feature. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_rr_over_det_ratio_shock_mr_costed_oos_<UTC>.json` (or alternative name) and corresponding script in `scripts/`. **Set correct `campaign:137` and `strategy_id` in emitted JSON and include top-level gate fields** (`oos_edge_proven`, `edge_claim`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`). Reference prior registry `reports/strategy_edge_registry_20261107T075344Z.json` (sha `0c199afadd2a2aea7032bacef2997622402e883567d36d48153dd1376c033b3d`) and C136 OOS sha `1e9e562d79d561b4266f6bb3bf5fe447e99668787f76d63519af1cb7b57b99cc`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T075344Z.json` (sha `0c199afadd2a2aea7032bacef2997622402e883567d36d48153dd1376c033b3d`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C135–C136 context and add C137 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign137_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C137 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete report artifacts exist for C137** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'rr_over_det|rr_det_ratio|rqa_ratio_rr_det|RR_OVER_DET' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C137 (`VOLUME_RQA_RR_OVER_DET_RATIO_SHOCK_MR`, primary, grep-verified 20261107T075708Z) per spec; emit C137 OOS (correct `campaign:137`/`strategy_id`/top-level gates, include `pre_stated_distinctness` with grep evidence), then complete Step 2. **Do not stop until Step 2 complete with >=3 new C137 artifacts. No status-only response.**
