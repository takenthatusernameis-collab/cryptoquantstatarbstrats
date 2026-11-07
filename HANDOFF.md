# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T194910Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T194910Z) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C170 locked/verified on disk (SHAs):** OOS `reports/real_quote_volume_rqa_lmax_over_det_ratio_shock_mr_costed_oos_20261107T194830Z.json`=e88f0c061dd695efd7274295fd470e8833d5c04423100c78556664390d3c5f30 (`oos_edge_proven:false`, `edge_claim:NONE`, exposure true, cross-asset nets: fee0=+0.7898, fee5=+0.4108, fee10=+0.0318, fee20=-0.7262, fee40=-2.2422), ingest `reports/real_feed_ingest_attempt_20261107T194845Z.json`=dd9cf0316389cab53d4e0e0be0d1c4b0ac87775cf216e5c06768467ffac8f379, registry `reports/strategy_edge_registry_20261107T194900Z.json`=c89757fe45765de2ff7c9be8f0293f10909d93aa3146d466be05772b7940437e (supersedes C169 19cc20be), summary `reports/campaign170_execution_summary_20261107T194910Z.json`=60e0587af45ef41b45707b37acd2e10d004fa89368f7bba8f668ad7719f3e0c6, script `scripts/run_real_quote_volume_rqa_lmax_over_det_ratio_shock_mr_costed_oos.py`=3b62f67f9391ba2e6f5fc97625da537910ea878aa69b5870cea35d2246d18284. state.yaml synced C170-done/C171-next.
- **Collision guards verified:** C169 `VMAX_OVER_TREND` => 0 non-self (pre-run). C170 `LMAX_OVER_DET` => **0** non-self (grep -rEIn, verified 20261107T194659Z pre-implementation/run). C171 preselected `RR_OVER_VMAX` => **0** non-self (grep -rEIn, verified 20261107T194840Z post-C170). Re-verify at run time (0 non-self) before implementation.
- **No C171 artifacts exist yet** (`reports/*c171*`/`*campaign171*` absent). Prior C104–C170 remain locked.

## C104–C170 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T194900Z.json` (c89757fe...). Use it as `PRIOR_REGISTRY`; cite C170 OOS SHA e88f0c06... in pre-stated refs.

## INITIAL TASK — C171 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T194910Z
**Execute C171 now. NO status-only replies. NO status summary before >= 3 NEW concrete C171 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected at end of C170; run-time grep required)
`VOLUME_RQA_RR_OVER_VMAX_RATIO_SHOCK_MR` — RQA ratio **`RR/V_max`** (recurrence rate `RR = sum(R)/N^2` normalized by max vertical line length `V_max`) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `V_max==0` or undefined/non-finite (no qualifying vertical lines), recurrence degenerate (`sum(R)<=0`), or undefined. Trailing/causal only.
Distinctness (pre-stated): different numerator/denominator token family from C165 `TREND/%LAM`, C166 `V_max/%LAM`, C167 `TT/TREND`, C168 `RR/TREND` (C168 uses RR numerator with TREND denominator; C171 uses RR numerator with V_max denominator — distinct denominator token family), C169 `V_max/TREND`, C170 `Lmax/DET`. Explicit `RR_OVER_VMAX` tokens absent (verified 0 at 20261107T194840Z).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rEIn 'rr_over_vmax|vmax_over_rr|RR_OVER_VMAX|RQA_RR_OVER_VMAX|rqa_ratio_rr_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collides: pick next grep-zero fallback (e.g. `TT_OVER_VMAX`, `VMAX_OVER_TT` — both grep-0 at 20261107T194840Z; any distinct RQA-ratio candidate not used in C125–C171), re-grep, record chosen feature + cmd/hits/evidence in artifacts/state.

### Required C171 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C170): `scripts/run_real_quote_volume_rqa_rr_over_vmax_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T194900Z.json` (c89757fe...), cite C170 OOS SHA e88f0c06.... Emit `reports/real_quote_volume_rqa_rr_over_vmax_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 171) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T194900Z.json` (c89757fe...). Structurally consistent; include prior + C171 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign171_execution_summary_<UTC>.json` listing **all new C171 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C171`, `next_campaign:C172`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c172_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C171, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C171 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T194910Z)
- C104–C170 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C170 `LMAX_OVER_DET` collision guard verified 0 non-self; C171 `RR_OVER_VMAX` grep verified 0 — eliminates collision-search delay.
- Single durable handoff (`HANDOFF.md`) + `research_state/state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.
- No C171 artifacts exist; start implementation/run immediately from the C170 script pattern.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rEIn 'rr_over_vmax|vmax_over_rr|RR_OVER_VMAX|RQA_RR_OVER_VMAX|rqa_ratio_rr_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0
# then: implement/run C171 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C171-done/C172-next with grep-verified C172 preselection
```

## NEXT FOCUS CAMPAIGN — C172 (preselect at end of C171; HEAVY WORK MANDATORY)
After C171 completes, **C172 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C171, record grep cmd/hits/evidence in `state.yaml.c172_preselected`, then execute C172 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
