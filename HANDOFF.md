# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T184339Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T184339Z) — no reruns needed
- `deps_ok`: numpy 2.5.4, scipy 1.18.1, pandas 3.1.1. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C167 locked/verified on disk (SHAs):** OOS `reports/real_quote_volume_rqa_tt_over_trend_ratio_shock_mr_costed_oos_20261107T184339Z.json`=515fffa2ffaafbda2ac486722d36c2bbe315f667fb90aaa67a54f7c955034f52 (`oos_edge_proven:false`, `edge_claim:NONE`, exposure true), ingest `reports/real_feed_ingest_attempt_20261107T184339Z.json`=8eacbb204c626c3ca63ddf8886e0c9d931268d6b7384ab6289983e0c57d61ade, registry `reports/strategy_edge_registry_20261107T184339Z.json`=541298ffe161771ce67e775ce3a02dee643ca2d7cd979c0604dd4e7179e698fd (supersedes C166 f400501e), summary `reports/campaign167_execution_summary_20261107T184339Z.json`=8ffd8bbe7f4f66131a386a5733d4a4a7736ecf5c2490bc80409576fe19c29f85, script `scripts/run_real_quote_volume_rqa_tt_over_trend_ratio_shock_mr_costed_oos.py`=70f9bd5ee59cc06585b4922ed920cf971e97cf683bd1620aa2fd47406a20115a. state.yaml synced C167-done/C168-next.
- **Collision guards re-verified 20261107T184339Z:** C167 primary `TT_OVER_TREND` tokens => **0** hits in `scripts/ strategies/ backtest/ utils/`. C168 preselected `RR_OVER_TREND` => **0**, fallback `VMAX_OVER_TREND` => **0** (verified 20261107T174108Z). Re-verify at run time (0 non-self) before implementation.
- **No C168 artifacts exist yet** (`reports/*c168*`/`*campaign168*` absent). Prior C104–C167 remain locked.

## C104–C167 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T184339Z.json` (541298fe...). Use it as `PRIOR_REGISTRY`; cite C167 OOS SHA 515fffa2... in pre-stated refs.

## INITIAL TASK — C168 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T184339Z
**Execute C168 now. NO status-only replies. NO status summary before >= 3 NEW concrete C168 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected at end of C167; run-time grep required)
`VOLUME_RQA_RR_OVER_TREND_RATIO_SHOCK_MR` — RQA ratio **`RR/TREND`** (recurrence rate RR = sum(R)/M^2 normalized by `TREND` determinism) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `TREND==0` or undefined/non-finite, `RR` undefined/non-finite, offdiag/recurrence degenerate (`sum(R)<=0`), or undefined. Trailing/causal only.
Distinctness (pre-stated): different numerator/denominator token family from C165 `TREND/%LAM`, C166 `V_MAX/%LAM`, C167 `TT/TREND`; explicit `RR_OVER_TREND` tokens absent (verified 0 at 20261107T184339Z).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rn 'rr_over_trend|trend_over_rr|RQA_RR_OVER_TREND|rqa_ratio_rr_over_trend' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collides: pick next grep-zero fallback (`VMAX_OVER_TREND`, verified 0 at 20261107T174108Z), re-grep, record chosen feature + cmd/hits/evidence in artifacts/state.

### Required C168 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C167): `scripts/run_real_quote_volume_rqa_rr_over_trend_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T184339Z.json` (541298fe...), cite C167 OOS SHA 515fffa2.... Emit `reports/real_quote_volume_rqa_rr_over_trend_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 168) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T184339Z.json` (541298fe...). Structurally consistent; include prior + C168 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign168_execution_summary_<UTC>.json` listing **all new C168 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C168`, `next_campaign:C169`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c169_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C168, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C168 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T184339Z)
- C104–C167 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C167 `TT_OVER_TREND` and C168 preselect `RR_OVER_TREND` / fallback `VMAX_OVER_TREND` grep-verified **0** — eliminates collision-search delay.
- Single durable handoff (`HANDOFF.md`) + `research_state/state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.
- No C168 artifacts exist; start implementation/run immediately from the C167 script pattern.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rn 'rr_over_trend|trend_over_rr|RQA_RR_OVER_TREND|rqa_ratio_rr_over_trend' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0
# then: implement/run C168 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C168-done/C169-next with grep-verified C169 preselection
```

## NEXT FOCUS CAMPAIGN — C169 (preselect at end of C168; HEAVY WORK MANDATORY)
After C168 completes, **C169 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C168 (preferred fallback already verified 0 now: `VMAX_OVER_TREND` — re-verify), record grep cmd/hits/evidence in `state.yaml.c169_preselected`, then execute C169 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
