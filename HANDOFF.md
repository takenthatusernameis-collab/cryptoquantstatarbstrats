# READ THIS FIRST — SINGLE DURABLE HANDOFF (REFRESHED 20261109T012706Z, C104–C242 LOCKED — edge_claim NONE, C242 DONE, C243 PRESELECTED HEAVY — EXECUTE NEXT, NO STATUS-FIRST)
**Repo:** `cryptoquantstatarbstrats` | **Focus:** crypto quant stat-arb strategies — fail-closed, **real-data-only** edge validation. WF OOS 720/168/168, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same windows. **Claim edge ONLY if** OOS exposure>0 AND for ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net. R-B unblocked on validated `real_quote_volume`; nonspot blocked fail-closed. **C104–C242 LOCKED (no reruns). C242 DONE on disk (edge_claim NONE). C243 preselected grep-zero (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN_SHOCK_MR) — execute C243 next, no status-first.** Latest registry = `reports/strategy_edge_registry_20261109T012706Z.json` (d7100bc45fff0a3d9ef26fa7aa07dd52133bf6c865af4fc9768f96218ed974bf). Latest OOS = C242 `5655c52e9bae7e7a7b90b1aef133497bbd6e6eb1bbecec58e977ca0e13242808` (oos_edge_proven false).

## TIMESTAMPED INITIAL TASK MESSAGE (20261109T012706Z) — HEAVY WORK MANDATORY
**PRIORITY 1: EXECUTE C243.** C242 is complete on disk (VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_P10_SHOCK_MR, edge_claim NONE; cross-asset net sums fee0=0.3828757410033743, fee5=0.036875741003373985, fee10=-0.3091242589966263, fee20=-1.001124258996627, fee40=-2.385124258996627 — not all cost slices positive (fee0,fee5 positive but fee10-40 negative), all_cost_slices_beat_bh_mean_rule true as recorded in OOS; exposure true; oos_edge_proven false). C243 script does NOT yet exist on disk. **Do not summarize status. Do not stop at status. Implement + run C243 + emit >=4 artifacts with SHA256 from bytes + sync state.yaml + HANDOFF.**

## VERIFIED BASELINE (20261109T012706Z)
- deps_ok (numpy/scipy/pandas 2.5.4/1.18.1/3.1.1, `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python`).
- Caches: spot `data/cache/0bab5d6a902481b313752a935d4517c9ec3b07e9a5064db5805b77dbe631fcf7.pkl` (56075733...), spot meta (d03556ba...), volume `data/cache/volume_1h_full.pkl/meta/provenance` (43658953.../4d321584.../c7ff2f27...).
- **C239 DONE (locked):** GEOMEAN, oos 76b139d6065b9366495f2fbdcb99bb9a2df4473bdaf0329d3b0a79f97fc3b61d, edge_claim NONE.
- **C240 DONE (locked):** HARMONIC_MEAN, oos d24b0a8b45ec2ef767b53ff1f4493586fb8ac66d6208b60d6833cf8429093f23, registry 453a374c47bdb0a634ec91ecaa86a3cb461e6d2e13d604227eff49f162bdda19, edge_claim NONE.
- **C241 DONE (locked):** P90, oos 94914f1f2ec9c0b8f15c159a3665019573c639ba2cb888754fcac103996be3db, registry bb9b240eb748942a36e28f5da8279a656ca6da3ed8aff1f463e740871247d8fa, edge_claim NONE.
- **C242 DONE (verified on disk, SHAs from bytes):**
  - OOS 5655c52e9bae7e7a7b90b1aef133497bbd6e6eb1bbecec58e977ca0e13242808 (`reports/real_quote_volume_rqa_rte_over_white_diag_line_length_p10_shock_mr_costed_oos_20261109T012706Z.json`, VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_P10_SHOCK_MR, campaign 242, edge_claim NONE, oos_edge_proven false, any_exposure_oos true, all_cost_slices_positive false, all_cost_slices_beat_bh_mean_rule true, cross-asset fee0=0.3828757410033743 fee5=0.036875741003373985 fee10=-0.3091242589966263 fee20=-1.001124258996627 fee40=-2.385124258996627).
  - Ingest 14a0b7096e2dbda5a7cc62a686b79d5a72039faad9d4fbca271af103ac927c06 (`reports/real_feed_ingest_attempt_20261109T012706Z.json`, rb_unblocked true, nonspot blocked fail-closed).
  - Registry d7100bc45fff0a3d9ef26fa7aa07dd52133bf6c865af4fc9768f96218ed974bf (`reports/strategy_edge_registry_20261109T012706Z.json`) supersedes `reports/strategy_edge_registry_20261109T012117Z.json` bb9b240eb748942a36e28f5da8279a656ca6da3ed8aff1f463e740871247d8fa.
  - Script fa108310ed82c0cdc7cc6d678f8bb474c9a220cc03a2d7b2bc07946c7f939586 (`scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_p10_shock_mr_costed_oos.py`, campaign 242, WHITE_DIAG_LINE_LENGTH_P10 = 10th percentile (numpy linear interpolation) of qualifying WHITE diagonal segments, >=3 segments, P10>0; fail-closed). Distinctness grep 0 non-self at run.
  - Summary e51fd33d4bc37003288e4a5b15382ababbd2386c2850fa1eb4fc9293d9b32705 (`reports/campaign242_execution_summary_20261109T012706Z.json`).
- Single durable handoff = this file + `research_state/state.yaml`.

## BOTTLENECKS REMOVED / MANDATES (NO EXCUSES)
- **Env bottleneck cleared.** Reuse `/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python` (deps_ok). Runs are CPU-heavy; allow sufficient timeout (~30 min) — **must complete C243 in this session**; no status-only replies.
- **Collision guard required at start.** C243 primary candidate is grep-zero verified 20261109T012706Z.
- **No status-first.** Artifacts on disk are the deliverable.
- **No reruns of locked campaigns C104–C242.** No gate/threshold weakening, no proxies labeled real, no fabricated feeds/provenance/results.
- **Collision handling is fail-closed:** if a preselected candidate collides on grep, reject it, pick a distinct grep-zero fallback, record primary/fallback grep cmd/hits/evidence in all artifacts + state + HANDOFF.
- **Real-data-only, fail-closed.** Nonspot blocked fail-closed; R-B unblocked on validated `real_quote_volume`.
- **Distinctness enforced.** Grep-verify candidate before implementation/run and record evidence.
- **Heavy work mandatory.** No status-only replies. No stop between campaigns.

## C243 — NEXT FOCUS CAMPAIGN (PRESELECTED, GREP-ZERO VERIFIED 20261109T012706Z)
**Primary candidate:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN_SHOCK_MR` — RQA ratio RTE / WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN on delay-embedded log-volume returns (RTE = recurrence time entropy of white vertical gap distribution, w>=w_min, LOI/self excluded; WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN = trimmed mean (numpy default 10% each tail) of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0 with >=1 qualifying segment; fail-closed if <3 qualifying segments or trimmed mean non-finite/non-positive). Distinct from P10(C242), P90(C241), HARMONIC_MEAN(C240), GEOMEAN(C239), RMS(C238), ENTROPY(C237), GINI(C236), RANGE(C235), CV(C234), IQR(C233), MAD(C232), KURTOSIS(C231), SKEWNESS(C230), COUNT_VARIANCE(C229), DIAG_COUNT_VARIANCE(C228), DIVERGENCE(C227), VARIANCE(C226), MEDIAN_ABS_DEV(C232), and prior C125-C242 families.
**grep evidence (20261109T012706Z):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN|WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN' scripts/ strategies/ backtest/ utils/ 2>&1` → 0 hits.
**Fallbacks (grep-zero verified candidates):** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_WINSORIZED_MEAN_SHOCK_MR`, `RTE_OVER_WHITE_DIAG_LINE_LENGTH_GEOMETRIC_MEAN_SHOCK_MR` (verify at start). At C243 start grep-verify; if collision, pick a distinct grep-zero fallback not used C125–C242 and record evidence.

### COLLISION GUARD (RUN AT START)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN|WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # MUST be 0 non-self
```
If collision found: pick a distinct grep-zero fallback not used C125–C242 (verify). Record chosen feature + grep cmd/hits/evidence in all artifacts + state + HANDOFF.

### REQUIRED C243 DELIVERABLES (ALL ON DISK, SHA256 FROM BYTES)
1. **OOS script + run**: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_trimmed_mean_shock_mr_costed_oos.py` (or collision-safe). Model on C188–C242. Change only feature computation, IDs, `pre_stated_distinctness`, refs: `PRIOR_REGISTRY=reports/strategy_edge_registry_20261109T012706Z.json` (d7100bc45fff0a3d9ef26fa7aa07dd52133bf6c865af4fc9768f96218ed974bf), cite C242 OOS SHA `5655c52e9bae7e7a7b90b1aef133497bbd6e6eb1bbecec58e977ca0e13242808`, C241 OOS SHA `94914f1f2ec9c0b8f15c159a3665019573c639ba2cb888754fcac103996be3db`, and C240 OOS SHA `d24b0a8b45ec2ef767b53ff1f4493586fb8ac66d6208b60d6833cf8429093f23`. Emit `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_trimmed_mean_shock_mr_costed_oos_<UTC>.json` with `pre_stated_distinctness`, `cross_asset.oos_net_sums`, `oos_edge_proven`, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, `edge_claim:"NONE"` unless rule holds. **No carryover template text; set `campaign: 243`.**
2. **Ingest**: `reports/real_feed_ingest_attempt_<UTC>.json` (campaign 243). Nonspot blocked fail-closed, `rb_unblocked:true` for validated `real_quote_volume`. Include cache/provenance SHAs.
3. **Registry (superseding)**: `reports/strategy_edge_registry_<UTC>.json` superseding `reports/strategy_edge_registry_20261109T012706Z.json` (d7100bc45fff0a3d9ef26fa7aa07dd52133bf6c865af4fc9768f96218ed974bf). Include prior + all C243 artifact paths/SHAs/scripts; `edge_claim:"NONE"` unless rule holds.
4. **Summary**: `reports/campaign243_execution_summary_<UTC>.json` listing **all new C243 artifact paths + sha256 from bytes**.
5. **Sync**: `research_state/state.yaml` → `latest_campaign_done: C243`, `next_campaign: C244`, latest registry/OOS sha+path, `oos_edge_proven`, `c244_preselected` (distinct grep-verified RQA-ratio candidate not used C125–C243, with grep cmd/hits/evidence). Update this `HANDOFF.md`.

## EDGE RULE (EXACT)
`oos_edge_proven = true` **IFF** OOS exposure > 0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows. Real data only.

## IMMEDIATE FIRST ACTIONS
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
/home/runner/work/_temp/kilo-tmp/kilo/c233-venv/bin/python -c "import numpy,scipy,pandas; print('deps_ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN|WHITE_DIAG_LINE_LENGTH_TRIMMED_MEAN' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # must be 0 non-self
# NOW: implement+run C243 -> emit >=4 artifacts with SHAs -> sync state.yaml + HANDOFF
```

(End of file - total 59 lines)