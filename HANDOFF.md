# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T194509Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T194509Z) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C169 locked/verified on disk (SHAs):** OOS `reports/real_quote_volume_rqa_vmax_over_trend_ratio_shock_mr_costed_oos_20261107T193943Z.json`=06071d806fedc8eba2342f331fea23fbb061e952369b80ddbd3273689441f262 (`oos_edge_proven:false`, `edge_claim:NONE`, exposure true), ingest `reports/real_feed_ingest_attempt_20261107T194126Z.json`=76204842b3279beee2cc6d4ff5dde0eb6656c54ecd7caab0c89ca3e3fea3037f, registry `reports/strategy_edge_registry_20261107T194147Z.json`=19cc20be3105ed35e4691fda5a2147094a674fa504667d9598c30c1432eab104 (supersedes C168 b8f49687), summary `reports/campaign169_execution_summary_20261107T194215Z.json`=3a17d322bb00d1f64a7bbff025b369f5a9ea56894629bfae58358d18706db9a0, script `scripts/run_real_quote_volume_rqa_vmax_over_trend_ratio_shock_mr_costed_oos.py`=915e47ba61a2a53a9fbec4f238d644f094d8965a8a5877c46568f9db6a4f3343. state.yaml synced C169-done/C170-next.
- **Collision guards re-verified 20261107T194509Z:** C168 `RR_OVER_TREND` tokens => **0** non-self hits in `scripts/ strategies/ backtest/ utils/` before implementation/run. C169 `VMAX_OVER_TREND` => **0** non-self (verified 20261107T194509Z, incl. C169 script's own guard string). C170 preselected `LMAX_OVER_DET` => **0** non-self (grep -E, verified 20261107T194509Z post-C169). Re-verify at run time (0 non-self) before implementation.
- **No C170 artifacts exist yet** (`reports/*c170*`/`*campaign170*` absent). Prior C104–C169 remain locked.

## C104–C169 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T194147Z.json` (19cc20be...). Use it as `PRIOR_REGISTRY`; cite C169 OOS SHA 06071d80... in pre-stated refs.

## INITIAL TASK — C170 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T194509Z
**Execute C170 now. NO status-only replies. NO status summary before >= 3 NEW concrete C170 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected at end of C169; run-time grep required)
`VOLUME_RQA_LMAX_OVER_DET_RATIO_SHOCK_MR` — RQA ratio **`Lmax/DET`** (max vertical line length Lmax normalized by `TREND`/determinism) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `DET==0` or undefined/non-finite, `Lmax` undefined/non-finite (no qualifying vertical lines), offdiag/recurrence degenerate (`sum(R)<=0`), or undefined. Trailing/causal only.
Distinctness (pre-stated): different numerator/denominator token family from C165 `TREND/%LAM`, C166 `V_max/%LAM`, C167 `TT/TREND`, C168 `RR/TREND`, C169 `V_max/TREND`; explicit `LMAX_OVER_DET` tokens absent (verified 0 at 20261107T194509Z). Does not collide with C169's `vmax_over_trend` guard tokens.

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rEIn 'lmax_over_det|det_over_lmax|LMAX_OVER_DET|RQA_LMAX_OVER_DET|rqa_ratio_lmax_over_det' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collides: pick next grep-zero fallback (distinct RQA-ratio candidate not used in C125–C170), re-grep, record chosen feature + cmd/hits/evidence in artifacts/state.

### Required C170 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C168/C169): `scripts/run_real_quote_volume_rqa_lmax_over_det_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T194147Z.json` (19cc20be...), cite C169 OOS SHA 06071d80.... Emit `reports/real_quote_volume_rqa_lmax_over_det_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 170) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T194147Z.json` (19cc20be...). Structurally consistent; include prior + C170 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign170_execution_summary_<UTC>.json` listing **all new C170 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C170`, `next_campaign:C171`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c171_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C170, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C170 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T194509Z)
- C104–C169 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C168/C169 collision guards verified 0 non-self; C170 `LMAX_OVER_DET` grep verified 0 — eliminates collision-search delay.
- Single durable handoff (`HANDOFF.md`) + `research_state/state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.
- No C170 artifacts exist; start implementation/run immediately from the C169 script pattern.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rEIn 'lmax_over_det|det_over_lmax|LMAX_OVER_DET|RQA_LMAX_OVER_DET|rqa_ratio_lmax_over_det' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0
# then: implement/run C170 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C170-done/C171-next with grep-verified C171 preselection
```

## NEXT FOCUS CAMPAIGN — C171 (preselect at end of C170; HEAVY WORK MANDATORY)
After C170 completes, **C171 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C170, record grep cmd/hits/evidence in `state.yaml.c171_preselected`, then execute C171 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**

(End of file - total 120 lines)
