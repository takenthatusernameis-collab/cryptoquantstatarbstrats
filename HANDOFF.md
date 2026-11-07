# READ THIS FIRST — SINGLE DURABLE HANDOFF (20261107T235740Z)

Repo: `cryptoquantstatarbstrats` (crypto quant stat arb strategies).
**Priority (from repo name):** fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. Claim edge **ONLY** if the exact fail-closed edge rule holds. R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest.

## VERIFIED NOW (20261107T235740Z; SHAs verified from bytes) — no reruns needed
- `deps_ok`: numpy/scipy/pandas importable. `pytest 9.2.0` available (observed 20261107T235445Z).
- Real caches present: `data/cache/volume_1h_full.pkl`, `volume_1h_full.meta.json`, `volume_1h_full.provenance.json`, spot `0bab5d6a...631fcf7.pkl` (+meta).
- **C186 complete/locked on disk (SHAs from bytes):** OOS `reports/real_quote_volume_rqa_entr_over_lavg_ratio_shock_mr_costed_oos_20261107T235627Z.json`=8c249216f6e7fdd0805782248185741a1eb2c5f5ab265d0b804f03da2fddc1df (`strategy_id=VOLUME_RQA_ENTR_OVER_LAVG_RATIO_SHOCK_MR`, correct label), `oos_edge_proven:false`, `edge_claim:NONE`, `any_exposure_oos:true`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset nets: fee0=-0.6928474302642706, fee5=-1.116847430264271, fee10=-1.5408474302642712, fee20=-2.388847430264271, fee40=-4.08484743026427, `real_data_only:true`, `fail_closed:true`. Ingest `reports/real_feed_ingest_attempt_20261107T235718Z.json`=cb5169c3905fb579384769be3c5f56a1cc08c7d7b0b15bc94ed58333239c50fd (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`). Registry `reports/strategy_edge_registry_20261107T235740Z.json`=32245884262f787ae8889d77dcb606b367a6f2f5d3f64a026af085615bc9bc61 (supersedes C185 registry 12839fa67ac4d6ac6b82e8aaace9ed1a9b2a27f0164c594ea4c4e626b0809e44). Script `scripts/run_real_quote_volume_rqa_entr_over_lavg_ratio_shock_mr_costed_oos.py`=5bbf466567a838dfc9aa9cecd4647aa2e6957b26faa0de5480f9e221f0e8cba9. Summary `reports/campaign186_execution_summary_20261107T235740Z.json`=326240f7fd0ed316ff1b40ace98d2864e496cbf06d09d27a04da32d77121168d. `research_state/state.yaml` = C186 done / C187 next.
- **C185 anomaly (recorded, no rerun):** C185 OOS in-file `strategy_id` reads `VOLUME_RQA_RR_OVER_LAVG_RATIO_SHOCK_MR` vs TT_OVER_LAVG family (metadata label anomaly). C185 OOS SHA f3960f34d4cf93494d59ed808c27c94b59150c72abece500ce1b0512344da4f4 verified from bytes; edge_claim NONE. C185 script SHA from bytes 73033702c79fbf5b86de8f52b1ae1ae709345cd70ce0a888ebdae30a47e4155d.
- **C187 preselected `VOLUME_RQA_LAVG_OVER_ENTR_RATIO_SHOCK_MR` => 0 non-self hits in implementation dirs** (verified 20261107T235740Z): `grep -rnE 'LAVG_OVER_ENTR|lavg_over_entr|rqa_ratio_lavg_over_entr|rqa_lavg_over_entr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l` => 0. **Re-verify at C187 run time (0 non-self) before implementation.** Fallback if collides: `TREND_OVER_DET` (grep 0 observed 20261107T235740Z) or another grep-zero RQA-ratio candidate not used in C125–C186 — verify 0 non-self, record grep cmd/hits/evidence.
- Prior C104–C186 remain locked.

## C104–C186 DONE — LOCKED (DO NOT RERUN UNCHANGED)
- No prior campaign reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Latest superseding registry: `reports/strategy_edge_registry_20261107T235740Z.json` (32245884262f787ae8889d77dcb606b367a6f2f5d3f64a026af085615bc9bc61). Use it as `PRIOR_REGISTRY`; cite C186 OOS SHA 8c249216f6e7fdd0805782248185741a1eb2c5f5ab265d0b804f03da2fddc1df.

## INITIAL TASK — C187 (MANDATORY, HEAVY WORK, START IMMEDIATELY) — 20261107T235740Z
**Execute C187 now. NO status-only replies. NO status summary before >= 3 NEW concrete C187 report artifacts exist on disk** (OOS + ingest + registry/summary), **each with SHA256 computed from bytes**. Work is complete only when artifacts are emitted and `research_state/state.yaml` is synced.

### Primary candidate (preselected in state; run-time grep required)
`VOLUME_RQA_LAVG_OVER_ENTR_RATIO_SHOCK_MR` — RQA ratio **LAVG/ENTR** on delay-embedded log-volume returns (inverse pairing of C186). LAVG = mean diagonal line length over qualifying diagonal lines (k>=1, excluding LOI, l>=l_min) on the recurrence matrix; ENTR = Shannon entropy (natural log) of diagonal line lengths over qualifying diagonal lines, computed from normalized diagonal-line-length distribution on that recurrence matrix. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `ENTR==0` or `ENTR` undefined/non-finite/degenerate, `LAVG` undefined/non-finite/degenerate, denominator/ratio non-finite, or undefined. Trailing/causal only.
Distinctness (pre-stated): uses `LAVG` numerator with `ENTR` denominator — inverse of C186; pairing not used in C125–C186. `LAVG_OVER_ENTR` tokens absent in scripts/strategies/backtest/utils at 20261107T235740Z.

### Collision guard (run-time, required):
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'LAVG_OVER_ENTR|lavg_over_entr|rqa_ratio_lavg_over_entr|rqa_lavg_over_entr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback not used in C125–C186 (e.g., `TREND_OVER_DET` — grep 0 observed 20261107T235740Z; verify 0 non-self, record grep cmd/hits/evidence), record chosen feature in artifacts/state.

### Required C187 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C185–C186): `scripts/run_real_quote_volume_rqa_lavg_over_entr_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T235740Z.json` (32245884262f787ae8889d77dcb606b367a6f2f5d3f64a026af085615bc9bc61), cite C186 OOS SHA 8c249216f6e7fdd0805782248185741a1eb2c5f5ab265d0b804f03da2fddc1df. Emit `reports/real_quote_volume_rqa_lavg_over_entr_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence). Ensure `strategy_id` matches the feature family.
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 187) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T235740Z.json` (32245884262f787ae8889d77dcb606b367a6f2f5d3f64a026af085615bc9bc61). Structurally consistent; include prior + C187 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign187_execution_summary_<UTC>.json` listing **all new C187 artifact paths + sha256 from bytes** (OOS, ingest, registry, script).
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C187`, `next_campaign:C188`, latest registry sha, latest OOS path/sha, `oos_edge_proven` from emitted report, `c188_preselected` (distinct grep-verified RQA-ratio candidate not used in C125–C187, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C187 artifacts exist.** Heavy work mandatory.
- Nonspot ingest blocker does **NOT** block R-B on `real_quote_volume`.

## BOTTLENECKS REMOVED / EFFICIENCY (20261107T235740Z)
- C104–C186 locked; C185/C186 artifact SHA integrity verified from bytes. No reruns.
- Recorded C185 metadata anomaly (OOS in-file `strategy_id` RR_OVER_LAVG vs TT family) so next agent does not waste cycles investigating/rerunning.
- Deps/caches ready (`deps_ok`, required cache/provenance files present). `pytest 9.2.0` available.
- C187 `LAVG_OVER_ENTR` collision guard verified 0 in implementation dirs (20261107T235740Z); `TREND_OVER_DET` fallback grep 0.
- Single durable handoff + `state.yaml` are the only coordination sources.

## Immediate first actions
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'LAVG_OVER_ENTR|lavg_over_entr|rqa_ratio_lavg_over_entr|rqa_lavg_over_entr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# then: implement/run C187 -> emit OOS+ingest+registry+summary (>=3) -> sync state.yaml to C187-done/C188-next with grep-verified C188 preselection
```

## NEXT FOCUS CAMPAIGN — C188 (preselect at end of C187; HEAVY WORK MANDATORY)
After C187 completes, **C188 is mandatory**. Preselect a distinct grep-verified RQA-ratio candidate not used in C125–C187 (verify by grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c188_preselected`, then execute C188 under the same deliverable/edge-rule template. **No status-only replies. No stop after status.**
