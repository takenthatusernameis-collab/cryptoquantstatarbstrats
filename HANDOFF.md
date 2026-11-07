# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T205043Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T204909Z C174 run) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C174 locked/verified on disk (SHAs):** OOS `reports/real_quote_volume_rqa_det_over_trend_ratio_shock_mr_costed_oos_20261107T204909Z.json`=083ff5be33807d7f91e8b5a517a6945148f0809eeb0a84e3a46e9616b60a5141 (`oos_edge_proven:false`, `edge_claim:NONE`, exposure true, cross-asset nets: fee0=-0.8326390458759599, fee5=-1.2276390458759603, fee10=-1.6226390458759603, fee20=-2.4126390458759603, fee40=-3.99263904587596), ingest `reports/real_feed_ingest_attempt_20261107T204909Z.json`=a2d51089a1f5fde01abc54de8d9a57410560a4acb861c4da55259a8495485b40, registry `reports/strategy_edge_registry_20261107T204909Z.json`=cf392ce4e8ed93c674d2ec0fd567eb4deae341485399e3c2b4dee53ee59a51b5 (supersedes C173 f804e29b37465d5e40d5012818302aa3956b53bbc7fbdce397943eb394a6df0f), summary `reports/campaign174_execution_summary_20261107T204909Z.json`=01d1487a2ae6636b3ac1cc3fc5bd44a2e52d9cf5bbe176eda0e1787df0dfef64, script `scripts/run_real_quote_volume_rqa_det_over_trend_ratio_shock_mr_costed_oos.py`=295fe4629f975cb566c8b9d0850190f7e792c3385376386b73da46996d07eb4b. state.yaml synced C174-done/C175-next.
- **Collision guards verified:** C174 `DET_OVER_TREND`/`TREND_OVER_DET` verified **0** non-self before implementation/run; post-creation grep shows only self script. C175 preselected `VOLUME_RQA_ENTR_OVER_VMAX_RATIO_SHOCK_MR` => **0** non-self (`grep -rEIn 'entr_over_vmax|ENTR_OVER_VMAX|vmax_over_entr|rqa_ratio_entr_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1`, observed 20261107T205043Z, post-C174). Re-verify at run time (0 non-self) before implementation.
- **No C175 artifacts exist yet** (`reports/*c175*`/`*campaign175*` absent). Prior C104–C174 remain locked.

## C104–C174 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T204909Z.json` (cf392ce4e8ed93c674d2ec0fd567eb4deae341485399e3c2b4dee53ee59a51b5). Use it as `PRIOR_REGISTRY`; cite C174 OOS SHA 083ff5be33807d7f91e8b5a517a6945148f0809eeb0a84e3a46e9616b60a5141 in pre-stated refs.

## INITIAL TASK — C175 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T205043Z
**Execute C175 now. NO status-only replies. NO status summary before >= 3 NEW concrete C175 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected at end of C174; run-time grep required)
`VOLUME_RQA_ENTR_OVER_VMAX_RATIO_SHOCK_MR` — RQA ratio **ENTR/V_max** (Shannon entropy `ENTR` of the diagonal line length distribution, normalized by max vertical line length `V_max`) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `V_max==0` or undefined/non-finite (no qualifying vertical lines), `ENTR` undefined/non-finite/degenerate (no qualifying diagonal line distribution / entropy undefined), `sum(R)<=0`, or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `ENTR` numerator with `V_max` denominator — pairing not used in C125–C174 (C173 used `DET/V_max`, C170 used `Lmax/DET`, C165/C167–C169 used TREND/%LAM or */TREND variants). Explicit `ENTR_OVER_VMAX`/`VMAX_OVER_ENTR` tokens absent (verified 0 at 20261107T205043Z).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rEIn 'entr_over_vmax|ENTR_OVER_VMAX|vmax_over_entr|rqa_ratio_entr_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collides: pick next grep-zero fallback (any distinct RQA-ratio candidate not used in C125–C175), re-grep, record chosen feature + cmd/hits/evidence in artifacts/state.

### Required C175 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C174): `scripts/run_real_quote_volume_rqa_entr_over_vmax_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T204909Z.json` (cf392ce4e8ed93c674d2ec0fd567eb4deae341485399e3c2b4dee53ee59a51b5), cite C174 OOS SHA 083ff5be33807d7f91e8b5a517a6945148f0809eeb0a84e3a46e9616b60a5141. Emit `reports/real_quote_volume_rqa_entr_over_vmax_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 175) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T204909Z.json` (cf392ce4e8ed93c674d2ec0fd567eb4deae341485399e3c2b4dee53ee59a51b5). Structurally consistent; include prior + C175 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign175_execution_summary_<UTC>.json` listing **all new C175 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C175`, `next_campaign:C176`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c176_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C175, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C175 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T205043Z)
- C104–C174 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C174 `DET_OVER_TREND` collision guard verified 0 non-self before implementation/run; post-creation grep shows only self script.
- C175 `ENTR_OVER_VMAX` preselect grep verified 0 non-self at 20261107T205043Z — eliminates collision-search delay.
- Single durable handoff (`HANDOFF.md`) + `research_state/state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.
- No C175 artifacts exist; start implementation/run immediately from the C174 script pattern.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rEIn 'entr_over_vmax|ENTR_OVER_VMAX|vmax_over_entr|rqa_ratio_entr_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0
# then: implement/run C175 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C175-done/C176-next with grep-verified C176 preselection
```

## NEXT FOCUS CAMPAIGN — C176 (preselect at end of C175; HEAVY WORK MANDATORY)
After C175 completes, **C176 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C175, record grep cmd/hits/evidence in `state.yaml.c176_preselected`, then execute C176 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**

(End of file)
