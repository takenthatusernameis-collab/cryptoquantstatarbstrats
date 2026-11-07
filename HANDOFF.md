# READ THIS FIRST — C138 INITIAL TASK (20261107T080222Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute the next focus campaign NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

**Readiness verified 20261107T080222Z:** `numpy,scipy,pandas` importable; required caches present (`volume_1h_full.{pkl,provenance.json}`, `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`); pytest unavailable (honest); C138 primary grep-zero in `scripts/ strategies/ backtest/ utils/`; git state to be committed by next agent if desired.

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- C104–C136 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.
- **C137 DONE (20261107T080222Z):** `VOLUME_RQA_RR_OVER_DET_RATIO_SHOCK_MR` (RQA ratio `RATIO_RR_DET = %RR/%DET`, recurrence density normalized by determinism, delay-embedded log-volume returns `m=2,tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`; fail-closed on `%DET<=0`/offdiag<=0/non-finite/degenerate/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - OOS: `reports/real_quote_volume_rqa_rr_over_det_ratio_shock_mr_costed_oos_20261107T080021Z.json` (sha256 `0acefbc7dfdaf656291ffad9d6900f483800707bc7878c7f2503baa6a9414f37`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=-1.0874977508831756`, `fee5_slip5=-2.1474977508831765`, `fee10_slip10=-3.207497750883177`, `fee20_slip20=-5.327497750883176`, `fee40_slip40=-9.567497750883176`). RQA computed every 2 bars (causal forward-hold) — disclosed.
  - Script: `scripts/run_real_quote_volume_rqa_rr_over_det_ratio_shock_mr_costed_oos.py` (sha256 `e37e5fb742bdce26cb495aa2f1dc1b996b14ef63b63de5456ea068f708847bae`; `campaign:137`, `strategy_id: VOLUME_RQA_RR_OVER_DET_RATIO_SHOCK_MR`, top-level gate fields).
  - Ingest: `reports/real_feed_ingest_attempt_20261107T080222Z.json` (sha256 `4caff2e3c20aa1faf10c547631d51fc18b831b5d576a34323729fe926aa3a754`, fail-closed blocked/no real nonspot artifact; `rb_unblocked=true`).
  - Registry superseding C136: `reports/strategy_edge_registry_20261107T080222Z.json` (sha256 `0afcf580807f83dc82519ffbd8dac1283bb17621d2a813abad9ec33f8a73e5c3`; supersedes `reports/strategy_edge_registry_20261107T075344Z.json` sha `0c199afadd2a2aea7032bacef2997622402e883567d36d48153dd1376c033b3d`; `edge_claim: NONE`; C137 entry appended).
  - Summary: `reports/campaign137_execution_summary_20261107T080222Z.json` (sha256 from disk; SHAs from bytes on disk).
  - Distinctness (grep-verified pre-implementation, zero non-self hits): `rr_over_det|rr_det_ratio|rqa_ratio_rr_det|RR_OVER_DET` over `scripts/ strategies/ backtest/ utils/` returned 0 hits — distinct from C125 `%RR` direct, C126 `%DET` direct, C133 `%DET/%RR` (inverse), C134 `%LAM/%DET`, C136 `%LAM/%RR`; C137 trades ratio `%RR/%DET`.
  - C136 OOS ref: `reports/real_quote_volume_rqa_lam_over_rr_ratio_shock_mr_costed_oos_20261107T075344Z.json` (sha256 `1e9e562d79d561b4266f6bb3bf5fe447e99668787f76d63519af1cb7b57b99cc`).
  - Pytest: unavailable (`/usr/bin/python3: No module named pytest`) — recorded honestly; not fabricated.
- Real data preconditions OK (do not re-scan/fetch): `data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}` present.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C137 marked DONE with disk-verified SHAs and superseding registry emitted; C104–C137 locked — no reruns. Carry forward latest registry `strategy_edge_registry_20261107T080222Z.json` (sha `0afcf580807f83dc82519ffbd8dac1283bb17621d2a813abad9ec33f8a73e5c3`).
- **C138 pre-selected (grep-VERIFIED 20261107T080222Z, zero non-self hits in `scripts/ strategies/ backtest/ utils/`):** Primary candidate `VOLUME_RQA_DET_OVER_LAM_RATIO_SHOCK_MR` — ratio `%DET/%LAM` (determinism normalized by laminarity) on delay-embedded log-volume returns, `m=2, tau=1, eps=0.5*std(r_window)` fixed, `W_RR=168`, `l_min=2`, fail-closed to NaN/no-signal when `%LAM<=0` or undefined/non-finite/degenerate/zero off-diagonal recurrence. **Collision guard PASSED:** C126 trades `%DET` direct, C128 `%LAM` direct, C133 `%DET/%RR`, C134 `%LAM/%DET` (inverse), C136 `%LAM/%RR`, C137 `%RR/%DET`; this trades *ratio* `%DET/%LAM` — grep confirmed 0 hits for `det_over_lam|det_lam_ratio|rqa_ratio_det_lam|DET_OVER_LAM`. If a future agent sees a collision, pick next distinct alternative: `VOLUME_RQA_RR_OVER_LAM_RATIO_SHOCK_MR` — verify no `rr_over_lam|rr_lam_ratio` collision; same spec, fail-closed. **Pre-state chosen alternative, record grep-zero, justify distinctness in OOS `pre_stated_distinctness`**.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C138 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C137 done — do NOT rerun. C138 is PENDING and must be executed.

### Step 0 — Readiness + distinctness (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
# primary candidate grep (must be 0 non-self before implementation); if not 0, apply collision guard and pick/verify alternative
grep -rn 'det_over_lam\|det_lam_ratio\|rqa_ratio_det_lam\|DET_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Primary candidate expected distinct (grep-verified 20261107T080222Z); record grep result (or any alternative) in OOS `pre_stated_distinctness`.

### Step 1 — Run C138 (PRIORITY 1)
1. **Feature (pre-stated primary, grep-verified/disambiguated):** `VOLUME_RQA_DET_OVER_LAM_RATIO_SHOCK_MR` (or verified alternative per collision guard). On `r_t = ln(v_t)-ln(v_{t-1})`, delay embedding `X_i=(r_i,r_{i+tau})`, `m=2,tau=1`, trailing `W_RR=168`. `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, `eps = 0.5*std(r_window)` fixed. Compute `%LAM = (points in qualifying vertical lines l>=l_min=2, main diagonal excluded)/(offdiag sum)`, `%DET = (points in qualifying diagonal lines l>=l_min=2, main diagonal excluded)/(offdiag sum)`. `RATIO_DET_LAM = %DET / %LAM` (**fail-closed** to `NaN`/no-signal if `%LAM<=0`, offdiag/undefined/non-finite/degenerate). Causal trailing only.
2. **Signal (fail-closed MR):** `z = (feature - ALB_mean) / ALB_std`, `ALB=336`. Use `RATIO_DET_LAM` as the feature. `entry_z >= 1.5` → fade (short); `entry_z <= -1.5` → long; `exit |z| < 0.5` or `max_hold=24` or flip. Exec `t -> t+1`.
3. **WF/costs/B&H (exact):** `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows. Real data only; full provenance + sha256.
4. **Emit:** `reports/real_quote_volume_rqa_det_over_lam_ratio_shock_mr_costed_oos_<UTC>.json` (or alternative name) and corresponding script in `scripts/`. **Set correct `campaign:138` and `strategy_id` in emitted JSON and include top-level gate fields** (`oos_edge_proven`, `edge_claim`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`). Reference prior registry `reports/strategy_edge_registry_20261107T080222Z.json` (sha `0afcf580807f83dc82519ffbd8dac1283bb17621d2a813abad9ec33f8a73e5c3`) and C137 OOS sha `0acefbc7dfdaf656291ffad9d6900f483800707bc7878c7f2503baa6a9414f37`.

### Step 2 — Registry + ingest + pytest + summary (MANDATORY)
1. Ingest attempt report: `reports/real_feed_ingest_attempt_<UTC>.json` (fail-closed, honest nonspot status; `rb_unblocked=true`).
2. Pytest: run `python3 -m pytest -q --tb=no` if available; record exact outcome honestly. Do not fabricate.
3. Registry superseding `reports/strategy_edge_registry_20261107T080222Z.json` (sha `0afcf580807f83dc82519ffbd8dac1283bb17621d2a813abad9ec33f8a73e5c3`): structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C136–C137 context and add C138 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
4. Summary: `reports/campaign138_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C138 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete report artifacts exist for C138** (OOS + ingest + registry/summary counting as concrete artifacts).
- **Heavy work mandatory:** run/implement as needed + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'det_over_lam\|det_lam_ratio\|rqa_ratio_det_lam\|DET_OVER_LAM' scripts/ strategies/ backtest/ utils/ 2>/dev/null | head
```
Then implement/run C138 (`VOLUME_RQA_DET_OVER_LAM_RATIO_SHOCK_MR`, primary, grep-verify before implementation) per spec; emit C138 OOS (correct `campaign:138`/`strategy_id`/top-level gates, include `pre_stated_distinctness` with grep evidence), then complete Step 2. **Do not stop until Step 2 complete with >=3 new C138 artifacts. No status-only response.**
