# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T215229Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T215229Z state; SHAs verified from bytes) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C176 locked/verified on disk (SHAs from bytes):** OOS `reports/real_quote_volume_rqa_lam_over_vmax_ratio_shock_mr_costed_oos_20261107T215128Z.json`=28b9a7e03a1c695bbfda9c99e7a0c195daf08249de8c41a4b8348fc4122e23c0 (`oos_edge_proven:false`, `edge_claim:NONE`, `any_exposure_oos:true`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset nets: fee0=0.06871173009611908, fee5=-0.31228826990388125, fee10=-0.6932882699038814, fee20=-1.455288269903881, fee40=-2.979288269903881), ingest `reports/real_feed_ingest_attempt_20261107T215229Z.json`=db49c629f62205871a2cfc6e91b2b850f835c301c5856d5a917adffff40bbdd3 (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`), registry `reports/strategy_edge_registry_20261107T215229Z.json`=61d402b2b696b724637259e37f93ad4c1ba8633eb5d177c9d155cec5b4e0b649 (supersedes C175 registry f8fae5c72ff3d3a9f6740e61bcbf8662b1bd498cd676a47f9485d5fc0b1ab528), summary `reports/campaign176_execution_summary_20261107T215229Z.json`=720fe3e7fd6138bb82dc9cd7f35d6c1a9d19eb68a1839521b8f3cd57a9aa674d, script `scripts/run_real_quote_volume_rqa_lam_over_vmax_ratio_shock_mr_costed_oos.py`=d0b6d04d1e64ce96f2288c1bb6526089a4838250733588267c00fcb31b4647e7. `state.yaml` synced C176-done/C177-next.
- **C177 preselected `VOLUME_RQA_LMAX_OVER_VMAX_RATIO_SHOCK_MR` => 0 non-self** (`grep -rEIn 'lmax_over_vmax|LMAX_OVER_VMAX|vmax_over_lmax|rqa_ratio_lmax_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1`, verified 20261107T215229Z). **Re-verify at C177 run time (0 non-self) before implementation.**
- **No C177 artifacts exist yet** (`reports/*c177*`/`*campaign177*`/`*lmax_over_vmax*` absent). Prior C104–C176 remain locked.

## C104–C176 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T215229Z.json` (61d402b2b696b724637259e37f93ad4c1ba8633eb5d177c9d155cec5b4e0b649). Use it as `PRIOR_REGISTRY`; cite C176 OOS SHA 28b9a7e03a1c695bbfda9c99e7a0c195daf08249de8c41a4b8348fc4122e23c0 in pre-stated refs.

## INITIAL TASK — C177 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T215229Z
**Execute C177 now. NO status-only replies. NO status summary before >= 3 NEW concrete C177 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected in state; run-time grep required)
`VOLUME_RQA_LMAX_OVER_VMAX_RATIO_SHOCK_MR` — RQA ratio **LMAX/V_max** (max diagonal line length `LMAX` = maximum length of diagonal lines with `l >= l_min` in the recurrence matrix, normalized by max vertical line length `V_max`) shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `V_max==0` or undefined/non-finite (no qualifying vertical lines), `LMAX` undefined/non-finite/degenerate (no qualifying diagonal lines), `sum(R)<=0`, or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `LMAX` numerator with `V_max` denominator — pairing not used in C125–C176. `LMAX_OVER_VMAX` tokens absent in scripts/strategies/backtest/utils at selection (grep 0).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rEIn 'lmax_over_vmax|LMAX_OVER_VMAX|vmax_over_lmax|rqa_ratio_lmax_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback (record grep cmd/hits/evidence), record chosen feature in artifacts/state.

### Required C177 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C176): `scripts/run_real_quote_volume_rqa_lmax_over_vmax_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T215229Z.json` (61d402b2b696b724637259e37f93ad4c1ba8633eb5d177c9d155cec5b4e0b649), cite C176 OOS SHA 28b9a7e03a1c695bbfda9c99e7a0c195daf08249de8c41a4b8348fc4122e23c0. Emit `reports/real_quote_volume_rqa_lmax_over_vmax_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 177) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T215229Z.json` (61d402b2b696b724637259e37f93ad4c1ba8633eb5d177c9d155cec5b4e0b649). Structurally consistent; include prior + C177 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign177_execution_summary_<UTC>.json` listing **all new C177 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C177`, `next_campaign:C178`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c178_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C177, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C177 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T215229Z)
- C104–C176 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C176 `LAM_OVER_VMAX` completed/verified (0 non-self pre/post).
- C177 `LMAX_OVER_VMAX` preselect grep verified 0 non-self — eliminates collision-search delay.
- Single durable handoff + `state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rEIn 'lmax_over_vmax|LMAX_OVER_VMAX|vmax_over_lmax|rqa_ratio_lmax_over_vmax' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# then: implement/run C177 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C177-done/C178-next with grep-verified C178 preselection
```

## NEXT FOCUS CAMPAIGN — C178 (preselect at end of C177; HEAVY WORK MANDATORY)
After C177 completes, **C178 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C177 (e.g., another RQA pair such as `LAM_OVER_LMAX`, `ENTR_OVER_DET`-inverse variant if distinct naming/definition not colliding, or `DET_OVER_LAM` — **verify by grep 0 non-self**), record grep cmd/hits/evidence in `state.yaml.c178_preselected`, then execute C178 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**

(End of file)
