# READ THIS FIRST — SINGLE DURABLE HANDOFF (NEXT AGENT START: 2026-11-08T00:43:14Z)
**Repo:** `cryptoquantstatarbstrats` (crypto quant stat arb strategies). Priority (inferred from repo name): fail-closed, **real-data-only** stat-arb edge validation — walk-forward OOS, costed backtests, B&H comparison, full provenance/SHA256. **Claim edge ONLY if the exact fail-closed edge rule holds.** R-B proceeds on validated `real_quote_volume` regardless of nonspot ingest. **C104–C186 are LOCKED — do not rerun unchanged.**

## VERIFIED BASELINE (20261107T235740Z state; rechecked 2026-11-08T00:43Z) — no reruns
- `deps_ok`: numpy/scipy/pandas importable. `pytest 9.2.0` available.
- Caches present: `data/cache/volume_1h_full.pkl`, `volume_1h_full.meta.json`, `volume_1h_full.provenance.json`, spot `0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl`.
- C186 complete/locked (SHAs from bytes): OOS `reports/real_quote_volume_rqa_entr_over_lavg_ratio_shock_mr_costed_oos_20261107T235627Z.json`=8c249216f6e7fdd0805782248185741a1eb2c5f5ab265d0b804f03da2fddc1df (`VOLUME_RQA_ENTR_OVER_LAVG_RATIO_SHOCK_MR`, `oos_edge_proven:false`, `edge_claim:NONE`, exposure true, all-cost-positive false, beats-BH-mean false). Ingest `reports/real_feed_ingest_attempt_20261107T235718Z.json`=cb5169c3905fb579384769be3c5f56a1cc08c7d7b0b15bc94ed58333239c50fd (nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`). Registry `reports/strategy_edge_registry_20261107T235740Z.json`=32245884262f787ae8889d77dcb606b367a6f2f5d3f64a026af085615bc9bc61 supersedes C185 registry 12839fa67ac4d6ac6b82e8aaace9ed1a9b2a27f0164c594ea4c4e626b0809e44. Script `scripts/run_real_quote_volume_rqa_entr_over_lavg_ratio_shock_mr_costed_oos.py`=5bbf466567a838dfc9aa9cecd4647aa2e6957b26faa0de5480f9e221f0e8cba9. Summary `reports/campaign186_execution_summary_20261107T235740Z.json` present.
- C185 anomaly recorded (no rerun): C185 in-file `strategy_id` label RR_OVER_LAVG vs TT family; SHA f3960f34d4cf93494d59ed808c27c94b59150c72abece500ce1b0512344da4f4 verified; `edge_claim:NONE`.
- C187 primary grep precheck (20261107T235740Z): `LAVG_OVER_ENTR|lavg_over_entr|rqa_ratio_lavg_over_entr|rqa_lavg_over_entr_ratio` => **0 non-self hits** in `scripts/ strategies/ backtest/ utils/`. **Re-verify 0 non-self at C187 run time before implementation.**

## BOTTLENECKS REMOVED / NO EXCUSES (2026-11-08T00:43Z)
- C104–C186 locked; artifact SHAs verified; no reruns, no stale cache re-scans, no gate/threshold weakening, no proxies labeled real.
- Deps/caches ready; pytest available. Nonspot ingest blocker does **not** block R-B on `real_quote_volume`.
- Single durable handoff = `HANDOFF.md` + `research_state/state.yaml`. No other TODO/NEXT/SESSION files.
- **No status-only replies. No “summarize then stop”. No waiting.** Work starts by running the prereq/grep commands and implementing C187.

## INITIAL TASK — C187 (MANDATORY, HEAVY WORK, START IMMEDIATELY)
**Execute C187 now.** You must produce **>= 3 NEW concrete C187 report artifacts on disk** (OOS + ingest + registry/superseding + summary) **each with SHA256 computed from bytes**, plus the OOS script and synced `research_state/state.yaml`. A status summary is allowed **only after** these artifacts exist.

### Primary candidate (preselected; run-time grep required)
`VOLUME_RQA_LAVG_OVER_ENTR_RATIO_SHOCK_MR` — RQA ratio **LAVG/ENTR** on delay-embedded log-volume returns (inverse of C186). LAVG = mean diagonal line length over qualifying diagonal lines (k>=1, excluding LOI, l>=`l_min`) on the recurrence matrix; ENTR = Shannon entropy (natural log) of diagonal line lengths over qualifying diagonal lines, from the normalized diagonal-line-length distribution on that recurrence matrix. Params: `m=2,tau=1,eps=0.5*std(r_window),W_RR=168,l_min=2`. **Fail-closed NaN/no-signal** if `ENTR==0` or ENTR undefined/non-finite/degenerate, LAVG undefined/non-finite/degenerate, denominator/ratio non-finite, or undefined. Trailing/causal only. Pre-stated distinctness: LAVG numerator / ENTR denominator inverse pairing of C186; not used C125–C186; grep 0 at preselect.

### Collision guard (required at run time)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
grep -rnE 'LAVG_OVER_ENTR|lavg_over_entr|rqa_ratio_lavg_over_entr|rqa_lavg_over_entr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self for primary
```
If collides: pick a grep-zero fallback not used in C125–C186 (e.g., `TREND_OVER_DET` — grep 0 observed 20261107T235740Z; **verify 0 non-self**), record chosen feature + grep cmd/hits/evidence in artifacts/state.

### Required C187 deliverables (all on disk, SHA256 from bytes)
1. **OOS script + run** (model on C185–C186): `scripts/run_real_quote_volume_rqa_lavg_over_entr_ratio_shock_mr_costed_oos.py` (or collision-safe alternative). Change only feature computation, IDs, `pre_stated_distinctness`, and refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261107T235740Z.json` (32245884262f787ae8889d77dcb606b367a6f2f5d3f64a026af085615bc9bc61), cite C186 OOS SHA 8c249216f6e7fdd0805782248185741a1eb2c5f5ab265d0b804f03da2fddc1df. Emit `reports/real_quote_volume_rqa_lavg_over_entr_ratio_shock_mr_costed_oos_<UTC>.json` with `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `cross_asset.oos_net_sums`, `edge_claim:"NONE"` unless rule holds, `real_data_only:true`, `fail_closed:true`, `pre_stated_distinctness` (grep cmd/hits/evidence). `strategy_id` must match family.
2. **Ingest:** `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 187) — nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`; include cache/provenance SHAs.
3. **Registry (superseding):** `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261107T235740Z.json` (32245884262f787ae8889d77dcb606b367a6f2f5d3f64a026af085615bc9bc61). Include prior + C187 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary:** `reports/campaign187_execution_summary_<UTC>.json` listing **all new C187 artifact paths + sha256 from bytes**.
5. **Sync state:** `research_state/state.yaml` → `latest_campaign_done:C187`, `next_campaign:C188`, latest registry/OOS sha+path, `oos_edge_proven` from emitted report, `c188_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C187, with grep cmd/hits/evidence). **Do not copy stale candidates.**

## Fail-closed edge rule (EXACT)
`oos_edge_proven=true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF `720/168/168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.

## Mandatory rules (HARD)
- Real data only; fail-closed. No proxies labeled real; no fabricated feeds/provenance/results.
- No pairs/feed re-scans on same stale cache; no prior campaign reruns unchanged; no gate/threshold weakening.
- Edge claim ONLY if rule holds. Pre-state distinctness; grep-verify before implementation/run; record evidence.
- **No status summary before >= 3 new concrete C187 artifacts exist.** Heavy work mandatory.

## Immediate first actions (run, then build)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python3 -c "import numpy,scipy,pandas; print('deps_ok')"
ls data/cache/volume_1h_full.pkl data/cache/volume_1h_full.meta.json data/cache/volume_1h_full.provenance.json data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl
grep -rnE 'LAVG_OVER_ENTR|lavg_over_entr|rqa_ratio_lavg_over_entr|rqa_lavg_over_entr_ratio' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 for primary
# implement+run C187 -> emit OOS+ingest+registry+summary (>=3) with SHAs -> sync state.yaml
```

## NEXT FOCUS CAMPAIGN — C188 (MANDATORY after C187; HEAVY WORK)
C188 is not optional. After C187 artifacts/state are synced, preselect a **distinct grep-verified** RQA-ratio candidate not used in C125–C187 (grep 0 non-self), record grep cmd/hits/evidence in `state.yaml.c188_preselected`, then **execute C188** under the same deliverable/edge-rule template. **No status-only replies. No stop after status.** If C187 is blocked only by a collision, switch to a grep-zero fallback and continue — do not stall.
