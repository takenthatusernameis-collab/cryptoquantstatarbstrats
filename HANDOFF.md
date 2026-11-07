# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T183012Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T183012Z) — no reruns needed
- `deps_ok`: numpy 2.5.4, scipy 1.18.1, pandas 3.1.1. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C166 locked/verified on disk (SHAs):** OOS `reports/real_quote_volume_rqa_vmax_over_lam_ratio_shock_mr_costed_oos_20261107T164659Z.json`=87d630102068c8539e7eed8441d237db37d20fe14fbf515b6c4ee489357d467e (`oos_edge_proven:false`, `edge_claim:NONE`, exposure true, fee0 net +0.1198857017085776 but fails all-cost-positive/B&H rule), ingest `reports/real_feed_ingest_attempt_20261107T173330Z.json`=fb4bb81400d74036aa06526fb217f61b83232b27cf9f8c2353b446b4631ea128, registry `reports/strategy_edge_registry_20261107T173330Z.json`=f400501ed85c734d6f3093595b7594c631862af82c2fc28f58fbc7fd4d233762 (supersedes C165 bc2c0f7), summary `reports/campaign166_execution_summary_20261107T173330Z.json`=85d480312bb2db49206eea8a963a4d98c03845d972d8cef08723a1cf3ab4d691, script `scripts/run_real_quote_volume_rqa_vmax_over_lam_ratio_shock_mr_costed_oos.py`=b2fed7637425d530900fd1fd8b731c4be40434d975736e94e92a50939c44f2f8.
- **Collision guards re-verified 20261107T183012Z:** C167 primary `TT_OVER_TREND` tokens => **0** hits in `scripts/ strategies/ backtest/ utils/`. C168 fallbacks `RR_OVER_TREND` => **0**, `VMAX_OVER_TREND` => **0**. Re-verify at run time (0 non-self) before implementation.
- **No C167 artifacts exist yet** (`reports/*c167*`/`*campaign167*` absent). Prior C104–C166 remain locked.

## C104–C166 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T173330Z.json` (f400501e...). Use it as `PRIOR_REGISTRY`; cite C166 OOS SHA 87d63010... in pre-stated refs.

## INITIAL TASK — C167 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T183012Z
**Execute C167 now. NO status-only replies. NO status summary before >= 3 NEW concrete C167 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (pre-selected; run-time grep required)
`VOLUME_RQA_TT_OVER_TREND_RATIO_SHOCK_MR` — RQA ratio **`TT/TREND`** (trapping time `TT` = mean vertical-line length among qualifying `l>=l_min`, normalized by `TREND` determinism) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `TREND==0` or undefined/non-finite, `TT` undefined/non-finite, no qualifying vertical lines, offdiag/recurrence degenerate (`sum(R)<=0`), or undefined. Trailing/causal only.
Distinctness (pre-stated): different numerator/denominator token family from C165 `TREND/%LAM` and C166 `V_MAX/%LAM`; explicit `TT_OVER_TREND` tokens absent (verified 0 at 20261107T183012Z).

**Collision guard (run-time, required):**
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rn 'tt_over_trend|trend_over_tt|TT_OVER_TREND|TREND_OVER_TT|rqa_ratio_tt_over_trend|RQA_TT_OVER_TREND' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collides: pick next grep-zero fallback (`RR_OVER_TREND` or `VMAX_OVER_TREND`, both verified 0 at 20261107T183012Z), re-grep, record chosen feature + cmd/hits/evidence in artifacts/state.

### Required C167 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C166): `scripts/run_real_quote_volume_rqa_tt_over_trend_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T173330Z.json` (f400501e...), cite C166 OOS SHA 87d63010.... Emit `reports/real_quote_volume_rqa_tt_over_trend_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 167) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T173330Z.json` (f400501e...). Structurally consistent; include prior + C167 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign167_execution_summary_<UTC>.json` listing **all new C167 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C167`, `next_campaign:C168`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c168_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C167, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C167 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T183012Z)
- C104–C166 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C167 `TT_OVER_TREND` and C168 fallbacks (`RR_OVER_TREND`, `VMAX_OVER_TREND`) grep-verified **0** now — eliminates collision-search delay.
- Single durable handoff (`HANDOFF.md`) + `research_state/state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.
- No C167 artifacts exist; start implementation/run immediately from the C166 script pattern.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'tt_over_trend|trend_over_tt|TT_OVER_TREND|TREND_OVER_TT|rqa_ratio_tt_over_trend|RQA_TT_OVER_TREND' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0
# then: implement/run C167 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C167-done/C168-next with grep-verified C168 preselection
```

## NEXT FOCUS CAMPAIGN — C168 (preselect at end of C167; HEAVY WORK MANDATORY)
After C167 completes, **C168 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C167 (preferred fallbacks already verified 0 now: `RR_OVER_TREND`, `VMAX_OVER_TREND` — re-verify), record grep cmd/hits/evidence in `state.yaml.c168_preselected`, then execute C168 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
