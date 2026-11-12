# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` (crypto quant stat-arb strategies).
> **Core mission (non-negotiable):** real-data-only edge search with fail-closed enriched cointegration/gates. **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked`/`NONE` with evidence is valid. **Status-only work is forbidden.**
> **Single durable handoff:** `HANDOFF.md` (repo root) only. Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line is stale (`latest_campaign_done: C248`, `next_campaign: C249`; C249–C267 complete on disk). Must not be edited to block/replace progress. Sync only if explicitly requested by user.

## PRIORITIZED TIMESTAMPED INITIAL TASK MESSAGE (2026-11-12T01:25:51Z UTC — C268 complete; START C269 NOW) — DO NOT DEVIATE

**Repo focus (priority driver):** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. Next agent must pursue **real-data-only, fail-closed, costed OOS stat-arb edge discovery** (heavy execution), not status/docs/refactors.

**Bottleneck check (verified 2026-11-12T01:25:51Z UTC):** none blocking.
- Deps OK: `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1
- Real caches present: `68` files in `data/cache/` (**no refetch**); git working tree clean at check time; no stalled background processes observed
- C268 artifacts/SHA256 present and recorded below
- `research_state/state.yaml` remains locked/stale per mandate (C249 next in file; do not edit unless explicitly requested)

**PRIORITY 1 (HEAVY EXECUTION — MANDATORY, NOW): Run Campaign #269 end-to-end.** No planning/exploration phase. No status-only work.

### C269 SPEC (pre-stated, fail-closed)
- **Strategy (first choice, grep-zero):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_MODE_SKEW_SHOCK_MR`
  - **Distinctness (re-verify before run, must be 0 non-self):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_MODE_SKEW|WHITE_DIAG_LINE_LENGTH_PEARSON_MODE_SKEW|PEARSON_MODE_SKEW' scripts/ strategies/ backtest/ utils/`
  - **Pre-stated formula (fail-closed, fixed):** on qualifying WHITE diagonal segment lengths `L` pooled over off-diagonal diagonals `k!=0` (consecutive 0-cells/non-recurrent runs, `length >= w_min=2`), require `N>=3`. Compute `mean = mean(L)`, `mode` as the most frequent value in `L` with a deterministic tie-break (if tie, use smallest length value so result is reproducible); compute `std = population_std(L)` (or sample std — **pick one and record explicitly in artifacts**, consistent with numpy default you document). Feature = `(mean - mode) / std`. **Fail-closed** if `N<3`, if mode undefined, if `std <= 0` or non-finite, or if feature non-finite/undefined → no exposure for that window/asset per pipeline conventions (record explicitly, no fabrication). Distinct from all prior C125–C268 families (incl. C268 `STANDARDIZED_MOMENT`, C267 `ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN`, C266 `RELATIVE_MEAN_ABSOLUTE_DIFFERENCE`, C265 `MAD_FROM_MEDIAN`, C264 `QCD`, etc.).
- **Fallbacks if collision/invalid after recheck (pick FIRST grep-zero in chain; re-verify and record evidence):** `MEDIAN_ABSOLUTE_DEVIATION_FROM_MEAN` → `INTERQUARTILE_MEAN` → `BIWEIGHT_MIDVARIANCE` (pre-state a fixed, fail-closed formula for whichever is chosen).
- **WF/costs:** `train=720, test=168, step=168`; cost grid bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.
- **Edge rule:** `oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only.
- **Required artifacts (SHA256 from bytes):** costed OOS report, runner script, ingest attempt, strategy edge registry, campaign execution summary under `reports/`/`scripts/` with campaign timestamping. Update this handoff with results/evidence/hashes and next campaign.
- **Execution discipline:** do not stop at planning; produce runnable artifacts + executed OOS outputs + hashes in this campaign. No early exit except `oos_edge_proven: true`. If environment/runtime blocks, emit fail-closed evidence artifacts and document exact blocker (do not claim progress without evidence).

### UNINTERRUPTED PIPELINE (future agents must not avoid heavy work)
C264–C268 complete (`NONE` with evidence). **Now:** complete C269 end-to-end (next grep-zero WHITE-diag line-length RQA variant, pre-stated fail-closed formula, same WF/costs/edge rule, required artifacts+SHA256, record evidence, update handoff). **C270+:** continue enumerating grep-zero WHITE-diag line-length RQA dispersion/shape variants in same family. For each: re-verify grep-zero, pre-state fail-closed formula, run, package artifacts+SHA256, record evidence, update handoff. Never re-run C1–C15 or C249–C268 except evidence-backed defect fix. **No early exit except `oos_edge_proven: true`.**

## STATE SNAPSHOT (2026-11-12T00:11:40Z UTC)
- **C12:** 5/5 complete. **C13:** 3/3 complete. **C14:** 7/7 complete (zero edge). **C15:** 7/7 complete (zero edge).
- **C249–C265:** COMPLETE, all `edge_claim: NONE`, `oos_edge_proven: false` (artifacts on disk with SHA256-from-bytes).
- **C266:** **COMPLETE** — `RELATIVE_MEAN_ABSOLUTE_DIFFERENCE` (0 non-self). `edge_claim: NONE`, `oos_edge_proven: false`, `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- **C267:** **COMPLETE** — `ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN` (0 non-self). `edge_claim: NONE`, `oos_edge_proven: false`, `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- **C268:** **COMPLETE** — `STANDARDIZED_MOMENT` = mean((L_i-med)^3)/mean(|L_i-med|)^3 about the median, N>=3, fail-closed (0 non-self). `edge_claim: NONE`, `oos_edge_proven: false`, `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- **Caches:** real spot/volume caches present in `data/cache/` (`.pkl`+`.meta.json`+provenance, 66 files); **no refetch**.
- **Environment:** `python3` 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1.

## C267 — COMPLETE (2026-11-12T00:00:46Z UTC run / 2026-11-12T00:06:33Z UTC packaged)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN_SHOCK_MR` (ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN=`sqrt(mean((L_i-med)^2))`, `med=median(L)`, `N>=3`, fail-closed).
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- **Evidence:** `cross_asset.oos_net_sums` fee0_slip0=32.17419158920375, fee5_slip5=-2.6758084107954136, fee10_slip10=-37.525808410795655, fee20_slip20=-107.22580841079625, fee40_slip40=-246.62580841079648.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_root_mean_square_deviation_from_median_shock_mr_costed_oos_20261112T000046Z.json` — `062692ba2eaba2fba51ffc368b45a6a4d174106617fc895bdc83cb14191ab589`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_root_mean_square_deviation_from_median_shock_mr_costed_oos.py` — `4a870e5c6fc8dcfe58dab966a79e8bdde22af598ab852ee29b19d537e35a1bfc`
  - Ingest: `reports/real_feed_ingest_attempt_20261112T000633Z.json` — `59c19e51c99b97c6bd75f0dd2b15d11faaf5a55f90f858029bbf1a592aa08445`
  - Registry: `reports/strategy_edge_registry_20261112T000608Z.json` — `208157e15a84897f4e3f3d4dea9109de85fd0b2dec72b6cfc34e425eab7c7338`
  - Summary: `reports/campaign267_execution_summary_20261112T000046Z.json` — `65ed1d0c7249faccfae02a17871e98387949e716fc329be93f47ba4e8505a5d9`
- **Distinctness:** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN|WHITE_DIAG_LINE_LENGTH_ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN` = 0 non-self hits at run.

## C268 — COMPLETE (2026-11-12T01:06:35Z UTC run / 2026-11-12T01:14:00Z UTC packaged)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_STANDARDIZED_MOMENT_SHOCK_MR` (STANDARDIZED_MOMENT = mean((L_i - med)^3) / mean(|L_i - med|)^3, med = median(L), N>=3, over qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0, length>=w_min=2; fail-closed).
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- **Evidence:** `cross_asset.oos_net_sums` fee0_slip0=-31.450501547906214, fee5_slip5=-68.46150154790529, fee10_slip10=-105.47250154790555, fee20_slip20=-179.49450154790617, fee40_slip40=-327.53850154790644.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_standardized_moment_shock_mr_costed_oos_20261112T010635Z.json` — `2d79ea9e7a770689e820e6f15fb390cfe74426e991d42f1759cfd20c5db51360`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_standardized_moment_shock_mr_costed_oos.py` — `b9c1b88de660e31b910514f9f2736b03826891b7d1fef36551b527a749e725d7`
  - Ingest: `reports/real_feed_ingest_attempt_20261112T005857Z.json` — `d6106b2b2b92b688a3117b5ed89c77dcde4e8d73f90cc3f6180cba4d4980dd00`
  - Registry: `reports/strategy_edge_registry_20261112T011400Z.json` — `ac2bb2d1310ea5469be2c6603aba985305ec5d9d7577c13f497649c00dd996c6`
  - Summary: `reports/campaign268_execution_summary_20261112T010635Z.json` — `d8470cf7a9355ad97d499c9d6afbdcdc09b38ef7a70ab554197817bce143f38a`
- **Distinctness:** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_STANDARDIZED_MOMENT|rte_over_white_diag_line_length_standardized_moment|WHITE_DIAG_LINE_LENGTH_STANDARDIZED_MOMENT|white_diag_line_length_standardized_moment` = 0 non-self hits at run.

## C266 — COMPLETE (2026-11-11T22:56:14Z UTC run / 2026-11-11T23:14:47Z UTC packaged)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE_SHOCK_MR`
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- **Evidence:** `cross_asset.oos_net_sums` fee0_slip0=-44.26754432579919, fee5_slip5=-82.22254432579824, fee10_slip10=-120.17754432579859, fee20_slip20=-196.08754432579923, fee40_slip40=-347.90754432579945.
- **Artifacts (SHA256 from bytes):** OOS `b14dd3d3d997c3e9ada30bacaba140ac85938e35a82738bbcc626fe33d008092`, Script `1de611abb384e878ba373b854bbe01f4febeb3f20b899d05c77fdbd181d9b44a`, Ingest `49aec224913311c7af628e890509a0b570f6bdc85d2b42d91b5ce3846546ce64`, Registry `7d581f43e06994ab7a1a36d61d7afeb41bb3b486b52ba8c83d0c8409bb18f815`, Summary `876720557fc8224fa5f872de2571584e353d9348b791b9e6f43a780d9747e4b8`.

## C265 — COMPLETE (2026-11-11T20:10:37Z UTC)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MAD_FROM_MEDIAN_SHOCK_MR` — `edge_claim: NONE`, `oos_edge_proven: false`.
- **Evidence:** net sums fee0_slip0=0.8844218751429131, fee5_slip5=-0.0655781248570877, fee10_slip10=-1.015578124857088, fee20_slip20=-2.9155781248570882, fee40_slip40=-6.715578124857087.
- **Artifacts (SHA256):** OOS `0297d22a42bb8c980e4730958cd19e4006751518374d0b311f84e1b3071a1c07`, Script `aee3bcdc8e6b1a3972ea134a7d9211c5e2400081a2eb0633351fe2e3b697931b`, Ingest `a8abbd340d2474ddc8b069f6f2b9fb34bf255c577f5ba83ffefab9684d2c794f`, Registry `10baa10b4c5d4584240373ee3f3d989bec5bbe06ea4fd3fb8c2d5e9a6dd9e418`, Summary `c563b37e65c26f059d63ee12837bc724dc8202974ff54a61014bc692d4afbcd4`.

## C264 — COMPLETE (2026-11-11T19:34:10Z UTC run / 2026-11-11T19:48:43Z UTC packaged)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION_SHOCK_MR` — `edge_claim: NONE`, `oos_edge_proven: false`.
- **Evidence:** net sums fee0_slip0=-0.4465752245280936, fee5_slip5=-2.304575224528095, fee10_slip10=-4.162575224528096, fee20_slip20=-7.8785752245280944, fee40_slip40=-15.310575224528094.
- **Artifacts (SHA256):** OOS `5d9665d4ba39692ac3ffe397a5b90f383d3bf72f0d2d50930944d02534e37a4a`, Script `ea3818b184eb89b139deb4f15471272cfdacb38231b16d01185bc18622c66442`, Ingest `aa88643d4ef17ab8e3230f6aa2c4ef5fd2e578454cd8504c2a417cf137494d72`, Registry `8e2f1e233980bf2328738452c0198c5eeab698630c51c298a98a626ce6a54867`, Summary `80ec2ab781c8dfb8679d4479f09e2974bb4c6424feb9e16603825d06136d95f0`.

## HARD BANS
- ❌ No status-only work; no "planning/researching" as substitute for producing artifacts.
- ❌ No re-runs of C1–C15 or C249–C268 except evidence-backed defect fix.
- ❌ No network refetch (use `data/cache/` only). No synthetic/fabricated data.
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked for C1–C15).
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user.
- ❌ No early exit from pipeline except `oos_edge_proven: true`.

**END OF DURABLE HANDOFF — 2026-11-12T01:24:15Z UTC (C268 complete, no blockers; C269 mandated next).**
**NEXT AGENT: START C269 NOW (HEAVY). Use `PEARSON_MODE_SKEW` (grep-zero re-verified now) or next fallback if collision, pre-state fail-closed formula, run costed OOS WF, emit all required artifacts + SHA256-from-bytes, record NONE/edge with evidence, update this handoff, continue C270+. NO STATUS-ONLY.**
