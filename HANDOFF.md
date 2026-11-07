# READ THIS FIRST — C142 COMPLETED / C143 NEXT (20261107T095654Z; single durable handoff)

**Single durable handoff for `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Execute C143 NOW — no investigation-only work, no status-only replies. Produce heavy artifacts first. Real data only; fail-closed; no proxies labeled real; no fabricated feeds/provenance/results.**

**Readiness re-verified 20261107T095311Z (still valid):** `numpy,scipy,pandas` importable; required caches present (`volume_1h_full.{pkl,meta.json,provenance.json}`, `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`); pytest unavailable (honest, `/usr/bin/python3: No module named pytest`).

## Repo prioritization (from name `cryptoquantstatarbstrats`)
Fail-closed, real-data-only stat-arb edge validation: walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. Nonspot ingest is a hard blocker only if a real nonspot artifact never appears; R-B proceeds on validated `real_quote_volume` family regardless.

## Verified current state (do not rerun unchanged)
- **C104–C142 DONE → `oos_edge_proven=false` (registry lineage). Do NOT rerun.** All 39 campaigns C104–C142 locked; `edge_claim: NONE` throughout.
- **C142 COMPLETED (20261107T095654Z):** `VOLUME_RQA_DET_OVER_TT_RATIO_SHOCK_MR` (RQA ratio `RATIO_DET_TT = %DET / TT_mean`, diagonal-line determinism normalized by trapping time/mean vertical-line length, on delay-embedded log-volume returns; `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`; fail-closed on `TT_mean<=0`/no qualifying vertical lines/`%DET` undefined/non-finite/offdiag-degenerate/undefined) — `oos_edge_proven=false`, `edge_claim: NONE`.
  - Correct OOS (regenerated; flawed 20261107T090953Z report had wrong C141 ENTR/%RR metadata — superseded, not used): `reports/real_quote_volume_rqa_det_over_tt_ratio_shock_mr_costed_oos_20261107T095547Z.json` (sha `bbdba5d6ccee31218c5bb3f2ab158981f0d3eedfd6add36d5dc9be0390487796`, `real_data_only=true`, `fail_closed=true`, `oos_edge_proven=false`, `any_exposure_oos=true`, `all_cost_slices_positive_oos_net_sum=false`, `all_cost_slices_beat_bh_mean_rule=false`; cross-asset OOS net sums `fee0_slip0=0.21928571878091374`, `fee5_slip5=-0.1547142812190866`, `fee10_slip10=-0.5287142812190867`, `fee20_slip20=-1.2767142812190868`, `fee40_slip40=-2.7727142812190864`). Top-level gate fields present; refs C141 registry sha `0fcfc941...`/C141 OOS sha `2c1513ac...`; grep-zero `det_over_tt|det_tt_ratio|rqa_ratio_det_tt|DET_OVER_TT` recorded.
  - Flawed prior (superseded): `reports/real_quote_volume_rqa_det_over_tt_ratio_shock_mr_costed_oos_20261107T090953Z.json` (sha `740b41df3c1fd65ad323102500ec461befd9de995744672eed08404d689a32c4`) — wrong C141 ENTR/%RR candidate/feature/`pre_stated_distinctness` metadata.
  - Ingest: `reports/real_feed_ingest_attempt_20261107T091027Z.json` (sha `00dee85236e3a6930fc4b81b059be31d51953eb03e9829bf56551e350e1fa421`, campaign 142, nonspot blocked fail-closed, `rb_unblocked=true`).
  - Script: `scripts/run_real_quote_volume_rqa_det_over_tt_ratio_shock_mr_costed_oos.py` (sha `15130345d48f9241960ed0a573365788b25c9e3f8a60a8cd85a024a22c4b2184`).
  - Registry superseding C141: `reports/strategy_edge_registry_20261107T095654Z.json` (sha `adf7d58adb4151dab1769d739d938311131d955bf190221fae4a6afb0e9e2e72`, supersedes `reports/strategy_edge_registry_20261107T090342Z.json` sha `0fcfc9410fadb171b621a959029dccb4ec891fc8dd2543d3f7c1db8252706fa4`).
  - Summary: `reports/campaign142_execution_summary_20261107T095654Z.json` (sha `4541b04db338d48e00d88cab8948881d1db646ce3d18d10f0ed100a817fdac60`).
  - `research_state/state.yaml` synced: `latest_campaign_done: C142`, `next_campaign: C143`.
- Real data preconditions OK (do not re-scan/fetch): caches present as above.
- Python deps OK: `numpy, scipy, pandas` importable. pytest NOT installed; record honestly.

## Bottlenecks removed (this handoff)
- C104–C142 locked; no reruns unchanged. Carry forward latest registry `strategy_edge_registry_20261107T095654Z.json` (sha `adf7d58adb4151dab1769d739d938311131d955bf190221fae4a6afb0e9e2e72`).
- C142 flaw resolved: DET/TT OOS regenerated with correct metadata/top-level gates; flawed report superseded; registry/summary/state synced with disk-verified SHAs.
- "No status before >=3 new artifacts" + mandatory run — forces heavy work for C143.
- pytest unavailable recorded honestly — do not fabricate test results.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## NEXT FOCUS CAMPAIGN — C143 (MANDATORY, HEAVY WORK)

**Order is non-negotiable.** C104–C142 done — do NOT rerun.

### Step 0 — Readiness + distinctness grep + implement/run (required, fail-closed)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'lam_over_tt\|lam_tt_ratio\|rqa_ratio_lam_tt\|LAM_OVER_TT' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Primary C143 candidate (pre-selected): **`VOLUME_RQA_LAM_OVER_TT_RATIO_SHOCK_MR`** — RQA ratio `RATIO_LAM_TT = %LAM / TT_mean` (laminarity normalized by trapping time/mean vertical-line length) on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). Fail-closed NaN/no-signal if `TT_mean<=0`, no qualifying vertical lines, `%LAM` undefined/non-finite, offdiag-degenerate, or undefined. Distinct from C125–C142 (all prior RQA metrics/ratios including `%LAM` direct C128/C129 TT-family context, `%LAM/%DET` C134, `%LAM/%RR` C136, `%RR/%LAM` C139, `%DET/%TT` C142, `%RR/TT` C140, `ENTR/%RR` C141). **If grep non-zero (collision), pick next distinct alternative (`VOLUME_RQA_ENTR_OVER_DET_RATIO_SHOCK_MR` ENTR/%DET fail-closed on %DET<=0/no qualifying diagonal lines; or `VOLUME_RQA_ENTR_OVER_LAM_RATIO_SHOCK_MR` ENTR/%LAM fail-closed on %LAM<=0/no qualifying vertical lines), re-grep, and record chosen feature + grep evidence.**

Implement script `scripts/run_real_quote_volume_rqa_lam_over_tt_ratio_shock_mr_costed_oos.py` (or chosen alternative) modeled on the correct C142 script (copy its WF/cost/B&H/SHA/report structure; change only feature computation, IDs, and `pre_stated_distinctness`/refs to latest registry `strategy_edge_registry_20261107T095654Z.json` sha `adf7d58adb4151dab1769d739d938311131d955bf190221fae4a6afb0e9e2e72` and C142 OOS sha `bbdba5d6ccee31218c5bb3f2ab158981f0d3eedfd6add36d5dc9be0390487796`). Run it to emit `reports/real_quote_volume_rqa_<chosen>_costed_oos_<UTC>.json` with all top-level gate fields (`oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`), `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` recording grep cmd/hits/evidence.

### Step 1 — Ingest + registry + summary (MANDATORY)
1. Ingest: create/emit `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 143) consistent with prior ingest style — record nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume` family.
2. Registry: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T095654Z.json` (sha `adf7d58adb4151dab1769d739d938311131d955bf190221fae4a6afb0e9e2e72`). Structurally consistent `campaign/supersedes/supersedes_sha256/lineage/entries/campaigns`; include C138–C142 context/entries and add C143 with artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds.
3. Summary: `reports/campaign143_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (SHAs computed from bytes on disk): OOS, ingest, registry, script.
4. Sync `research_state/state.yaml`: `latest_campaign_done: C143`, `next_campaign: C144`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c144_preselected` with a distinct grep-verified RQA-ratio candidate not used in C125–C143.

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C143 collision guard required; record chosen feature + grep evidence).
- **No status summary before >= 3 new concrete C143 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rn 'lam_over_tt\|lam_tt_ratio\|rqa_ratio_lam_tt\|LAM_OVER_TT' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Then implement and run the C143 LAM/TT (or collision-safe alternative) OOS script, emit ingest/registry/summary, and sync state.yaml to C143-done/C144-next. **Do not stop until C143 is properly complete with >=3 new artifacts and state.yaml synced. No status-only response.**
