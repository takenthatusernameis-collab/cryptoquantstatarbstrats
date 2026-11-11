# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` = crypto quant stat-arb strategies. Core mission: real-data-only edge search (fail-closed enriched cointegration gates), no fabrication, no status-only work. **Single durable handoff at repo root: `HANDOFF.md` only** (verified/updated 2026-11-11T13:13:44Z UTC, this session; C254 complete, C255 is the next non-deferrable run). Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked`/`NONE` with evidence is valid. **Status-only work is forbidden.**
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line (stale at `latest_campaign_done: C248` / `next_campaign: C249`; C249–C253 complete on disk). Separate research line; must not be edited to block/replace C1–C15 progress. Sync `state.yaml` only if explicitly requested by the user.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-11T13:13:44Z UTC)

**DO THIS FIRST (heavy execution, no status-only, no planning substitute): Campaign #255 — real-data-only fail-closed volume RQA shock mean-reversion costed-OOS edge search, next grep-zero distinct fallback. Primary preselected: `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABSOLUTE_DEVIATION` (median absolute deviation = median(|x_i - median(x)|) of qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0; pre-state exact formula, fail-closed if <3 qualifying segments or median/MAD undefined/non-finite or MAD <= 0/degenerate or ratio undefined). Fallback if blocked: `RTE_OVER_WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE` (semi-variance of qualifying segment lengths; fail-closed on undefined/degenerate/insufficient). Both grep-zero pre-checked 2026-11-11T13:04:10Z UTC (see BOTTLENECK REMOVAL). Verify distinctness before implementation/run. Use `python3` (3.12.3); deps `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1 available.**

**State (verified 2026-11-11T13:13:44Z UTC; C254 artifacts confirmed on disk):** C12 5/5, C13 3/3, C14 7/7 (zero edge), C15 7/7 (zero edge). C249–C253 COMPLETE (NONE). **C254 COMPLETE** (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEAN_ABSOLUTE_DEVIATION`, `edge_claim: NONE`, `oos_edge_proven: false`) — 5 artifacts + SHA256 from bytes on disk (see C254 section). **C255 NOT STARTED** — zero C255 artifacts in `reports/`/`scripts/`. Caches present in `data/cache/` (`.pkl`+`.meta.json`); no network refetch. **Bottlenecks cleared:** deps OK (no c7-venv blocker); grep-zero pre-check for `MEDIAN_ABSOLUTE_DEVIATION` = 0 and `WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE` = 0 (scripts/strategies/backtest/utils); no blocking background process. Stop only if `oos_edge_proven: true`; otherwise record honest `edge_claim: NONE` with evidence and update this handoff. Do not edit `research_state/state.yaml` unless explicitly requested by user.

**C255 plan (non-deferrable):**
- **Preselected strategy:** `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABSOLUTE_DEVIATION` (median absolute deviation = median(|x_i - median(x)|) of qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0; pre-state exact formula, fail-closed on undefined/degenerate/insufficient segments).
- **Distinctness gate (must re-confirm before implementation/run):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABSOLUTE_DEVIATION|WHITE_DIAG_LINE_LENGTH_MEDIAN_ABSOLUTE_DEVIATION' scripts/ strategies/ backtest/ utils/` → **0 nonself hits required**.
- **If blocked/fails distinctness:** select next grep-zero distinct fallback (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE` / `WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE`, grep-zero pre-checked 2026-11-11T13:04:10Z), record evidence, and proceed (no status-only stop).
- **Implement by adapting C254 pattern:** copy/edit `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_mean_absolute_deviation_shock_mr_costed_oos.py` → C255 script; preserve fail-closed, real-data-only, SHA256-from-bytes, and artifact/registry/summary/ingest emission patterns. Prior registry for C255 = `reports/strategy_edge_registry_20261111T130410Z.json` (sha256 `4b546a84990fa52fb3ada2ddf713b5959aabade58653819fdb94206a45af9a7d`).
- **Required outputs (all SHA256 from bytes):** timestamped costed-OOS artifact, script, ingest attempt, strategy-edge-registry entry, campaign execution summary.
- **Edge rule (honest, fail-closed):** `oos_edge_proven: true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows (real data only). Otherwise `edge_claim: NONE` with evidence: `cross_asset_oos_net_sums`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`.
- **Stop only if `oos_edge_proven: true`.** Otherwise record honest blocked/no-edge conclusion with evidence and update this handoff (paths, SHA256s, conclusion, next directive). No planning/researching as substitute for execution. Do **not** edit `research_state/state.yaml` unless explicitly requested by user.

**EXACT COMMANDS TO RUN FOR C255 (from repo root)**

```bash
# 1. Re-verify grep-zero distinctness for MEDIAN_ABSOLUTE_DEVIATION (MUST return 0 nonself hits)
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABSOLUTE_DEVIATION|WHITE_DIAG_LINE_LENGTH_MEDIAN_ABSOLUTE_DEVIATION' scripts/ strategies/ backtest/ utils/

# 2. Copy C254 pattern script and adapt for MEDIAN_ABSOLUTE_DEVIATION
cp scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_mean_absolute_deviation_shock_mr_costed_oos.py \
   scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_median_absolute_deviation_shock_mr_costed_oos.py

# 3. Edit: replace MEAN_ABSOLUTE_DEVIATION/mean_absolute_deviation with MEDIAN_ABSOLUTE_DEVIATION/median_absolute_deviation;
#    update strategy_id, feature docstring/formula (pre-state exact MAD = median(|x_i - median(x)|) of qualifying
#    WHITE diagonal segment lengths; fail-closed if <3 segments or median/MAD undefined/non-finite or MAD <= 0/degenerate),
#    grep-distinctness strings, artifact/report naming, campaign=255, prior registry ->
#    strategy_edge_registry_20261111T130410Z.json (sha 4b546a84990fa52fb3ada2ddf713b5959aabade58653819fdb94206a45af9a7d).
#    Update own_campaign exclusion set to include C255 helper stems. Reference C254 OOS sha
#    fa6324e99b8ead1dec745f0e27142799ae6b0819d10b6ada7c7df046fcc61cd4.

# 4. Run script (heavy work) and emit ingest/registry/summary artifacts
python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_median_absolute_deviation_shock_mr_costed_oos.py
python3 scripts/run_real_feed_ingest_attempt_255.py
python3 scripts/emit_campaign255_registry.py
python3 scripts/emit_campaign255_summary.py

# 5. Record SHA256-from-bytes for: OOS artifact, script, ingest attempt, registry, summary.

# 6. Update THIS HANDOFF.md with: UTC timestamp, commands run, artifact paths+SHA256, conclusion, next directive.
#    Do NOT edit research_state/state.yaml unless explicitly requested by user.
```

## C254 (MAIN LINE — COMPLETE, 2026-11-11T13:04:10Z UTC)

- Campaign 254, strategy `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEAN_ABSOLUTE_DEVIATION_SHOCK_MR` (mean absolute deviation = mean(|x_i - mean(x)|) of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0; pre-stated exact formula MAD = mean(|x_i - mean(x)|); fail-closed if <3 qualifying segment lengths or mean/MAD undefined/non-finite or MAD <= 0/degenerate or ratio undefined/non-finite), edge_claim **NONE**, oos_edge_proven **false**, all_new_c254_artifact_paths_sha256_from_bytes **true**.
- **Distinctness (pre-run, required):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEAN_ABSOLUTE_DEVIATION|WHITE_DIAG_LINE_LENGTH_MEAN_ABSOLUTE_DEVIATION' scripts/ strategies/ backtest/ utils/` → 0 nonself hits at run (`grep_hits_nonself_at_run: 0`; self + own campaign emit/ingest scripts excluded in-script).
- **Commands run (from repo root):** distinctness grep; created `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_mean_absolute_deviation_shock_mr_costed_oos.py`, `scripts/run_real_feed_ingest_attempt_254.py`, `scripts/emit_campaign254_registry.py`, `scripts/emit_campaign254_summary.py`; `python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_mean_absolute_deviation_shock_mr_costed_oos.py`; `python3 scripts/run_real_feed_ingest_attempt_254.py`; `python3 scripts/emit_campaign254_registry.py`; `python3 scripts/emit_campaign254_summary.py`.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_mean_absolute_deviation_shock_mr_costed_oos_20261111T125847Z.json` — `fa6324e99b8ead1dec745f0e27142799ae6b0819d10b6ada7c7df046fcc61cd4`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_mean_absolute_deviation_shock_mr_costed_oos.py` — `c388cfeccfc666366d4ba5bb27511dcadce28ff5b1cfca7c80d02e783c904e6e`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T130409Z.json` — `6e6acf15e0ba9d062498b940a41b73e36434574eb5d57ad2a1761f3b310ab06e`
  - Registry: `reports/strategy_edge_registry_20261111T130410Z.json` — `4b546a84990fa52fb3ada2ddf713b5959aabade58653819fdb94206a45af9a7d`
  - Summary: `reports/campaign254_execution_summary_20261111T130410Z.json` — `ba41511e37960be99893e129f8a432de28eed7d68e3a5dc9bd6e423008d64be9`
- **Evidence (real data, WF 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]]):**
  - `cross_asset_oos_net_sums`: fee0_slip0=-2.8516343128245802, fee5_slip5=-3.5576343128245806, fee10_slip10=-4.263634312824581, fee20_slip20=-5.675634312824582, fee40_slip40=-8.49963431282458
  - `any_exposure_oos: true`
  - `all_cost_slices_positive_oos_net_sum: false`
  - `all_cost_slices_beat_bh_mean_rule: false`
  - **Conclusion:** `oos_edge_proven: false`, `edge_claim: NONE`. No edge found (fails all-cost-slices-positive and BH-beat rules); honest no-edge recorded.

## C253 (MAIN LINE — COMPLETE, 2026-11-11T12:48:32Z UTC)

- Campaign 253, strategy `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_DEVIATION_SHOCK_MR` (quartile deviation / semi-interquartile range, pre-stated fixed `QD=(Q3-Q1)/2` with `Q1=np.percentile(arr,25)`, `Q3=np.percentile(arr,75)`, NumPy default linear interpolation, of qualifying WHITE diagonal segment lengths pooled over off-diagonal diagonals k!=0; fail-closed if <3 segments or Q1/Q3 non-finite or (Q3-Q1)<=0 or QD<=0/degenerate or ratio undefined/non-finite), edge_claim **NONE**, oos_edge_proven **false**, all_new_c253_artifact_paths_sha256_from_bytes **true**.
- **Distinctness (pre-run, required):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_DEVIATION|WHITE_DIAG_LINE_LENGTH_QUARTILE_DEVIATION' scripts/ strategies/ backtest/ utils/` → 0 nonself hits at run (`grep_hits_nonself_at_run: 0`; self + own campaign emit/ingest scripts excluded in-script).
- **Commands run (from repo root):** distinctness grep; created `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_quartile_deviation_shock_mr_costed_oos.py`, `scripts/run_real_feed_ingest_attempt_253.py`, `scripts/emit_campaign253_registry.py`, `scripts/emit_campaign253_summary.py`; `python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_quartile_deviation_shock_mr_costed_oos.py`; `python3 scripts/run_real_feed_ingest_attempt_253.py`; `python3 scripts/emit_campaign253_registry.py`; `python3 scripts/emit_campaign253_summary.py`.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_quartile_deviation_shock_mr_costed_oos_20261111T124208Z.json` — `9145124daa97ff0ac8ed9b676eff0fadad92bbfb1c4d7ba5940655482267c33f`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_quartile_deviation_shock_mr_costed_oos.py` — `f3011b61b1a9b3dc4edd90e640a6ce0cab3308d0c16095e7ff6eba8105a642ca`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T124802Z.json` — `ad077d81b75cfa167695bd6b99ca3f74bd8b64d91f5a4e46a604095f769cb1f7`
  - Registry: `reports/strategy_edge_registry_20261111T124803Z.json` — `6829a6dd9598892636c021da790c9c71e893902855b698629a08df555faf2494`
  - Summary: `reports/campaign253_execution_summary_20261111T124803Z.json` — `4382f884e0bf07c421dfe533edbfaffa709d6b2bc6a1be4de274d0c8ffd1b90d`
- **Evidence (real data, WF 720/168/168, costs [[0,0],[5,5],[10,10],[20,20],[40,40]]):**
  - `cross_asset_oos_net_sums`: fee0_slip0=-1.859703456753104, fee5_slip5=-3.003703456753105, fee10_slip10=-4.1477034567531055, fee20_slip20=-6.435703456753105, fee40_slip40=-11.011703456753104
  - `any_exposure_oos: true`
  - `all_cost_slices_positive_oos_net_sum: false`
  - `all_cost_slices_beat_bh_mean_rule: false`
  - **Conclusion:** `oos_edge_proven: false`, `edge_claim: NONE`. No edge found (fails all-cost-slices-positive and BH-beat rules); honest no-edge recorded.

## C252 (MAIN LINE — COMPLETE, 2026-11-11T12:20:52Z UTC)

- Campaign 252, strategy `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW_SHOCK_MR`, edge_claim **NONE**, oos_edge_proven **false**.
- OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_skew_shock_mr_costed_oos_20261111T121511Z.json` — `6f7fb512d2c3eded0d9634337b5e787ab46699e1ca057d7ecf69d1d9b36dbe7b`
- Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_skew_shock_mr_costed_oos.py` — `57a6e0db98f07e596ea28c7ca0fdcaceb05f3f3d27ea8ec960fe7d00f6e6c04b`
- Ingest: `reports/real_feed_ingest_attempt_20261111T121310Z.json` — `35c71d6e0ac4172bf6897bf347021162b936c5ea7955a7c4906a240b0090b316`
- Registry: `reports/strategy_edge_registry_20261111T122051Z.json` — `30b19d73024700bd855fd7a507a6c93fcbe527cb2347f769155becfb555f9851`
- Summary: `reports/campaign252_execution_summary_20261111T122052Z.json` — `4d2b6ae8541e3abfdbc2c1a58760214be1fac5709a157272d4c42906ba179aba`
- Evidence: cross_asset_oos_net_sums fee0_slip0=2.3437845178451764, fee5_slip5=0.6557845178451747, fee10_slip10=-1.0322154821548257, fee20_slip20=-4.408215482154825, fee40_slip40=-11.160215482154824; any_exposure_oos true; all_cost_slices_positive_oos_net_sum false; all_cost_slices_beat_bh_mean_rule true. No edge (fails all-cost-slices-positive).

## C251 (MAIN LINE — COMPLETE)

- Campaign 251, strategy `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE_SHOCK_MR`, edge_claim NONE, oos_edge_proven false.
- OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_midrange_shock_mr_costed_oos_20261111T111904Z.json` (sha256 `8764897cf3b1b7746568bb43f6c088c504f167d10c12ccdfdd18c990c77883ef`)
- Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_midrange_shock_mr_costed_oos.py` (sha256 `794807178d5f60649d533c531d02e24e40f44c0ccef992e9c721f5e64c26331a`)
- Ingest: `reports/real_feed_ingest_attempt_20261111T112426Z.json` (sha256 `ca2efb4b27fb4902e3f8b9be8bb4983c59b28be32b15a76b12e7ad0f4b896638`)
- Registry: `reports/strategy_edge_registry_20261111T112426Z.json` (sha256 `e1c8ba8c8382daedebc22e75c19a218fe7e0d9d8d5d2a0953e929c348d02eecd`)
- Summary: `reports/campaign251_execution_summary_20261111T112427Z.json` (sha256 `fb89eb1c1c45f67311ad9dbdccedd1ff7c0584988f4e7a12fbd673b2c74df837`)
- Evidence: cross_asset_oos_net_sums all negative; `any_exposure_oos: true`; `all_cost_slices_positive_oos_net_sum: false`; `all_cost_slices_beat_bh_mean_rule: false`.

## C250 (MAIN LINE — COMPLETE)

- Campaign 250, strategy `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K_SHOCK_MR`, edge_claim NONE, oos_edge_proven false.
- OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos_20261111T103421Z.json` (sha256 `af1e3767a474fe28f839a42cc7662fd2f933aadd72df57a4ae76249af211bd7b`)
- Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_yule_k_shock_mr_costed_oos.py` (sha256 `1f94dc35ae8bda2f94e933ed90bee5f34ccde81efacee9ae8cb6352a1764828b`)
- Ingest: `reports/real_feed_ingest_attempt_20261111T104044Z.json` (sha256 `eed9819368d4c5106fa6aab1c01e0a0cd5bb22fcdc62e23e22614b797480d903`)
- Registry: `reports/strategy_edge_registry_20261111T104048Z.json` (sha256 `37d4a9b6f418c7dcf180c39e02bf89aeb3751c060b6d75b510c19bec4ec6b4d7`)
- Summary: `reports/campaign250_execution_summary_20261111T104050Z.json` (sha256 `facee955b68c9498aac50631a3bda06097042f9e44a1175f226b3da69a66729f`)

## C249 (RESEARCH LINE — COMPLETE)

- `reports/campaign249_execution_summary_20261110T170949Z.json`, strategy `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW_SHOCK_MR`, edge_claim NONE, oos_edge_proven false.
- OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_groeneveld_meeden_skew_shock_mr_costed_oos_20261109T034759Z.json` (sha256 `042fa8fb58b1b2976869cb0508396325d7d25eed075b38ecbf4043033f2615b4`)
- Registry: `reports/strategy_edge_registry_20261110T170949Z.json` (sha256 `e3a17b7c880da04429f269cbaeec9b4fe5364ee9d865962b68304bdeda782c00`)

## C14/C15 (COMPLETE, zero edge)

- C14 7/7 `insufficient_or_blocked`/`no_edge`; no cost-aware OOS triggered. C15 7/7 `no_edge`/`insufficient_or_blocked`; no cost-aware OOS triggered. No re-runs except evidence-backed defect fix.

## BOTTLENECK REMOVAL (pre-cleared/re-verified — 2026-11-11T13:13:44Z UTC)

- C12–C15, C249–C254 complete — no re-runs permitted except evidence-backed defect fix.
- All caches `.pkl`+`.meta.json` present in `data/cache/`; no network refetch (real cached spot/volume only).
- **Python/deps:** `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1 (missing c7-venv not a blocker).
- `research_state/state.yaml` locked/stale — do not touch; does not block C255.
- **Grep-zero re-verified this session:** `MEDIAN_ABSOLUTE_DEVIATION`=0 and `WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE`=0 (primary/fallback). `python3` 3.12.3 + numpy 2.5.4/pandas 3.1.1/scipy 1.18.1 available.
- No blocking background process. No status-only work.

## HARD BANS

- ❌ No status-only work
- ❌ No re-runs of C1–C15 or C249–C254 except evidence-backed defect fix
- ❌ No network refetch (use `data/cache/` only)
- ❌ No synthetic/fabricated data
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked for C1–C15)
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user
- ❌ No early exit — C255 run must complete unless `oos_edge_proven: true`
- ❌ No "planning" or "researching" as substitute for running the script and producing artifacts

## KEY FILES

- C254 (latest pattern): `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_mean_absolute_deviation_shock_mr_costed_oos.py`, `scripts/run_real_feed_ingest_attempt_254.py`, `scripts/emit_campaign254_registry.py`, `scripts/emit_campaign254_summary.py`, `reports/campaign254_execution_summary_20261111T130410Z.json`, `reports/strategy_edge_registry_20261111T130410Z.json`
- C253 pattern: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_quartile_deviation_shock_mr_costed_oos.py`, `reports/campaign253_execution_summary_20261111T124803Z.json`
- C252 pattern: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_skew_shock_mr_costed_oos.py`, `reports/campaign252_execution_summary_20261111T122052Z.json`
- Strategy/gates (C1–C15 line): `strategies/pairs_trading.py`, `utils/cointegration.py`
- Caches (real-only): `data/cache/*.{pkl,meta.json}`
- Locked separate line (do not edit): `research_state/state.yaml`

**If MEDIAN_ABSOLUTE_DEVIATION fails grep-zero or is blocked:** pick next grep-zero distinct fallback (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE` / `WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE`, grep-zero pre-checked 2026-11-11T13:04:10Z), record evidence, implement/run it (no status-only stop).

**END OF DURABLE HANDOFF — verified/updated 2026-11-11T13:13:44Z UTC.** C12–C15 complete (zero edge). C249–C254 complete (NONE). **C254 COMPLETE** (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEAN_ABSOLUTE_DEVIATION`, `edge_claim: NONE`, `oos_edge_proven: false`) — 5 artifacts+SHA256 from bytes recorded in C254 section. **C255 NOT STARTED.** **IMMEDIATE NEXT ACTION (non-deferrable): Campaign #255 — implement/run `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABSOLUTE_DEVIATION` (grep-zero pre-checked) via `python3` from C254 pattern, produce timestamped OOS/script/ingest/registry/summary artifacts with SHA256-from-bytes, record honest edge/no-edge with evidence, then update this handoff. Do not stop at planning. No status-only work.**
