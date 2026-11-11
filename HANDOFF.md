# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` (crypto quant stat-arb strategies).
> **Core mission (non-negotiable):** real-data-only edge search with fail-closed enriched cointegration/gates. **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked`/`NONE` with evidence is valid. **Status-only work is forbidden.**
> **Single durable handoff:** `HANDOFF.md` (repo root) only. Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line is stale (`latest_campaign_done: C248`, `next_campaign: C249`; C249–C265 complete on disk). Must not be edited to block/replace C1–C15/C249+ progress. Sync only if explicitly requested by user.

## PRIORITIZED TIMESTAMPED INITIAL TASK MESSAGE (2026-11-11T20:45:00Z UTC — C266 runner in progress; next session must complete C266 packaging + start C267) — START HERE, DO NOT DEVIATE

**PRIORITY 1 (HEAVY EXECUTION — MANDATORY):** Continue the proven main line: **real cached quote/volume RQA shock mean-reversion costed-OOS**, real-data-only, fail-closed gates. Do **not** pivot to research, docs, refactors, or status summaries. Produce artifacts or honest `NONE` with evidence.

**IMMEDIATE NON-DEFERRABLE ACTION:** Complete **Campaign #266** end-to-end now (runner launched this session; C265 complete, `edge_claim: NONE`). No planning phase. No "explore first" substitution.

### Preflight (re-verified 2026-11-11T20:45:00Z UTC — path clear, no blocking bottlenecks)
```bash
python3 -c "import numpy,pandas,scipy; print('ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE|WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE|relative_mean_absolute_difference' scripts/ strategies/ backtest/ utils/ 2>&1 | wc -l  # C266 primary self-only expected (13); must be 0 non-self
ls data/cache/*.pkl data/cache/*.meta.json | wc -l  # expect 66
git -C /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats status --short | head
```
- **Verified this session:** deps OK (`python3` 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1); C266 primary token present only in self script `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_relative_mean_absolute_difference_shock_mr_costed_oos.py` (13 self hits, **0 non-self**); real caches present (**66** `.pkl`/`.meta.json` in `data/cache/`); git clean. No blocking bottlenecks observed. C265 artifacts complete on disk.
- **C266 run status (2026-11-11T20:45:00Z UTC):** OOS runner script exists and was launched this session (`python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_relative_mean_absolute_difference_shock_mr_costed_oos.py`). It is compute-heavy and produced no stdout before observation windows ended; **no `reports/*relative_mean_absolute_difference*` OOS artifact observed yet at handoff write time**. Next agent must first check for a newly emitted C266 OOS report; if absent, (re)run the script to completion (foreground or monitored) and then package required artifacts. Do not treat missing artifact as edge/no-edge without a completed, evidenced run.
- If deps missing → fix environment or fail closed with concrete evidence (no status-only downgrade).
- If caches/provenance missing → fail closed with evidence, **no network refetch**.
- If a background process blocks disk/CPU → stop it.

### C266 SPEC (pre-stated, fail-closed)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE_SHOCK_MR` (fallback primary per C264/C265 chain: `RELATIVE_MEAN_ABSOLUTE_DIFFERENCE`, grep-zero re-verified before selection).
- **Feature:** relative mean absolute difference of qualifying WHITE diagonal segment lengths (pooled over off-diagonal diagonals k!=0, length>=w_min=2, N>=3): `R_MAD = mean(|L_i - L_j|) / (2 * mean(L))` over all unordered pairs (numpy, pre-stated fixed). Fail-closed if <3 segments, mean(L)<=0/non-finite, R_MAD non-finite/degenerate. Distinct from C265 MAD_FROM_MEDIAN (median-centered) and C254 MEAN_ABSOLUTE_DEVIATION (mean-centered single dispersion).
- **Fail-closed:** if `<3` segments; `med`/`mean` undefined/non-finite; feature<=0, degenerate, or non-finite; or any intermediate undefined/non-finite.
- **WF/costs:** `train=720, test=168, step=168`; cost grid bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.
- **Edge rule:** `oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only.
- **Required artifacts (SHA256 from bytes):** OOS report, runner script, ingest attempt, strategy edge registry, campaign execution summary under `reports/`/`scripts/` with campaign timestamping. Update this handoff with results/evidence/hashes and next campaign.
- **Distinctness gate:** grep 0 nonself for the exact `RELATIVE_MEAN_ABSOLUTE_DIFFERENCE` / `relative_mean_absolute_difference` / `WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE` token family before run; if non-distinct, fail-closed switch to next pre-stated grep-zero variant and record evidence.

### UNINTERRUPTED PIPELINE (so future agents cannot avoid heavy work)
C264 complete (`NONE` with evidence). C265 complete (`NONE` with evidence). **Now:** finish C266 end-to-end (primary `RELATIVE_MEAN_ABSOLUTE_DIFFERENCE`, self-only distinct; runner launched 2026-11-11T20:45:00Z UTC) — wait for/produce OOS JSON, then emit ingest attempt, strategy edge registry, campaign execution summary with SHA256-from-bytes, record result/evidence, update this handoff.
**C267+:** only after C266 fully packaged, continue enumerating grep-zero WHITE-diag line-length RQA variants in the same family. Fallback chain if C266 collides/invalid: next pre-stated grep-zero variant (e.g. `ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN`, `STANDARDIZED_MOMENT` family, `PEARSON_MODE_SKEW`, `MEDIAN_ABSOLUTE_DEVIATION_FROM_MEAN`, `INTERQUARTILE_MEAN`, `BIWEIGHT_MIDVARIANCE`, or other not-yet-run dispersion/shape forms) — for each re-verify grep-zero, pre-state fail-closed formula, record evidence. For each: distinctness gate 0 nonself, fail-closed formula pre-stated, same WF/costs/edge rule, required artifacts+SHA256, update handoff. Never re-run C1–C15/C249–C265 except evidence-backed defect fix. **No early exit except `oos_edge_proven: true`.**

## STATE SNAPSHOT (2026-11-11T20:45:00Z UTC)
- **C12:** 5/5 complete. **C13:** 3/3 complete. **C14:** 7/7 complete (zero edge). **C15:** 7/7 complete (zero edge).
- **C249–C265:** COMPLETE, all `edge_claim: NONE`, `oos_edge_proven: false` (artifacts on disk with SHA256-from-bytes).
- **C266:** **IN PROGRESS (runner launched this session, compute-heavy).** Primary `RELATIVE_MEAN_ABSOLUTE_DIFFERENCE` distinct (0 non-self). Runner: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_relative_mean_absolute_difference_shock_mr_costed_oos.py`. OOS/ingest/registry/summary artifacts and SHA256/handoff finalization **pending completion** — no C266 `reports/*relative_mean_absolute_difference*` artifact present at handoff write time.
- **Caches:** real spot/volume caches present in `data/cache/` (`.pkl`+`.meta.json`+provenance, 66 files); **no refetch**.
- **Environment:** `python3` 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1. Git clean at handoff.

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
- ❌ No re-runs of C1–C15 or C249–C265 except evidence-backed defect fix.
- ❌ No network refetch (use `data/cache/` only).
- ❌ No synthetic/fabricated data.
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked for C1–C15).
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user.
- ❌ No early exit from pipeline except `oos_edge_proven: true`.

**END OF DURABLE HANDOFF — 2026-11-11T20:45:00Z UTC (C266 runner launched/in progress, OOS artifact not yet observed; preflight clear, no bottlenecks removed).**
**NEXT AGENTIC SESSION: COMPLETE C266 NOW (HEAVY) — obtain C266 OOS artifact (wait or rerun to completion), emit ingest/registry/summary with SHA256-from-bytes, record NONE/edge with evidence, update this handoff. THEN CONTINUE PIPELINE C267+. DO NOT ASK. DO NOT PLAN.**
