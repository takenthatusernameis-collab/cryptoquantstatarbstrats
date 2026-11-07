# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T224857Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T224857Z state; SHAs verified from bytes) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C183 locked/verified on disk (SHAs from bytes):** OOS `reports/real_quote_volume_rqa_det_over_lavg_ratio_shock_mr_costed_oos_20261107T224857Z.json`=dc86746e22b019b321032d2349ba04acd129ca0dfc7c55eb3c68337a86b9e56b (`oos_edge_proven:false`, `edge_claim:NONE`, `any_exposure_oos:true`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset nets: fee0=-0.1852589343858636, fee5=-0.609258934385864, fee10=-1.033258934385864, fee20=-1.881258934385864, fee40=-3.577258934385864), ingest `reports/real_feed_ingest_attempt_20261107T224857Z.json`=f9306527646a99ec2d70d49d692f25c45162253589bed1d255244b9d5450f21a (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`), registry `reports/strategy_edge_registry_20261107T224857Z.json`=afcf51fb2b3488a2c6dd6054c59efde47763d161cb0ec0126c6ef19853b9488b (supersedes C182 registry f3ad154d951cba8e0b41cc91d78dee04f8fe966aa4139cb1700536ce7d90c86c, cites C182 OOS SHA bf6dc9a04f23998f3d364bb87ac4d115cb21b2f1b2c0c3c08c559bd08750d13b), script `scripts/run_real_quote_volume_rqa_det_over_lavg_ratio_shock_mr_costed_oos.py`=7da03ba0647ad6a8b4780f38b87ea610a0244219b1f8282c1db9144f8663c24b, summary `reports/campaign183_execution_summary_20261107T224857Z.json`=907520649a567e33cd3860de51fc277f77de2620ab8f768ff822155e9d03d411. `state.yaml` synced C183-done/C184-next.
- **C184 preselected `VOLUME_RQA_RR_OVER_LAVG_RATIO_SHOCK_MR` => 0 hits** (`grep -rnE 'RR_OVER_LAVG|rr_over_lavg|rqa_ratio_rr_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1`, verified 20261107T224857Z, 0 hits). **Re-verify at C184 run time (0 non-self) before implementation.** Fallbacks if collides (grep-zero observed 20261107T224857Z): `TT_OVER_LAVG`, `ENTR_OVER_LAVG` (record grep cmd/hits/evidence for chosen).
- Prior C104–C183 remain locked.

## C104–C183 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T224857Z.json` (afcf51fb2b3488a2c6dd6054c59efde47763d161cb0ec0126c6ef19853b9488b). Use it as `PRIOR_REGISTRY`; cite C183 OOS SHA dc86746e22b019b321032d2349ba04acd129ca0dfc7c55eb3c68337a86b9e56b in pre-stated refs.

## INITIAL TASK — C184 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T224857Z
**Execute C184 now. NO status-only replies. NO status summary before >= 3 NEW concrete C184 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected in state; run-time grep required)
`VOLUME_RQA_RR_OVER_LAVG_RATIO_SHOCK_MR` — RQA ratio **RR/LAVG** shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. `RR` = recurrence rate = `(sum of all recurrence points in R) / M^2` (total recurrence density over the `M x M` recurrence matrix). `LAVG` = mean diagonal line length over qualifying diagonal lines (`k>=1`, excluding LOI) with `l>=l_min` on the **same** recurrence matrix. **Fail-closed NaN/no-signal** if `LAVG==0` or undefined/non-finite/degenerate (no qualifying diagonal lines), `RR` undefined/non-finite/degenerate, denominator/ratio non-finite, or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `RR` numerator with `LAVG` denominator — pairing not used in C125–C183. `RR_OVER_LAVG` tokens absent across scripts/strategies/backtest/utils at preselect (grep 0 at 20261107T224857Z).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'RR_OVER_LAVG|rr_over_lavg|rqa_ratio_rr_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback (e.g., `TT_OVER_LAVG`, `ENTR_OVER_LAVG`; record grep cmd/hits/evidence), record chosen feature in artifacts/state.

### Required C184 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C182/C183): `scripts/run_real_quote_volume_rqa_rr_over_lavg_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T224857Z.json` (afcf51fb2b3488a2c6dd6054c59efde47763d161cb0ec0126c6ef19853b9488b), cite C183 OOS SHA dc86746e22b019b321032d2349ba04acd129ca0dfc7c55eb3c68337a86b9e56b (and C182 ref as needed). Emit `reports/real_quote_volume_rqa_rr_over_lavg_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 184) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T224857Z.json` (afcf51fb2b3488a2c6dd6054c59efde47763d161cb0ec0126c6ef19853b9488b). Structurally consistent; include prior + C184 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign184_execution_summary_<UTC>.json` listing **all new C184 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C184`, `next_campaign:C185`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c185_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C184, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C184 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T224857Z)
- C104–C183 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C182 `LAM_OVER_LAVG` completed/verified (exposure OOS, no edge proven).
- C183 `DET_OVER_LAVG` completed/verified (exposure OOS, no edge proven; all cost slices negative cross-asset net: fee0=-0.1852589343858636..fee40=-3.577258934385864).
- C184 `RR_OVER_LAVG` preselect grep verified 0 — eliminates collision-search delay. Grep-zero fallbacks observed: `TT_OVER_LAVG`, `ENTR_OVER_LAVG`.
- Single durable handoff + `state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'RR_OVER_LAVG|rr_over_lavg|rqa_ratio_rr_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# then: implement/run C184 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C184-done/C185-next with grep-verified C185 preselection
```

## NEXT FOCUS CAMPAIGN — C185 (preselect at end of C184; HEAVY WORK MANDATORY)
After C184 completes, **C185 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C184 (verify by grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c185_preselected`, then execute C185 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
