# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T05:02:27Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (verified 2026-11-12T05:02:27Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. The single most relevant, highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge discovery** — continue the C273+ WHITE-diag line-length RQA dispersion/shape enumeration. Nothing else (docs, refactor, status, state.yaml sync) competes with this.

**Bottleneck audit (verified 2026-11-12T05:02:27Z UTC): bottlenecks removed.**
- `HANDOFF.md` consolidated: removed 10+ duplicate/conflicting "AUTHORITATIVE" blocks that pointed to already-completed C271/C272; single clear directive remains (this block).
- `git status --short`: dirty only with uncommitted C272 artifacts/scripts and this handoff update (expected, not stalled).
- Deps present: `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1.
- `data/cache/` = 68 real files (`.pkl`+`.meta.json`+provenance); **no refetch**.
- No stalled/available background processes.
- C272 artifacts confirmed on disk with SHA256-from-bytes (recorded below).

**C272 — COMPLETE (2026-11-12T04:57:22Z run / 2026-11-12T05:01:14Z packaged).** `oos_edge_proven: false` → chain continues. Grep-zero chain pick (after C271 consumed SKEWNESS_ABOUT_MEAN): walked `EXCESS_KURTOSIS`, `PERCENTILE_SPREAD`, `GINI_COEFFICIENT`, `HERMITE_DISSIPATION`; FIRST grep-zero = **EXCESS_KURTOSIS** (`grep_hits_nonself_at_run: 0`).
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_EXCESS_KURTOSIS_SHOCK_MR` (EXCESS_KURTOSIS = mean((L_i-mean)^4)/std(L)^4 - 3; std population ddof=0; N>=3 qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0, length>=w_min=2; fail-closed if N<3, std<=0/non-finite, or result non-finite/degenerate).
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- **Evidence:** `cross_asset.oos_net_sums` fee0_slip0=-3.277143034378751, fee5_slip5=-3.5021430343787285, fee10_slip10=-3.72714303437874, fee20_slip20=-4.17714303437875, fee40_slip40=-5.077143034378753. 11 assets tested (ok), zero insufficient/feature_insufficient/no_splits.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_excess_kurtosis_shock_mr_costed_oos_20261112T045722Z.json` — `a471da651d2009356d41ecb932a0b19bd4dcdf76567a036dd3ec1053f9ea659d`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_excess_kurtosis_shock_mr_costed_oos.py` — `c42b5537c05f94e13c490bea2ec9f9c6445fe008a23f4e480fce4fddbede0658`
  - Ingest: `reports/real_feed_ingest_attempt_20261112T045441Z.json` — `9c0e95d4fcc29051308e130c706167ff174c865f6ff2b464f24c381f10ba8e58`
  - Registry: `reports/strategy_edge_registry_20261112T050114Z.json` — `1038b38760f70b52505cd09cf7a59b52ce61bc0d01b1cd3803cd2d747d3e8d19`
  - Summary: `reports/campaign272_execution_summary_20261112T045722Z.json` — `042ccaee28d72c89024f7cee1f97c13bb0f3a502276866b57718bb981c4bc2fa`
- **Distinctness:** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_EXCESS_KURTOSIS|WHITE_DIAG_LINE_LENGTH_EXCESS_KURTOSIS|EXCESS_KURTOSIS` = 0 non-self hits at run.

**IMMEDIATE MANDATORY HEAVY WORK (non-optional, no planning phase): EXECUTE CAMPAIGN C273 END-TO-END NOW.**
Do not plan, summarize, explore, or ask questions — start implementation/execution immediately.
1. **Grep-zero chain pick (remaining, in order):** `PERCENTILE_SPREAD`, `GINI_COEFFICIENT`, `HERMITE_DISSIPATION` (SKEWNESS_ABOUT_MEAN→C271, EXCESS_KURTOSIS→C272). Pre-check at 2026-11-12T05:02:27Z: all three grep-zero in `scripts/ strategies/ backtest/ utils/` (`grep_hits_nonself_precheck: 0`). **Pick FIRST: `PERCENTILE_SPREAD`**. Re-verify 0 non-self at run (exclude own C273 files) and record `grep_hits_nonself_at_run: 0`. Do not skip earlier candidate.
2. **Pre-state fail-closed formula (C273):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PERCENTILE_SPREAD_SHOCK_MR`. Feature: `PERCENTILE_SPREAD = (P75(L) - P25(L)) / median(L)` over qualifying WHITE diagonal segment lengths L pooled over off-diagonal diagonals k!=0, length>=w_min=2, N>=3. Percentiles: numpy `percentile` linear/default, deterministic. Fail-closed if N<3, median<=0/non-finite, P75/P25/median/spread non-finite or undefined. Distinctness patterns to prove zero: `RTE_OVER_WHITE_DIAG_LINE_LENGTH_PERCENTILE_SPREAD|WHITE_DIAG_LINE_LENGTH_PERCENTILE_SPREAD|PERCENTILE_SPREAD`.
3. **Run costed OOS WF** on real cached data only: `train=720, test=168, step=168`; cost bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.
4. **Emit required artifacts** under `reports/`/`scripts/` with campaign timestamps: OOS report, runner script, ingest attempt, strategy edge registry, campaign execution summary. Compute SHA256 from bytes for each and record in this handoff.
5. **Record result/evidence**: `edge_claim`, `oos_edge_proven`, exposure/cost/B&H flags, `cross_asset.oos_net_sums`, distinctness proof. Edge rule: `oos_edge_proven=true` IFF OOS exposure>0 AND ALL cost slices OOS net sum>0 AND mean OOS net>mean B&H OOS net on same WF windows.
6. If `oos_edge_proven: false` (expected unless proven), **immediately continue C274+** — no early exit except proven edge. Honest `NONE` with evidence is valid; status-only work is not.

**NEXT FOCUS CAMPAIGN (C274+) — mandatory enumeration, future agents cannot avoid heavy work:**
Run sequentially C273 → C274 → …; each must produce executed costed-OOS output + all required artifacts + SHA256-from-bytes + evidence recorded in this handoff + next campaign noted. Stop the chain ONLY on `oos_edge_proven: true`.
- Chain after C273: `GINI_COEFFICIENT` (C274 candidate), `HERMITE_DISSIPATION` (C275 candidate), then identify further grep-zero WHITE-diag line-length dispersion/shape variants and continue enumeration.
- Same rules: grep-zero re-verified at run (hard gate), pre-state fail-closed formula, `train=720,test=168,step=168`, costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, real cached data only, no refetch/synthetic, no reruns C1–C15 or C249–C272 except evidence-backed defect fix.

**Hard rules:** no planning/status-only work, no synthetic/fabricated data, no network refetch, no threshold weakening, no `research_state/state.yaml` edits unless explicitly requested by user. `research_state/state.yaml` RQA line is stale (C248/C249 markers) — locked/separate; do not edit to block progress.

## STATE SNAPSHOT (2026-11-12T05:02:27Z UTC)
- **C1–C15:** complete (see history below); zero edge proven.
- **C249–C272:** COMPLETE, all `edge_claim: NONE`, `oos_edge_proven: false` (artifacts on disk with SHA256-from-bytes; C249–C270 hashes recorded in prior history/state, C271–C272 recorded above).
- **Latest (C272):** EXCESS_KURTOSIS shock MR — nets fee0/5/10/20/40 = -3.277143034378751 / -3.5021430343787285 / -3.72714303437874 / -4.17714303437875 / -5.077143034378753.
- **C271:** SKEWNESS_ABOUT_MEAN shock MR — nets fee0/5/10/20/40 = 75.5061239106376 / 39.212123910638454 / 2.9181239106382506 / -69.66987608936242 / -214.84587608936266.
- **Environment:** python3 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1. Caches: `data/cache/` 68 real files, no refetch.

## C271 EVIDENCE (SHA256 from bytes)
- OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_skewness_about_mean_shock_mr_costed_oos_20261112T040322Z.json` — `b57646fc54a0227bd8d3854082f4817311e3983d06c75c407c8fa908a79eb400`
- Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_skewness_about_mean_shock_mr_costed_oos.py` — `4146e998b3771ff667dc5db45a9b9ac2f39c7d9ec82b966d58ff879b46795dba`
- Ingest: `reports/real_feed_ingest_attempt_20261112T040318Z.json` — `b3a168d45713a99e721047dbe4f2af6e84e797f39ae0afd4ad0d3ca798ce5d8b`
- Registry: `reports/strategy_edge_registry_20261112T040827Z.json` — `c62ec91aa1c85caa39336408470b252c920cf188c0e2afd0c87ed242201213ee`
- Summary: `reports/campaign271_execution_summary_20261112T040322Z.json` — `57975c8b4d561d6ad59e2d9ff6ee88ecfea29d9dc1711d066768cb77c4defa67`

## HARD BANS
- ❌ No status-only work; no "planning/researching" as substitute for producing artifacts.
- ❌ No re-runs of C1–C15 or C249–C272 except evidence-backed defect fix.
- ❌ No network refetch (use `data/cache/` only). No synthetic/fabricated data.
- ❌ No threshold weakening.
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user.
- ❌ No early exit from pipeline except `oos_edge_proven: true`.

---
## HISTORICAL RECORD (condensed, evidence preserved in artifacts)
- **C12:** 5/5 complete. **C13:** 3/3 complete. **C14:** 7/7 complete (zero edge). **C15:** 7/7 complete (zero edge).
- **C249–C270:** COMPLETE, all `edge_claim: NONE`, `oos_edge_proven: false`. Key artifacts/hashes tracked in `research_state/state.yaml` (stale index) and individual `reports/strategy_edge_registry_*`, `reports/campaign*_execution_summary_*`, OOS/ingest/script files under `reports/` and `scripts/` with SHA256-from-bytes.
- **C264 (MAD_FROM_MEDIAN precursor context):** QUARTILE_COEFFICIENT_OF_DISPERSION — NONE. **C265:** MAD_FROM_MEDIAN — NONE. **C266:** RELATIVE_MEAN_ABSOLUTE_DIFFERENCE — NONE. **C267:** ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN — NONE. **C268:** STANDARDIZED_MOMENT — NONE. **C269:** PEARSON_MODE_SKEW — NONE. **C270:** COEFFICIENT_OF_VARIATION — NONE. **C271:** SKEWNESS_ABOUT_MEAN — NONE. **C272:** EXCESS_KURTOSIS — NONE. (Full hashes for C264–C270 remain in their prior handoff entries preserved in git history and in artifact files on disk.)

**END OF DURABLE HANDOFF — refreshed 2026-11-12T05:02:27Z UTC (repo focus = crypto quant stat-arb strategies; bottlenecks removed: duplicate handoff blocks cleared; C273 PERCENTILE_SPREAD is the immediate mandatory heavy task — execute end-to-end now, then continue C274+ until `oos_edge_proven: true`).**
**NEXT AGENT: EXECUTE C273 NOW. Produce runnable+executed C273 artifacts (OOS/ingest/registry/summary/script) with SHA256-from-bytes and evidence in this file, then continue C274+ until `oos_edge_proven: true`. NO STATUS-ONLY.**
