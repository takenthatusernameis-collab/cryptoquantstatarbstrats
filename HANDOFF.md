# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T232110Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T232110Z state; SHAs verified from bytes) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C184 locked/verified on disk (SHAs from bytes):** OOS `reports/real_quote_volume_rqa_rr_over_lavg_ratio_shock_mr_costed_oos_20261107T232110Z.json`=98094a4533fa0a17a24f0d4d05b88dce785de0b76054909eeef0daf55d7e29be (`oos_edge_proven:false`, `edge_claim:NONE`, `any_exposure_oos:true`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset nets: fee0=-1.1137172605480297, fee5=-1.43371726054803, fee10=-1.75371726054803, fee20=-2.39371726054803, fee40=-3.6737172605480293), ingest `reports/real_feed_ingest_attempt_20261107T232110Z.json`=0267f6f314dd030f57206fce6113af0289611eee2fcf55df5bf29b470ddf88d0 (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`), registry `reports/strategy_edge_registry_20261107T232110Z.json`=f1df4ec5626cbe025c9b43837d30d4b04cd75c7b67f089e24d7ab72ad67fda45 (supersedes C183 registry afcf51fb2b3488a2c6dd6054c59efde47763d161cb0ec0126c6ef19853b9488b, cites C183 OOS SHA dc86746e22b019b321032d2349ba04acd129ca0dfc7c55eb3c68337a86b9e56b), script `scripts/run_real_quote_volume_rqa_rr_over_lavg_ratio_shock_mr_costed_oos.py`=19208e6d5d834ef576b6e1709803f9186ae8eac5790d9e6c77f43d22abf76be5, summary `reports/campaign184_execution_summary_20261107T232110Z.json`=e86205cbd2747271ee694bd8d81328e14e4cb7483f9898a66afc0041631ca5e4. `state.yaml` synced C184-done/C185-next.
- **C185 preselected `VOLUME_RQA_TT_OVER_LAVG_RATIO_SHOCK_MR` => 0 hits** (`grep -rnE 'TT_OVER_LAVG|tt_over_lavg|rqa_ratio_tt_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1`, verified 20261107T232110Z, 0 hits). **Re-verify at C185 run time (0 non-self) before implementation.** Fallbacks if collides (grep-zero observed 20261107T232110Z): `ENTR_OVER_LAVG` (record grep cmd/hits/evidence for chosen).
- Prior C104–C184 remain locked.

## C104–C184 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T232110Z.json` (f1df4ec5626cbe025c9b43837d30d4b04cd75c7b67f089e24d7ab72ad67fda45). Use it as `PRIOR_REGISTRY`; cite C184 OOS SHA 98094a4533fa0a17a24f0d4d05b88dce785de0b76054909eeef0daf55d7e29be in pre-stated refs.

## INITIAL TASK — C185 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T232110Z
**Execute C185 now. NO status-only replies. NO status summary before >= 3 NEW concrete C185 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected in state; run-time grep required)
`VOLUME_RQA_TT_OVER_LAVG_RATIO_SHOCK_MR` — RQA ratio **TT/LAVG** on delay-embedded log-volume returns. TT = trapping time = mean diagonal line length over qualifying diagonal lines (k>=1, excluding LOI, l>=l_min); LAVG = mean diagonal line length over qualifying diagonal lines on the same recurrence matrix. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `LAVG==0` or undefined/non-finite/degenerate (no qualifying diagonal lines), `TT` undefined/non-finite/degenerate, denominator/ratio non-finite, or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `TT` numerator with `LAVG` denominator — pairing not used in C125–C184. `TT_OVER_LAVG` tokens absent across scripts/strategies/backtest/utils at preselect (grep 0 at 20261107T232110Z).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'TT_OVER_LAVG|tt_over_lavg|rqa_ratio_tt_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback (e.g., `ENTR_OVER_LAVG`; record grep cmd/hits/evidence), record chosen feature in artifacts/state.

### Required C185 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C183/C184): `scripts/run_real_quote_volume_rqa_tt_over_lavg_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T232110Z.json` (f1df4ec5626cbe025c9b43837d30d4b04cd75c7b67f089e24d7ab72ad67fda45), cite C184 OOS SHA 98094a4533fa0a17a24f0d4d05b88dce785de0b76054909eeef0daf55d7e29be (and C183 ref as needed). Emit `reports/real_quote_volume_rqa_tt_over_lavg_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 185) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T232110Z.json` (f1df4ec5626cbe025c9b43837d30d4b04cd75c7b67f089e24d7ab72ad67fda45). Structurally consistent; include prior + C185 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign185_execution_summary_<UTC>.json` listing **all new C185 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C185`, `next_campaign:C186`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c186_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C185, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C185 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T232110Z)
- C104–C184 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C183 `DET_OVER_LAVG` completed/verified (exposure OOS, no edge proven).
- C184 `RR_OVER_LAVG` completed/verified (exposure OOS, no edge proven; all cost slices negative cross-asset net: fee0=-1.1137172605480297..fee40=-3.6737172605480293).
- C185 `TT_OVER_LAVG` preselect grep verified 0 — eliminates collision-search delay. Grep-zero fallback observed: `ENTR_OVER_LAVG`.
- Single durable handoff + `state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'TT_OVER_LAVG|tt_over_lavg|rqa_ratio_tt_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# then: implement/run C185 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C185-done/C186-next with grep-verified C186 preselection
```

## NEXT FOCUS CAMPAIGN — C186 (preselect at end of C185; HEAVY WORK MANDATORY)
After C185 completes, **C186 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C185 (verify by grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c186_preselected`, then execute C186 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
