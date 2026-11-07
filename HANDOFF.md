# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T223952Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T223952Z state; SHAs verified from bytes) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present + SHA-verified (from bytes): `data/cache/volume_1h_full.pkl`=4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c, `volume_1h_full.meta.json`=4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616, `volume_1h_full.provenance.json`=c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89, spot `0bab5d6a...631fcf7.pkl`=5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b.
- **C181 locked/verified on disk (SHAs from bytes):** OOS `reports/real_quote_volume_rqa_vmax_over_lavg_ratio_shock_mr_costed_oos_20261107T223952Z.json`=f01fd9687b472f502cae3bde2cd038af93e44e8b199c2c337837150fcd1a6335 (`oos_edge_proven:false`, `edge_claim:NONE`, `any_exposure_oos:true`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset nets: fee0=-0.14216190337967705, fee5=-0.37216190337967725, fee10=-0.6021619033796772, fee20=-1.0621619033796772, fee40=-1.982161903379677), ingest `reports/real_feed_ingest_attempt_20261107T223952Z.json`=be45c4ff5879c5a59f858abe9f872693be0c1799f6f508718a5ce1b8674f964e (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`), registry `reports/strategy_edge_registry_20261107T223952Z.json`=b311d5ca8a55dacb113af6448f079711dca8d0071bb684aa6a29b0a0b6d26ee2 (supersedes C180 registry 40e405929037363f538a487ebb5ca7c6f9ffcd6ebd1922ee3ad4235ec7442247, cites C180 OOS SHA 9701e5560c8c6708251be9860411e1a2912201cd406316ec50f243741a7ad50a), summary `reports/campaign181_execution_summary_20261107T223952Z.json`=1d17b5fed460c28319abfab72fde16c08fc2b6ee656e768b5ea23519129ed65e, script `scripts/run_real_quote_volume_rqa_vmax_over_lavg_ratio_shock_mr_costed_oos.py`=dbd767636146c55a5ddd50a0bb0b506832d6b2c9c30d8ae107e53865296263e9. `state.yaml` synced C181-done/C182-next.
- **C182 preselected `VOLUME_RQA_LAM_OVER_LAVG_RATIO_SHOCK_MR` => 0 hits** (`grep -rnE 'LAM_OVER_LAVG|lam_over_lavg|rqa_ratio_lam_over_lavg' scripts/ strategies/ backtest/ utils/ research_state/ HANDOFF.md reports/ 2>&1`, verified 20261107T224015Z, 0 hits). **Re-verify at C182 run time (0 non-self) before implementation.** Fallbacks if collides (grep-zero candidates observed 20261107T224015Z): `DET_OVER_LAVG`, `RR_OVER_LAVG`, `TT_OVER_LAVG` (record grep cmd/hits/evidence for chosen).
- Prior C104–C181 remain locked.

## C104–C181 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T223952Z.json` (b311d5ca8a55dacb113af6448f079711dca8d0071bb684aa6a29b0a0b6d26ee2). Use it as `PRIOR_REGISTRY`; cite C181 OOS SHA f01fd9687b472f502cae3bde2cd038af93e44e8b199c2c337837150fcd1a6335 in pre-stated refs.

## INITIAL TASK — C182 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T223952Z
**Execute C182 now. NO status-only replies. NO status summary before >= 3 NEW concrete C182 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected in state; run-time grep required)
`VOLUME_RQA_LAM_OVER_LAVG_RATIO_SHOCK_MR` — RQA ratio **LAM/LAVG** shock on delay-embedded log-volume returns. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. `LAM` = laminarity = `(sum of lengths of vertical lines with l>=l_min) / (sum of all recurrence points in R)` (vertical lines = consecutive 1s along columns, `l>=l_min`). `LAVG` = mean diagonal line length over qualifying diagonal lines (`k>=1`, excluding LOI) with `l>=l_min` on the **same** recurrence matrix. **Fail-closed NaN/no-signal** if `LAVG==0` or undefined/non-finite/degenerate (no qualifying diagonal lines), `LAM` undefined/non-finite/degenerate (no recurrence points or undefined), denominator/ratio non-finite, or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `LAM` numerator with `LAVG` denominator — pairing not used in C125–C181. `LAM_OVER_LAVG` tokens absent across scripts/strategies/backtest/utils/research_state/HANDOFF.md/reports at selection (grep 0 at 20261107T224015Z).

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'LAM_OVER_LAVG|lam_over_lavg|rqa_ratio_lam_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback (e.g., `DET_OVER_LAVG`, `RR_OVER_LAVG`, `TT_OVER_LAVG`; record grep cmd/hits/evidence), record chosen feature in artifacts/state.

### Required C182 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C181): `scripts/run_real_quote_volume_rqa_lam_over_lavg_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T223952Z.json` (b311d5ca8a55dacb113af6448f079711dca8d0071bb684aa6a29b0a0b6d26ee2), cite C181 OOS SHA f01fd9687b472f502cae3bde2cd038af93e44e8b199c2c337837150fcd1a6335. Emit `reports/real_quote_volume_rqa_lam_over_lavg_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 182) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T223952Z.json` (b311d5ca8a55dacb113af6448f079711dca8d0071bb684aa6a29b0a0b6d26ee2). Structurally consistent; include prior + C182 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign182_execution_summary_<UTC>.json` listing **all new C182 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C182`, `next_campaign:C183`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c183_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C182, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C182 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T223952Z)
- C104–C181 locked; artifact SHA integrity verified from bytes. No reruns.
- Deps/caches ready (`deps_ok`, all required cache/provenance files present and SHA-verified).
- C181 `VMAX_OVER_LAVG` completed/verified (exposure OOS, no edge proven; all cost slices negative cross-asset net).
- C182 `LAM_OVER_LAVG` preselect grep verified 0 — eliminates collision-search delay. Grep-zero fallbacks observed: `DET_OVER_LAVG`, `RR_OVER_LAVG`, `TT_OVER_LAVG`.
- Single durable handoff + `state.yaml` are the only coordination sources; next agent must not produce status-only output.
- `pytest` unavailable recorded honestly — do not waste time fabricating tests.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'LAM_OVER_LAVG|lam_over_lavg|rqa_ratio_lam_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# then: implement/run C182 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C182-done/C183-next with grep-verified C183 preselection
```

## NEXT FOCUS CAMPAIGN — C183 (preselect at end of C182; HEAVY WORK MANDATORY)
After C182 completes, **C183 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C182 (verify by grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c183_preselected`, then execute C183 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
