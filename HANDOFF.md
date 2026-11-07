# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T155019Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Prioritization (from repo name):** fail-closed, real-data-only stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Edge is claimed ONLY under the exact fail-closed edge rule. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## C162 DONE — do NOT rerun
- `pytest` unavailable (honestly recorded — do not fabricate test results). `numpy/scipy/pandas` importable (verified this session). Caches present (`data/cache/volume_1h_full.{pkl,meta.json,provenance.json}`, `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.{pkl,meta.json}`).
- **C162 result (locked):** `VOLUME_RQA_TREND_OVER_ENTR_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`.
  - OOS: `reports/real_quote_volume_rqa_trend_over_entr_ratio_shock_mr_costed_oos_20261107T145139Z.json` (sha `9ae2a423559374234c2cd1cec77b8f5cbb18786ae7282e5b918d0b5b523db9ea`). `any_exposure_oos:true`; cross-asset net sums `fee0=0.5204542903247399, fee5=0.09245429032473954, fee10=-0.33554570967526043, fee20=-1.1915457096752604, fee40=-2.90354570967526`; `all_cost_slices_positive_oos_net_sum:false`; `all_cost_slices_beat_bh_mean_rule:false`.
  - Ingest: `reports/real_feed_ingest_attempt_20261107T154835Z.json` (sha `adabb55c5b9b40af2bec1447a513194a19808d482f1dd36bfc42e905ade7aacc`).
  - Registry: `reports/strategy_edge_registry_20261107T154835Z.json` (sha `02309b4b050c102114e000ef013f83202fe1f661a245efb2e93d8ea2ef3b6210`, supersedes C161 `17048b6c...`).
  - Summary: `reports/campaign162_execution_summary_20261107T154835Z.json` (sha `269e7415ac8ff048e6564bf00116577d57fac465798d98ae47b7cfe842d6c22d`).
  - Script: `scripts/run_real_quote_volume_rqa_trend_over_entr_ratio_shock_mr_costed_oos.py` (sha `22ea68022ee398a3d16154c0946f03971bc1b508624a06ae1550f84fd1a79e52`).

## INITIAL TASK FOR NEXT SESSION — C163 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**No status-only replies. No status summary before >= 3 new concrete C163 report artifacts exist (OOS + ingest + registry/summary).**

**Primary C163 candidate (pre-selected — MUST re-verify grep at run time):** `VOLUME_RQA_ENTR_OVER_TREND_RATIO_SHOCK_MR` — RQA ratio `ENTR/TREND` (diagonal-line Shannon entropy normalized by diagonal recurrence TREND slope) shock on delay-embedded log-volume returns (`m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`). Fail-closed NaN/no-signal if `TREND==0` or undefined/non-finite (regression degenerate/insufficient qualifying diagonal points), `ENTR<=0` or undefined/non-finite, no qualifying diagonal lines, offdiag/recurrence degenerate, or undefined. Distinct from C125–C162 (incl C162 `TREND/ENTR` — inverse ratio, distinct numerator/denominator; C161 `L_max/TREND`, C160 `TREND/L_max`, C159 `TT/ENTR`).

**Collision guard (run-time, required):**
```bash
grep -rn 'entr_over_trend|entr_trend_ratio|rqa_ratio_entr_trend|ENTR_OVER_TREND' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l
```
Must be **0 non-self**. Preselect grep was 0 at 20261107T154835Z and re-verified 0 this session — still re-verify at run time. If collides, pick next distinct grep-zero alternative, re-grep, and record chosen feature + grep evidence.

### Required C163 deliverables (all on disk, SHA256 from bytes)
1. **Implement/run OOS script** (model on C162/C161): `scripts/run_real_quote_volume_rqa_entr_over_trend_ratio_shock_mr_costed_oos.py` (or chosen alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs to latest registry `reports/strategy_edge_registry_20261107T154835Z.json` (sha `02309b4b050c102114e000ef013f83202fe1f661a245efb2e93d8ea2ef3b6210`) + C162 OOS sha `9ae2a423559374234c2cd1cec77b8f5cbb18786ae7282e5b918d0b5b523db9ea`. Emit `reports/real_quote_volume_rqa_entr_over_trend_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim: NONE`, `real_data_only:true`, `fail_closed:true`, and `pre_stated_distinctness` (grep cmd/hits/evidence; explicit distinctness from C162/C161/C160).
2. **Ingest artifact:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 163) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T154835Z.json` (sha `02309b4b050c102114e000ef013f83202fe1f661a245efb2e93d8ea2ef3b6210`). Structurally consistent lineage; include prior context + C163 artifacts/SHAs/scripts; `edge_claim: NONE` unless edge rule holds. **Verify grep for C164 preselection; do not copy stale candidates.**
4. **Summary:** `reports/campaign163_execution_summary_<UTC>.json` listing all new artifact paths + sha256 (from bytes on disk): OOS, ingest, registry, script.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done: C163`, `next_campaign: C164`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c164_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C163).

## Fail-closed edge rule (exact)
`oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. No gate/threshold weakening. WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.

## Mandatory rules (hard)
- Real data only; fail-closed always. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if conditions above hold.
- Pre-state distinctness; grep-verify before implementation/run (C163 collision guard required; record evidence).
- **No status summary before >= 3 new concrete C163 report artifacts exist** (OOS + ingest + registry/summary).
- **Heavy work mandatory:** implement/run + artifact emission; no status-only replies.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## Bottlenecks removed (confirmed 20261107T155019Z)
- C104–C162 locked; no reruns unchanged. C162 artifacts emitted with disk-verified SHAs; state/HANDOFF synced.
- `numpy/scipy/pandas` importable; caches present. `pytest` unavailable recorded honestly — do not fabricate.
- C163 primary `ENTR/OVER_TREND` grep verified **0 hits** (preselect + this session recheck). Re-verify at run time.
- `"No status before >=3 new artifacts"` + mandatory heavy work enforced.
- Nonspot ingest does **NOT** block R-B on `real_quote_volume`.
- State over-claim corrected: `latest_campaign_done` = C162; `next_campaign` = C163.

## Immediate first action
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'entr_over_trend|entr_trend_ratio|rqa_ratio_entr_trend|ENTR_OVER_TREND' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l   # must be 0 non-self
```
Then implement/run C163 `ENTR/OVER_TREND` (or collision-safe alternative), emit ingest+registry+summary, sync `research_state/state.yaml` to C163-done/C164-next. **Do not stop until C163 is properly complete with >=3 new artifacts and state.yaml synced.**
