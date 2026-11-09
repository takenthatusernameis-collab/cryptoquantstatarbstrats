# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261109T014330Z, C104–C243 LOCKED — edge_claim NONE, C243 DONE, C244 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C243 LOCKED (no reruns). C243 DONE on disk (edge_claim NONE). C244 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN_SHOCK_MR) — execute C244 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261109T014330Z.json` (9751625c168c58db60e03180a156f167e6039e816aa7cc4edb94494e7d39a381). Latest OOS = C243 `35bd7caf8c10d0c333219c5df005d614efe57a87bb193e817dab02bd4dc1c712` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261109T014330Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C244.** C243 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=-2.5609096071284805, fee5=-3.4009096071284812, fee10=-4.240909607128482, fee20=-5.920909607128482, fee40=-9.28090960712848 — all cost slices negative; exposure true; oos_edge_proven false). C244 script does NOT yet exist on disk. **Do not summarize status. Do not stop at status. Implement + run C244 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261109T014330Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`).
- Caches: spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...), spot meta (d03556ba...), volume `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...).
- **C240 DONE (locked):** HARMONIC_MEAN, oos d24b0a8b45ec2ef767b53ff1f4493586fb8ac66d6208b60d6833cf8429093f23, edge_claim NONE.
- **C241 DONE (locked):** P90, oos 94914f1f2ec9c0b8f15c159a3665019573c639ba2cb888754fcac103996be3db, registry bb9b240eb748942a36e28f5da8279a656ca6da3ed8aff1f463e740871247d8fa, edge_claim NONE.
- **C242 DONE (locked):** P10, oos 5655c52e9bae7e7a7b90b1aef133497bbd6e6eb1bbecec58e977ca0e13242808, registry d7100bc45fff0a3d9ef26fa7aa07dd52133bf6c865af4fc9768f96218ed974bf, edge_claim NONE.
- **C243 DONE (verified on disk, SHAs from bytes):**
  - OOS 35bd7caf8c10d0c333219c5df005d614efe57a87bb193e817dab02bd4dc1c712 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_trimmed_mean_shock_mr_costed_oos_20261109T014330Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN_SHOCK_MR, campaign 243, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, all_cost_slices_beat_bh_mean_rule false, cross-asset fee0=-2.5609096071284805 fee5=-3.4009096071284812 fee10=-4.240909607128482 fee20=-5.920909607128482 fee40=-9.28090960712848).
  - Ingest 4e5b15e06d67f85c752758e0bf8fa5ba3113e4be126ef18864eb62c08bdce11c (`reports/real_feed_ingest_attempt_20261109T014330Z.json`, rb_unblocked true, nonspot blocked fail-closed).
  - Registry 9751625c168c58db60e03180a156f167e6039e816aa7cc4edb94494e7d39a381 (`reports/strategy_edge_registry_20261109T014330Z.json`) supersedes `reports/strategy_edge_registry_20261109T012706Z.json` d7100bc45fff0a3d9ef26fa7aa07dd52133bf6c865af4fc9768f96218ed974bf.
  - Script f0172936a8b9ea7fc6a2dfaa7bea6874ac006a1c07536926461705ab73f029f8 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_trimmed_mean_shock_mr_costed_oos.py`, campaign 243, WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN = scipy.stats.trim_mean proportiontocut=0.1 (10% each tail) of qualifying WHITE diagonal segments, >=3 segments, trimmed mean>0; fail-closed). Distinctness grep 0 non-self at run.
  - Summary 040d86e40136a7af1bf598c476691b3482bfd2fecfe2668a313318bca2eadb95 (`reports/campaign243_execution_summary_20261109T014330Z.json`).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **Env bottleneck cleared.** Reuse `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok). Runs are CPU-heavy; allow sufficient timeout (~30 min) — **must complete C244 in this session**; no status-only replies.
- **Collision guard required at start.** C244 primary candidate is grep-zero verified 20261109T014330Z.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C243.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C244 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261109T014330Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN = winsorized mean — apply `scipy.stats.mstats.winsorize` with limits `[0.1,0.1]` = 10% each tail then arithmetic mean — of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; fail-closed if <3 qualifying segments or winsorized mean non-finite/non-positive). Distinct from TRIMMED_MEAN(C243), P10(C242), P90(C241), HARMONIC_MEAN(C240), GEOMEAN(C239), RMS(C238), ENTROPY(C237), GINI(C236), RANGE(C235), CV(C234), IQR(C233), MAD(C232), KURTOSIS(C231), SKEWNESS(C230), COUNT_VARIANCE(C229), DIAG_COUNT_VARIANCE(C228), DIVERGENCE(C227), VARIANCE(C226), and prior C125-C243 families.
**grep evidence (20261109T014330Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN|WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallbacks (grep-zero verified candidates):** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDHINGE_SHOCK_MR`, `RTE_OVER_WHITE_DIAG_LINE_LENGTH_TRIMEAN_SHOCK_MR` (verify at start). At C244 start grep-verify; if collision, pick a distinct grep-zero fallback not used C125–C243 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN|WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C243 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C244 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_winsorized_mean_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C243. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261109T014330Z.json` (9751625c168c58db60e03180a156f167e6039e816aa7cc4edb94494e7d39a381), cite C243 OOS SHA `35bd7caf8c10d0c333219c5df005d614efe57a87bb193e817dab02bd4dc1c712`, C242 OOS SHA `5655c52e9bae7e7a7b90b1aef133497bbd6e6eb1bbecec58e977ca0e13242808`, and C241 OOS SHA `94914f1f2ec9c0b8f15c159a3665019573c639ba2cb888754fcac103996be3db`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_winsorized_mean_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 244`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 244). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261109T014330Z.json` (9751625c168c58db60e03180a156f167e6039e816aa7cc4edb94494e7d39a381). Include prior + all C244 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign244_execution_summary_<UTC>.json` listing **all new C244 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C244`, `next_campaign: C245`, latest registry/OOS sha+path, `oos_edge_proven`, `c245_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C244, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN|WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C244 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```
