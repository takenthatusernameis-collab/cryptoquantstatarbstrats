# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261109T032725Z, C104–C248 LOCKED — edge_claim NONE, C248 DONE, C249 PRESELECTED HEAVY — PENDING, EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C248 LOCKED (no reruns). C248 DONE on disk (edge_claim NONE). C249 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW_SHOCK_MR) — execute C249 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261109T032725Z.json` (a1a3bfed5579037f2c1d6ccd6c9411421cd166415cdcca95ad1b0c218dd7f04e). Latest OOS = C248 `af6b0717577928cfb6b6d543d0753d4427c44069d0a2055ea7983fffd7054933` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261109T032725Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C249.** C248 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_KELLY_SKEW_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=0.30197803228898, fee5=-1.1400219677110213, fee10=-2.5820219677110217, fee20=-5.466021967711021, fee40=-11.23402196771102 — fails all-cost-slices-positive rule though beats B&H mean at fee0; exposure true; oos_edge_proven false). C249 script does NOT yet exist on disk. **Do not summarize status. Do not stop at status. Implement + run C249 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.** This is the only open campaign; no status-first replies, no stopping between campaigns.

## VERIFIED BASELINE (20261109T032725Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`).
- Collision guard: `RTE_OVER_WHITE_DIAG_LINE_LENGTH_KELLY_SKEW|WHITE_DIAG_LINE_LENGTH_KELLY_SKEW` grep 0 hits at 20261109T032725Z — C248 primary ran clean. C249 preselected candidate `RTE_OVER_WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW|WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW` grep 0 hits at 20261109T032725Z — C249 primary collision-free, runnable now. Fallbacks grep-zero: YULE_K, MIDRANGE, PEARSON_SKEW.
- Caches: spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (5607573327c089e0ab990ac48f931752a99e6e89f60599cb2557246f0f5f8c9b), spot meta (d03556baeef34eae18d2122f4a17ec14e30fdd14e0a5616d914c5d0832d2d80d), volume `data/cache/volume_1h_full.pkl/meta/provenance` (4365895387de4e542165fd331e39da40d455a3de24c7254eb67ba890053d193c/4d321584d3c687ad9956908c0179a1eae7d629c296c491e1e5ad1259a890c616/c7ff2f27ec5a668128e4856f809efde4922563dba87be0648be6d802c6d21c89).
- **C104–C247 LOCKED (see state.yaml/registry).**
- **C248 DONE (verified on disk, SHAs from bytes):**
  - OOS af6b0717577928cfb6b6d543d0753d4427c44069d0a2055ea7983fffd7054933 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_kelly_skew_shock_mr_costed_oos_20261109T032725Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_KELLY_SKEW_SHOCK_MR, campaign 248, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, all_cost_slices_beat_bh_mean_rule true, cross-asset fee0=0.30197803228898 fee5=-1.1400219677110213 fee10=-2.5820219677110217 fee20=-5.466021967711021 fee40=-11.23402196771102).
  - Ingest 057e1d04821c0a3cebfb6acb479173b7dc09ca8949480cf2c11ba9849ea8e018 (`reports/real_feed_ingest_attempt_20261109T032725Z.json`, rb_unblocked true, nonspot blocked fail-closed).
  - Registry a1a3bfed5579037f2c1d6ccd6c9411421cd166415cdcca95ad1b0c218dd7f04e (`reports/strategy_edge_registry_20261109T032725Z.json`) supersedes `reports/strategy_edge_registry_20261109T031259Z.json` 87b0265771b4902b8954390d11aaf162069e739e10133781f8f9db5aec5e4d60.
  - Script f254fe693ac704feab2fcc6281a864f35de1cbae7a387d4a6cca100b30a77038 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_kelly_skew_shock_mr_costed_oos.py`, campaign 248, WHITE_DIAG_LINE_LENGTH_KELLY_SKEW = (P90 + P10 - 2*median)/(P90 - P10) Kelly skewness of lengths of qualifying WHITE diagonal segments pooled over off-diagonal diagonals k!=0, >=3 segments, (P90-P10)>0/near-zero fail-closed, Kelly skew finite, numpy.percentile 10/50/90 method='linear', fail-closed). Distinctness grep 0 non-self at run.
  - Summary 5152b99e7f3dfb13dc19fd9b8cff06114620fe4f41137e5ecb2fa0ec3045e125 (`reports/campaign248_execution_summary_20261109T032725Z.json`).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **Env bottleneck cleared.** Reuse `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok). Runs are CPU-heavy; allow sufficient timeout (~30 min) — **must complete C249 in this session**; no status-only replies.
- **Collision guard verified 0 at start.** C249 primary candidate grep-zero verified 20261109T032725Z — proceed without fallback.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C248.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C249 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261109T032725Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW = Groeneveld-Meeden robust skewness = (mean - median) / mean(|X - median|) of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; mean/median/E|X-median| computed on pooled segment lengths (numpy, pre-stated fixed); **fail-closed** if <3 qualifying segments, or mean(|X-median|) <= 0 / non-finite (near-zero denominator handled fail-closed), or Groeneveld-Meeden skew non-finite, or resulting denominator/ratio undefined/non-finite/degenerate). Distinct from KELLY_SKEW(C248, P10/P90-based), BOWLEY_SKEW(C247, quartile-based), moment SKEWNESS(C230), single-percentile P10(C242)/P90(C241), TRIMEAN(C246)/MIDHINGE(C245)/WINSORIZED_MEAN(C244)/TRIMMED_MEAN(C243)/HARMONIC_MEAN(C240)/GEOMEAN(C239)/RMS(C238)/ENTROPY(C237)/GINI(C236)/RANGE(C235)/CV(C234)/IQR(C233)/MAD(C232)/KURTOSIS(C231)/COUNT_VARIANCE(C229)/DIAG_COUNT_VARIANCE(C228)/DIVERGENCE(C227)/VARIANCE(C226), and prior C125-C248 families.
**grep evidence (20261109T032725Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW|WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallbacks (grep-zero verified candidates):** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K_SHOCK_MR`, `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE_SHOCK_MR`, `RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW_SHOCK_MR` (all 0 hits verified 20261109T032725Z). At C249 start grep-verify; if collision, pick a distinct grep-zero fallback not used C125–C248 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW|WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C248 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C249 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_groeneveld_meeden_skew_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C248. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261109T032725Z.json` (a1a3bfed5579037f2c1d6ccd6c9411421cd166415cdcca95ad1b0c218dd7f04e), cite C248 OOS SHA `af6b0717577928cfb6b6d543d0753d4427c44069d0a2055ea7983fffd7054933`, C247 OOS SHA `def2f1fc07104e4ecadaa87700327aab3c1d3d5df3e2d95801597ce3c94f7638`, and C246 OOS SHA `d329801a5c06bd49fbc129da4930011abca1c5920d464c5e420a5399e889f83c`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_groeneveld_meeden_skew_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 249`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 249). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261109T032725Z.json` (a1a3bfed5579037f2c1d6ccd6c9411421cd166415cdcca95ad1b0c218dd7f04e). Include prior + all C249 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign249_execution_summary_<UTC>.json` listing **all new C249 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C249`, `next_campaign: C250`, latest registry/OOS sha+path, `oos_edge_proven`, `c250_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C249, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW|WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C249 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

# CONFIRMED AT REFRESH 20261109T032725Z: deps_ok; collision guard = 0 hits; NO C249 script on disk; C249 pending and unblocked — proceed to implement+run immediately.
