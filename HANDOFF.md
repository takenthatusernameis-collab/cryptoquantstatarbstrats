# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T235500Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T235500Z; SHAs verified from bytes) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest` unavailable (do **NOT** fabricate tests).
- Real caches present (tracked in prior registries/provenance): `data/cache/volume_1h_full.pkl`, `volume_1h_full.meta.json`, `volume_1h_full.provenance.json`, spot `0bab5d6a...631fcf7.pkl`.
- **C185 complete/locked on disk (SHAs from bytes):** OOS `reports/real_quote_volume_rqa_tt_over_lavg_ratio_shock_mr_costed_oos_20261107T234714Z.json`=f3960f34d4cf93494d59ed808c27c94b59150c72abece500ce1b0512344da4f4 (`strategy_id` field inside JSON reads `VOLUME_RQA_RR_OVER_LAVG_RATIO_SHOCK_MR` — **metadata label anomaly vs filename/state family TT_OVER_LAVG; do NOT rerun C185, do NOT claim edge; cite SHA + note anomaly in any C186 registry that references C185**), `oos_edge_proven:false`, `edge_claim:NONE`, `any_exposure_oos:true`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset nets: fee0=-0.6085737738475036, fee5=-0.9095737738475038, fee10=-1.210573773847504, fee20=-1.8125737738475038, fee40=-3.016573773847504, `real_data_only:true`, `fail_closed:true`. Ingest `reports/real_feed_ingest_attempt_20261107T234818Z.json`=5fa176cd3f6056b9784d620d581f3ffa88451d1210cf77f656beaa52bf1e01e8 (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`). Registry `reports/strategy_edge_registry_20261107T234931Z.json`=12839fa67ac4d6ac6b82e8aaace9ed1a9b2a27f0164c594ea4c4e626b0809e44 (supersedes C184 registry f1df4ec5626cbe025c9b43837d30d4b04cd75c7b67f089e24d7ab72ad67fda45). Script `scripts/run_real_quote_volume_rqa_tt_over_lavg_ratio_shock_mr_costed_oos.py`=73033702c79fbf5b86de8f52b1ae1ae709345cd70ce0a888ebdae30a47e4155d (SHA from bytes; differs from state-recorded SHA — cite file SHA 73033702... if referencing; anomaly recorded, no rerun). Summary `reports/campaign185_execution_summary_20261107T234931Z.json`=85950a5b6770b27586b90a4ed9172a071dc661500ff8630eebd292ceaf7538ff. `research_state/state.yaml` = C185 done / C186 next (6b0e935cfc24168d2ec9f4e45e95843e856c19c46e69645568388ad0338308f7).
- **C186 preselected `VOLUME_RQA_ENTR_OVER_LAVG_RATIO_SHOCK_MR` => 0 non-self hits in implementation dirs** (verified 20261107T235500Z): `grep -rnE 'ENTR_OVER_LAVG|entr_over_lavg|rqa_ratio_entr_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l` => 0. **Re-verify at C186 run time (0 non-self) before implementation.** Fallback if collides: pick another grep-zero RQA-ratio candidate not used in C125–C185 (e.g., `LAM_OVER_LAVG` or `LAM_OVER_DET` — verify 0 non-self, record grep cmd/hits/evidence).
- Prior C104–C185 remain locked.

## C104–C185 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T234931Z.json` (12839fa67ac4d6ac6b82e8aaace9ed1a9b2a27f0164c594ea4c4e626b0809e44). Use it as `PRIOR_REGISTRY`; cite C185 OOS SHA f3960f34d4cf93494d59ed808c27c94b59150c72abece500ce1b0512344da4f4 and note the C185 in-file `strategy_id` label anomaly (RR_OVER_LAVG) without rerunning.

## INITIAL TASK — C186 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T235500Z
**Execute C186 now. NO status-only replies. NO status summary before >= 3 NEW concrete C186 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected in state; run-time grep required)
`VOLUME_RQA_ENTR_OVER_LAVG_RATIO_SHOCK_MR` — RQA ratio **ENTR/LAVG** on delay-embedded log-volume returns. ENTR = entropy of diagonal line lengths over qualifying diagonal lines (k>=1, excluding LOI, l>=l_min), computed from normalized diagonal-line-length distribution on that recurrence matrix; LAVG = mean diagonal line length over qualifying diagonal lines on the same recurrence matrix. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `LAVG==0` or undefined/non-finite/degenerate (no qualifying diagonal lines), `ENTR` undefined/non-finite/degenerate, denominator/ratio non-finite, or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `ENTR` numerator with `LAVG` denominator — pairing not used in C125–C185. `ENTR_OVER_LAVG` tokens absent in scripts/strategies/backtest/utils at 20261107T235500Z.

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'ENTR_OVER_LAVG|entr_over_lavg|rqa_ratio_entr_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback not used in C125–C185 (record grep cmd/hits/evidence), record chosen feature in artifacts/state.

### Required C186 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C183–C185): `scripts/run_real_quote_volume_rqa_entr_over_lavg_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T234931Z.json` (12839fa67ac4d6ac6b82e8aaace9ed1a9b2a27f0164c594ea4c4e626b0809e44), cite C185 OOS SHA f3960f34d4cf93494d59ed808c27c94b59150c72abece500ce1b0512344da4f4 and note its in-file `strategy_id` label anomaly (RR_OVER_LAVG) — no rerun. Emit `reports/real_quote_volume_rqa_entr_over_lavg_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence). Ensure `strategy_id` matches the feature family (do not repeat C185 label anomaly).
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 186) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T234931Z.json` (12839fa67ac4d6ac6b82e8aaace9ed1a9b2a27f0164c594ea4c4e626b0809e44). Structurally consistent; include prior + C186 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign186_execution_summary_<UTC>.json` listing **all new C186 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C186`, `next_campaign:C187`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c187_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C186, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C186 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T235500Z)
- C104–C185 locked; C185 artifact SHA integrity verified from bytes. No reruns.
- Recorded C185 metadata anomalies (OOS in-file `strategy_id` RR_OVER_LAVG vs TT family; script SHA differs from state record) so next agent does not waste cycles investigating/rerunning — cite SHAs, note anomaly, proceed.
- Deps/caches ready (`deps_ok`, required cache/provenance files present).
- C186 `ENTR_OVER_LAVG` collision guard verified 0 in implementation dirs (20261107T235500Z).
- Single durable handoff + `state.yaml` are the only coordination sources.
- `pytest` unavailable recorded honestly.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'ENTR_OVER_LAVG|entr_over_lavg|rqa_ratio_entr_over_lavg' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# then: implement/run C186 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C186-done/C187-next with grep-verified C187 preselection
```

## NEXT FOCUS CAMPAIGN — C187 (preselect at end of C186; HEAVY WORK MANDATORY)
After C186 completes, **C187 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C186 (verify by grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c187_preselected`, then execute C187 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
