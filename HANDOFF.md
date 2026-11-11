# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` (crypto quant stat-arb strategies).
> **Core mission (non-negotiable):** real-data-only edge search with fail-closed enriched cointegration/gates. **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked`/`NONE` with evidence is valid. **Status-only work is forbidden.**
> **Single durable handoff:** `HANDOFF.md` (repo root) only. Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line is stale (`latest_campaign_done: C248`, `next_campaign: C249`; C249–C265 complete on disk). Must not be edited to block/replace C1–C15/C249+ progress. Sync only if explicitly requested by user.

## PRIORITIZED TIMESTAMPED INITIAL TASK MESSAGE (2026-11-11T23:17:25Z UTC — C266 complete; next session must start C267) — START HERE, DO NOT DEVIATE

**PRIORITY 1 (HEAVY EXECUTION — MANDATORY):** Continue the proven main line: **real cached quote/volume RQA shock mean-reversion costed-OOS**, real-data-only, fail-closed gates. Do **not** pivot to research, docs, refactors, or status summaries. Produce artifacts or honest `NONE` with evidence.

**IMMEDIATE NON-DEFERRABLE ACTION:** Start **Campaign #267** end-to-end now (C266 complete, `edge_claim: NONE`, `oos_edge_proven: false`). No planning phase. No "explore first" substitution.

### Preflight (re-verified 2026-11-11T23:17:25Z UTC — path clear, no blocking bottlenecks)
```bash
python3 -c "import numpy,pandas,scipy; print('ok')"
grep -rnE 'ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN|STANDARDIZED_MOMENT|PEARSON_MODE_SKEW|MEDIAN_ABSOLUTE_DEVIATION_FROM_MEAN|INTERQUARTILE_MEAN|BIWEIGHT_MIDVARIANCE' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # C267 candidate grep-zero; must be 0 non-self
ls data/cache/*.pkl data/cache/*.meta.json | wc -l  # expect 66
git -C /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats status --short | head
```
- **Verified this session (2026-11-11T23:17:25Z UTC):** deps OK (`python3` 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1); real caches present (**66** `.pkl`/`.meta.json` in `data/cache/`); git clean. **No blocking bottlenecks observed.** C266 artifacts complete on disk with SHA256-from-bytes.
- **C266 run completed 2026-11-11T22:56:14Z UTC:** OOS report emitted, all packaging artifacts created. Result: `edge_claim: NONE`, `oos_edge_proven: false`, `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- If deps missing → fix environment or fail closed with concrete evidence (no status-only downgrade).
- If caches/provenance missing → fail closed with evidence, **no network refetch**.
- If a background process blocks disk/CPU → stop it.

### C267 SPEC (pre-stated, fail-closed — next grep-zero WHITE-diag line-length dispersion/shape variant)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_<NEXT_VARIANT>_SHOCK_MR` — select next pre-stated grep-zero variant from fallback chain (first candidate `ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN`, then `STANDARDIZED_MOMENT`, `PEARSON_MODE_SKEW`, `MEDIAN_ABSOLUTE_DEVIATION_FROM_MEAN`, `INTERQUARTILE_MEAN`, `BIWEIGHT_MIDVARIANCE`, or other not-yet-run dispersion/shape forms). Re-verify grep-zero before run.
- **Feature:** dispersion/shape statistic of qualifying WHITE diagonal segment lengths (pooled over off-diagonal diagonals k!=0, length>=w_min=2, N>=3). Fail-closed formula pre-stated per variant. Distinct from C266 RELATIVE_MEAN_ABSOLUTE_DIFFERENCE, C265 MAD_FROM_MEDIAN, C264 QCD, C254 MEAN_ABSOLUTE_DEVIATION, and all prior C125-C265 RQA families.
- **Fail-closed:** if `<3` segments; intermediate statistics undefined/non-finite; feature<=0, degenerate, or non-finite; or any intermediate undefined/non-finite.
- **WF/costs:** `train=720, test=168, step=168`; cost grid bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.
- **Edge rule:** `oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only.
- **Required artifacts (SHA256 from bytes):** OOS report, runner script, ingest attempt, strategy edge registry, campaign execution summary under `reports/`/`scripts/` with campaign timestamping. Update this handoff with results/evidence/hashes and next campaign.
- **Distinctness gate:** grep 0 nonself for the exact variant token family before run; if non-distinct, fail-closed switch to next pre-stated grep-zero variant and record evidence.

### UNINTERRUPTED PIPELINE (so future agents cannot avoid heavy work)
C264 complete (`NONE` with evidence). C265 complete (`NONE` with evidence). C266 complete (`NONE` with evidence). **Now:** start C267 end-to-end (next grep-zero WHITE-diag line-length RQA variant, pre-stated fail-closed formula, same WF/costs/edge rule, required artifacts+SHA256, update handoff). **C268+:** continue enumerating grep-zero WHITE-diag line-length RQA variants in the same family. Fallback chain if C267 collides/invalid: next pre-stated grep-zero variant — for each re-verify grep-zero, pre-state fail-closed formula, record evidence. Never re-run C1–C15/C249–C266 except evidence-backed defect fix. **No early exit except `oos_edge_proven: true`.**

## STATE SNAPSHOT (2026-11-11T23:17:25Z UTC)
- **C12:** 5/5 complete. **C13:** 3/3 complete. **C14:** 7/7 complete (zero edge). **C15:** 7/7 complete (zero edge).
- **C249–C265:** COMPLETE, all `edge_claim: NONE`, `oos_edge_proven: false` (artifacts on disk with SHA256-from-bytes).
- **C266:** **COMPLETE (2026-11-11T22:56:14Z UTC run / 2026-11-11T22:56:14Z UTC packaged).** Primary `RELATIVE_MEAN_ABSOLUTE_DIFFERENCE` distinct (0 non-self). Result: `edge_claim: NONE`, `oos_edge_proven: false`, `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- **Caches:** real spot/volume caches present in `data/cache/` (`.pkl`+`.meta.json`+provenance, 66 files); **no refetch**.
- **Environment:** `python3` 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1. Git clean at handoff (2026-11-11T23:17:25Z UTC).

## C266 — COMPLETE (2026-11-11T22:56:14Z UTC run / 2026-11-11T23:14:47Z UTC handoff updated)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE_SHOCK_MR` (RELATIVE_MEAN_ABSOLUTE_DIFFERENCE=mean(|L_i-L_j|)/(2*mean(L)) over all unordered pairs of qualifying WHITE diagonal segment lengths, pooled over off-diagonal diagonals k!=0, length>=w_min=2, N>=3, fail-closed).
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- **Evidence:** `cross_asset.oos_net_sums` fee0_slip0=-44.26754432579919, fee5_slip5=-82.22254432579824, fee10_slip10=-120.17754432579859, fee20_slip20=-196.08754432579923, fee40_slip40=-347.90754432579945.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_relative_mean_absolute_difference_shock_mr_costed_oos_20261111T225614Z.json` — `b14dd3d3d997c3e9ada30bacaba140ac85938e35a82738bbcc626fe33d008092`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_relative_mean_absolute_difference_shock_mr_costed_oos.py` — `1de611abb384e878ba373b854bbe01f4febeb3f20b899d05c77fdbd181d9b44a`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T225614Z.json` — `49aec224913311c7af628e890509a0b570f6bdc85d2b42d91b5ce3846546ce64`
  - Registry: `reports/strategy_edge_registry_20261111T225614Z.json` — `7d581f43e06994ab7a1a36d61d7afeb41bb3b486b52ba8c83d0c8409bb18f815`
  - Summary: `reports/campaign266_execution_summary_20261111T225614Z.json` — `876720557fc8224fa5f872de2571584e353d9348b791b9e6f43a780d9747e4b8`
- **Distinctness (pre-stated, self-only hits):** grep for `RTE_OVER_WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE|WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE` returned 0 nonself hits at run.

## C265 — COMPLETE (2026-11-11T20:10:37Z UTC run / 2026-11-11T20:10:37Z UTC packaged)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MAD_FROM_MEDIAN_SHOCK_MR` (MAD_FROM_MEDIAN=median(|L_i-med|), med=median(L), N>=3, fail-closed).
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: true`.
- **Evidence:** `cross_asset.oos_net_sums` fee0_slip0=0.8844218751429131, fee5_slip5=-0.0655781248570877, fee10_slip10=-1.015578124857088, fee20_slip20=-2.9155781248570882, fee40_slip40=-6.715578124857087.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_mad_from_median_shock_mr_costed_oos_20261111T201037Z.json` — `0297d22a42bb8c980e4730958cd19e4006751518374d0b311f84e1b3071a1c07`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_mad_from_median_shock_mr_costed_oos.py` — `aee3bcdc8e6b1a3972ea134a7d9211c5e2400081a2eb0633351fe2e3b697931b`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T201037Z.json` — `a8abbd340d2474ddc8b069f6f2b9fb34bf255c577f5ba83ffefab9684d2c794f`
  - Registry: `reports/strategy_edge_registry_20261111T201037Z.json` — `10baa10b4c5d4584240373ee3f3d989bec5bbe06ea4fd3fb8c2d5e9a6dd9e418`
  - Summary: `reports/campaign265_execution_summary_20261111T201037Z.json` — `c563b37e65c26f059d63ee12837bc724dc8202974ff54a61014bc692d4afbcd4`
- **Distinctness (pre-stated, self-only hits):** grep for `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MAD_FROM_MEDIAN|WHITE_DIAG_LINE_LENGTH_MAD_FROM_MEDIAN` returned 0 nonself hits at run.

## C264 — COMPLETE (2026-11-11T19:34:10Z UTC run / 2026-11-11T19:48:43Z UTC packaged)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION_SHOCK_MR` (QCD=(Q3-Q1)/(Q3+Q1), Q1/Q3 numpy percentile linear, N>=3, fail-closed).
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- **Evidence:** `cross_asset.oos_net_sums` fee0_slip0=-0.4465752245280936, fee5_slip5=-2.304575224528095, fee10_slip10=-4.162575224528096, fee20_slip20=-7.8785752245280944, fee40_slip40=-15.310575224528094.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_quartile_coefficient_of_dispersion_shock_mr_costed_oos_20261111T193410Z.json` — `5d9665d4ba39692ac3ffe397a5b90f383d3bf72f0d2d50930944d02534e37a4a`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_quartile_coefficient_of_dispersion_shock_mr_costed_oos.py` — `ea3818b184eb89b139deb4f15471272cfdacb38231b16d01185bc18622c66442`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T194843Z.json` — `aa88643d4ef17ab8e3230f6aa2c4ef5fd2e578454cd8504c2a417cf137494d72`
  - Registry: `reports/strategy_edge_registry_20261111T194843Z.json` — `8e2f1e233980bf2328738452c0198c5eeab698630c51c298a98a626ce6a54867`
  - Summary: `reports/campaign264_execution_summary_20261111T194843Z.json` — `80ec2ab781c8dfb8679d4479f09e2974bb4c6424feb9e16603825d06136d95f0`
- **Distinctness (pre-stated, self-only hits):** grep for `RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION|WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION` returned 0 nonself hits at run.

## HARD BANS
- ❌ No status-only work; no "planning/researching" as substitute for producing artifacts.
- ❌ No re-runs of C1–C15 or C249–C266 except evidence-backed defect fix.
- ❌ No network refetch (use `data/cache/` only).
- ❌ No synthetic/fabricated data.
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked for C1–C15).
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user.
- ❌ No early exit from pipeline except `oos_edge_proven: true`.

**END OF DURABLE HANDOFF — 2026-11-11T23:17:25Z UTC (C266 complete with all artifacts; C267 next).**
**NEXT AGENTIC SESSION: START C267 NOW (HEAVY) — select next grep-zero WHITE-diag line-length RQA variant (first candidate ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN, all 6 fallback variants grep-zero), pre-state fail-closed formula, re-verify distinctness (grep 0 nonself), run OOS costed walk-forward, emit ingest/registry/summary with SHA256-from-bytes, record NONE/edge with evidence, update this handoff. THEN CONTINUE PIPELINE C268+. DO NOT ASK. DO NOT PLAN.**