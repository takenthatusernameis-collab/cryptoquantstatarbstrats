# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T224422Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T224422Z state; SHAs verified from bytes) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C182 locked/verified on disk (SHAs from bytes):** OOS `reports/real_quote_volume_rqa_lam_over_lavg_ratio_shock_mr_costed_oos_20261107T224422Z.json`=bf6dc9a04f23998f3d364bb87ac4d115cb21b2f1b2c0c3c08c559bd08750d13b (`oos_edge_proven:false`, `edge_claim:NONE`, `any_exposure_oos:true`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset nets: fee0=-0.03429475499240531, fee5=-0.3342947549924056, fee10=-0.6342947549924057, fee20=-1.2342947549924057, fee40=-2.434294754992406), ingest `reports/real_feed_ingest_attempt_20261107T224422Z.json`=832bc3fa1307b207ab6feb80f33aaa90d19c24fda93b3312fb84b9683f22708b (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`), registry `reports/strategy_edge_registry_20261107T224422Z.json`=f3ad154d951cba8e0b41cc91d78dee04f8fe966aa4139cb1700536ce7d90c86c (supersedes C181 registry b311d5ca8a55dacb113af6448f079711dca8d0071bb684aa6a29b0a0b6d26ee2, cites C181 OOS SHA f01fd9687b472f502cae3bde2cd038af93e44e8b199c2c337837150fcd1a6335), script `scripts/run_real_quote_volume_rqa_lam_over_lavg_ratio_shock_mr_costed_oos.py`=fea1ccf31d8bf78731437dd7d8f3e64d590dc5e280d6285e055a78f87966ffe2, summary `reports/campaign182_execution_summary_20261107T224422Z.json`=ca80d10d6c1396a7a549e70a67999672378ec1dbfe0948da84bd6fa4ed3e1b00. `state.yaml` synced C182-done/C183-next.
- **C183 preselected `VOLUME_RQA_DET_OVER_LAVG_RATIO_SHOCK_MR` => 0 hits** (`grep -rnE 'DET_OVER_LAVG|det_over_lavg|rqa_ratio_det_over_lavg' scripts/ strategies/ backtest/ utils/ research_state/ HANDOFF.md reports/ 2>&1`, verified 20261107T224422Z, 0 hits). **Re-verify at C183 run time (0 non-self) before implementation.** Fallbacks if collides (grep-zero candidates observed 20261107T224422Z): `RR_OVER_LAVG`, `TT_OVER_LAVG` (record grep cmd/hits/evidence for chosen).
- Prior C104–C182 remain locked.

## C104–C182 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T224422Z.json` (f3ad154d951cba8e0b41cc91d78dee04f8fe966aa4139cb1700536ce7d90c86c). Use it as `PRIOR_REGISTRY`; cite C182 OOS SHA bf6dc9a04f23998f3d364bb87ac4d115cb21b2f1b2c0c3c08c559bd08750d13b in pre-stated refs.

## INITIAL TASK — C183 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T224422Z
**Execute C183 now. NO status-only replies. NO status summary before >= 3 NEW concrete C183 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected in state; run-time grep required)
`VOLUME_RQA_DET_OVER_LAVG_RATIO_SHOCK_MR` — RQA ratio **DET/LAVG** shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. `DET` = determinism = `(sum of lengths of qualifying diagonal lines l>=l_min) / (sum of all recurrence points in R)`. `LAVG` = mean diagonal line length over qualifying diagonal lines (`k>=1`, excluding LOI) with `l>=l_min` on the **same** recurrence matrix. **Fail-closed NaN/no-signal** if `LAVG==0` or undefined/non-finite/degenerate (no qualifying diagonal lines), `DET` undefined/non-finite/degenerate (no recurrence points or undefined), denominator/ratio non-finite, or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `DET` numerator with `LAVG` denominator — pairing not used in C125–C182. `DET_OVER_LAVG` tokens absent across scripts/strategies/backtest/utils/research_state/HANDOFF.md/reports at selection (grep 0 at 20261107T224422Z).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'DET_OVER_LAVG|det_over_lavg|rqa_ratio_det_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback (e.g., `RR_OVER_LAVG`, `TT_OVER_LAVG`; record grep cmd/hits/evidence), record chosen feature in artifacts/state.

### Required C183 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C181/C182): `scripts/run_real_quote_volume_rqa_det_over_lavg_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T224422Z.json` (f3ad154d951cba8e0b41cc91d78dee04f8fe966aa4139cb1700536ce7d90c86c), cite C182 OOS SHA bf6dc9a04f23998f3d364bb87ac4d115cb21b2f1b2c0c3c08c559bd08750d13b. Emit `reports/real_quote_volume_rqa_det_over_lavg_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 183) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T224422Z.json` (f3ad154d951cba8e0b41cc91d78dee04f8fe966aa4139cb1700536ce7d90c86c). Structurally consistent; include prior + C183 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign183_execution_summary_<UTC>.json` listing **all new C183 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C183`, `next_campaign:C184`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c184_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C183, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C183 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T224422Z)
- C104–C182 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C181 `VMAX_OVER_LAVG` completed/verified (exposure OOS, no edge proven; all cost slices negative cross-asset net).
- C182 `LAM_OVER_LAVG` completed/verified (exposure OOS, no edge proven; all cost slices negative cross-asset net).
- C183 `DET_OVER_LAVG` preselect grep verified 0 — eliminates collision-search delay. Grep-zero fallbacks observed: `RR_OVER_LAVG`, `TT_OVER_LAVG`.
- Single durable handoff + `state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'DET_OVER_LAVG|det_over_lavg|rqa_ratio_det_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# then: implement/run C183 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C183-done/C184-next with grep-verified C184 preselection
```

## NEXT FOCUS CAMPAIGN — C184 (preselect at end of C183; HEAVY WORK MANDATORY)
After C183 completes, **C184 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C183 (verify by grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c184_preselected`, then execute C184 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
