# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T193533Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T193533Z) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C168 locked/verified on disk (SHAs):** OOS `reports/real_quote_volume_rqa_rr_over_trend_ratio_shock_mr_costed_oos_20261107T193420Z.json`=a415fbb010ef42c91fef5d207f561afc30010a0a9bad96b836955517b88dd6a2 (`oos_edge_proven:false`, `edge_claim:NONE`, exposure true), ingest `reports/real_feed_ingest_attempt_20261107T193533Z.json`=49af8d68142375429fd104f2d53a8d6ddbdd22304421fa0212dcc4b113fa6bc8, registry `reports/strategy_edge_registry_20261107T193533Z.json`=b8f49687af816d799ba2196ed74968d59599a99a593fe03ed3d812cbb36cfbf2 (supersedes C167 541298ff), summary `reports/campaign168_execution_summary_20261107T193533Z.json`=ddc9a870aa82972acd527fad5196a050a01d715b7d0ac0400589967b69829718, script `scripts/run_real_quote_volume_rqa_rr_over_trend_ratio_shock_mr_costed_oos.py`=5da9cb5ed7618c9702efe891ddb2e029334ce2de459c78ad94676fe3ae64d0e6. state.yaml synced C168-done/C169-next.
- **Collision guards re-verified 20261107T193533Z:** C168 `RR_OVER_TREND` tokens => **0** non-self hits in `scripts/ strategies/ backtest/ utils/` before implementation/run. C169 preselected `VMAX_OVER_TREND` => **0** (verified 20261107T193533Z). Re-verify at run time (0 non-self) before implementation.
- **No C169 artifacts exist yet** (`reports/*c169*`/`*campaign169*` absent). Prior C104–C168 remain locked.

## C104–C168 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T193533Z.json` (b8f49687...). Use it as `PRIOR_REGISTRY`; cite C168 OOS SHA a415fbb0... in pre-stated refs.

## INITIAL TASK — C169 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T193533Z
**Execute C169 now. NO status-only replies. NO status summary before >= 3 NEW concrete C169 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected at end of C168; run-time grep required)
`VOLUME_RQA_VMAX_OVER_TREND_RATIO_SHOCK_MR` — RQA ratio **`V_max/TREND`** (max vertical line length V_max normalized by `TREND` determinism) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `TREND==0` or undefined/non-finite, `V_max` undefined/non-finite (no qualifying vertical lines), offdiag/recurrence degenerate (`sum(R)<=0`), or undefined. Trailing/causal only.
Distinctness (pre-stated): different numerator/denominator token family from C165 `TREND/%LAM`, C166 `V_max/%LAM`, C167 `TT/TREND`, C168 `RR/TREND`; explicit `VMAX_OVER_TREND` tokens absent (verified 0 at 20261107T193533Z).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rn 'vmax_over_trend|trend_over_vmax|VMAX_OVER_TREND|RQA_VMAX_OVER_TREND|rqa_ratio_vmax_over_trend' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collides: pick next grep-zero fallback (distinct RQA-ratio candidate not used in C125–C169), re-grep, record chosen feature + cmd/hits/evidence in artifacts/state.

### Required C169 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C168): `scripts/run_real_quote_volume_rqa_vmax_over_trend_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T193533Z.json` (b8f49687...), cite C168 OOS SHA a415fbb0.... Emit `reports/real_quote_volume_rqa_vmax_over_trend_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 169) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T193533Z.json` (b8f49687...). Structurally consistent; include prior + C169 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign169_execution_summary_<UTC>.json` listing **all new C169 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C169`, `next_campaign:C170`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c170_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C169, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C169 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T193533Z)
- C104–C168 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C168 `RR_OVER_TREND` and C169 preselect `VMAX_OVER_TREND` grep-verified **0** — eliminates collision-search delay.
- Single durable handoff (`HANDOFF.md`) + `research_state/state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.
- No C169 artifacts exist; start implementation/run immediately from the C168 script pattern.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'vmax_over_trend|trend_over_vmax|VMAX_OVER_TREND|RQA_VMAX_OVER_TREND|rqa_ratio_vmax_over_trend' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0
# then: implement/run C169 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C169-done/C170-next with grep-verified C170 preselection
```

## NEXT FOCUS CAMPAIGN — C170 (preselect at end of C169; HEAVY WORK MANDATORY)
After C169 completes, **C170 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C169, record grep cmd/hits/evidence in `state.yaml.c170_preselected`, then execute C170 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
