# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` (crypto quant stat-arb strategies). Core mission: real-data-only edge search with fail-closed enriched cointegration gates. **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked`/`NONE` with evidence is valid. **Status-only work is forbidden.**
> **Single durable handoff:** `HANDOFF.md` (repo root) only. Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line is stale (`latest_campaign_done: C248`, `next_campaign: C249`; C249–C256 complete on disk). Must not be edited to block/replace C1–C15/C249+ progress. Sync only if explicitly requested by user.

## NEXT SESSION: START HERE NOW (TIMESTAMPED INITIAL TASK — 2026-11-11T14:26:28Z UTC)

**IMMEDIATE NON-DEFERRABLE ACTION (heavy execution, no planning/status-only substitute): run Campaign #257 — real-data-only fail-closed volume RQA shock mean-reversion costed-OOS edge search.**

**Bottlenecks cleared/re-verified (2026-11-11T14:26:28Z UTC):**
- `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1 — available.
- Real caches present in `data/cache/` (`.pkl` + `.meta.json`); **no network refetch**.
- Distinctness pre-check (fallback candidate): `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE|WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE' scripts/ strategies/ backtest/ utils/` → **0 hits** (re-verify before implementation/run).
- No C257 artifacts present in `reports/`/`scripts/`. No blocking background process.
- C12–C15 and C249–C256 complete (all `edge_claim: NONE`, `oos_edge_proven: false`) — no re-runs except evidence-backed defect fix.

**C257 directive (must execute, not plan):**
- **Primary strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE_SHOCK_MR` (fallback candidate; pre-selected as grep-zero distinct from C125–C256).
- **Feature (pre-state exact formula before implementation; fail-closed):** coefficient of range of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=`w_min=2`) pooled over off-diagonal diagonals `k!=0`. Before coding, state exact formula/reference: let `L={L_i}`, `N>=3`; `mx=max(L)`, `mn=min(L)`; `COEFFICIENT_OF_RANGE=(mx-mn)/(mx+mn)` (pre-stated). Enforce fail-closed on `<3` qualifying segments, undefined/non-finite `mx/mn`, `(mx+mn)<=0`, `COEFFICIENT_OF_RANGE<=0`/degenerate/non-finite, or undefined/non-finite ratio/feature.
- **Distinctness gate:** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE|WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE' scripts/ strategies/ backtest/ utils/` must return **0 nonself hits** before run. If blocked/fails distinctness, pick next grep-zero distinct fallback (e.g. `RTE_OVER_WHITE_DIAG_LINE_LENGTH_NORMALIZED_RANGE`, `RTE_OVER_WHITE_DIAG_LINE_LENGTH_DECILE_RANGE`, `RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_VARIATION` — re-verify each), record evidence, and proceed (no status-only stop).
- **Prior registry/input:** `reports/strategy_edge_registry_20261111T142620Z.json` (sha256 `d8fb6e98ec5e4bf60fc3edf1f8161d9e24dc14a156dbced1748896ba489be7c6`). Use C256 artifacts/pattern as template:
  - script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos.py` (sha256 `720b9358d1c4952b3ddbf2c79c05070455d7d6037c8ddb58c56af0029bf8fb6a`)
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos_20261111T142022Z.json` (sha256 `7165c6067b9cdf7782285b538c4c891db6d21415e5b364c5bd32db07b9bcd260`)
- **Evaluation (locked):** real cached data only; WF `train=720/test=168/step=168`; costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.
- **Edge rule (fail-closed, honest):** `oos_edge_proven: true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows (real data only). Otherwise `edge_claim: NONE` with evidence (`cross_asset_oos_net_sums`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, exposure).
- **Required outputs (all SHA256 from bytes):** timestamped C257 costed-OOS artifact, run script, ingest attempt, strategy-edge-registry, campaign execution summary. Emit via `python3` from repo root (adapt C256 emit/run pattern; include C257 helper stems in own-campaign exclusions).
- **Stop condition:** stop early **only** if `oos_edge_proven: true`. Otherwise record honest `NONE`/blocked conclusion with evidence and update this handoff (UTC timestamp, commands, artifact paths+SHA256s, conclusion, next directive). **Do not edit `research_state/state.yaml` unless explicitly requested by user.**

**Exact execution skeleton (from repo root):**
```bash
# 1) Re-verify distinctness (must be 0 nonself hits)
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE|WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE' scripts/ strategies/ backtest/ utils/

# 2) Create/adapt C256-pattern script (state exact formula/reference + fail-closed)
cp scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos.py \
   scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_coefficient_of_range_shock_mr_costed_oos.py
# edit: strategy_id/feature/formula, grep strings, campaign=257, prior registry -> strategy_edge_registry_20261111T142620Z.json (d8fb6e98...), prior/C256 OOS sha 7165c606..., own_campaign exclusions, artifact naming

# 3) Run heavy work + emit artifacts
python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_coefficient_of_range_shock_mr_costed_oos.py
python3 scripts/run_real_feed_ingest_attempt_257.py
python3 scripts/emit_campaign257_registry.py
python3 scripts/emit_campaign257_summary.py

# 4) Compute/record SHA256-from-bytes for OOS, script, ingest, registry, summary
# 5) Update HANDOFF.md with timestamp, commands, paths+SHA256s, conclusion, next directive
```

## STATE SNAPSHOT (verified 2026-11-11T14:26:28Z UTC)

- **C12:** 5/5 complete. **C13:** 3/3 complete. **C14:** 7/7 complete (zero edge). **C15:** 7/7 complete (zero edge).
- **C249–C256:** COMPLETE, all `edge_claim: NONE`, `oos_edge_proven: false` (artifacts on disk with SHA256-from-bytes).
- **C257:** NOT STARTED (no C257 artifacts/scripts in `reports/`/`scripts/` at this timestamp).
- **Caches:** real spot/volume caches present in `data/cache/` (`.pkl`+`.meta.json`+provenance); no refetch.
- **Environment:** `python3` 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1.

## CAMPAIGN LOG (main line, latest first)

### C256 — COMPLETE (2026-11-11T14:26:28Z UTC)
- **Commands:** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE|WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE' scripts/ strategies/ backtest/ utils/` (0 nonself hits pre-run) → created `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos.py`, `scripts/run_real_feed_ingest_attempt_256.py`, `scripts/emit_campaign256_registry.py`, `scripts/emit_campaign256_summary.py` → `python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos.py` → `python3 scripts/run_real_feed_ingest_attempt_256.py` → `python3 scripts/emit_campaign256_registry.py` → `python3 scripts/emit_campaign256_summary.py`.
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE_SHOCK_MR`. Feature (pre-stated, fail-closed): RTE/WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE on delay-embedded (m=2,tau=1) log-volume returns, W_RR=168, eps=0.5*std, L_inf. Denominator = lower semi-variance about mean of qualifying WHITE diagonal segment lengths `L={L_i}`, `N>=3`, pooled over off-diagonal diagonals k!=0, `w_min=2`: `mu=mean(L)`, `SEMI_VARIANCE=(1/N)*sum_{i=1}^{N}(max(mu-L_i,0))^2` (mean squared shortfall below mean over all qualifying segments). Fail-closed if `<3` qualifying segments, undefined/non-finite `mu/SEMI_VARIANCE`, `SEMI_VARIANCE<=0`/degenerate (incl. no below-mean shortfall), or undefined/non-finite RTE/ratio.
- **Distinctness:** grep 0 nonself hits at run. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, real cached data only, no refetch.
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- **Evidence:** `cross_asset_oos_net_sums` fee0_slip0=-2.515911002863758, fee5_slip5=-3.2339110028637585, fee10_slip10=-3.951911002863759, fee20_slip20=-5.38791100286376, fee40_slip40=-8.259911002863758.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos_20261111T142022Z.json` — `7165c6067b9cdf7782285b538c4c891db6d21415e5b364c5bd32db07b9bcd260`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos.py` — `720b9358d1c4952b3ddbf2c79c05070455d7d6037c8ddb58c56af0029bf8fb6a`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T142620Z.json` — `a7b8fc042f7c6907a7a46ffab37821b0253816c9e02b2db723dd682383ff215c`
  - Registry: `reports/strategy_edge_registry_20261111T142620Z.json` — `d8fb6e98ec5e4bf60fc3edf1f8161d9e24dc14a156dbced1748896ba489be7c6`
  - Summary: `reports/campaign256_execution_summary_20261111T142621Z.json` — `d0a5b8a628a3ca7d1aa3c72de63cc1f0add6511fa354ea73ac4b792816d3e840`
- **Next directive:** Campaign #257 `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE_SHOCK_MR` (primary, grep-zero pre-verified). State exact formula/reference pre-implementation, enforce fail-closed, run WF/costs locked, emit SHA256-backed artifacts, update handoff.

### C255 — COMPLETE (2026-11-11T13:33:43Z UTC)
- Strategy: `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABSOLUTE_DEVIATION_SHOCK_MR` (median absolute deviation of qualifying WHITE diagonal segment lengths; exact pre-stated formula in artifacts). `edge_claim: NONE`, `oos_edge_proven: false`. Distinctness grep nonself hits at run: 0.
- Evidence: `cross_asset_oos_net_sums` fee0_slip0=-1.3490544354441005, fee5_slip5=-2.4850544354441015, fee10_slip10=-3.621054435444102, fee20_slip20=-5.8930544354441015, fee40_slip40=-10.437054435444102; `any_exposure_oos: true`; `all_cost_slices_positive_oos_net_sum: false`; `all_cost_slices_beat_bh_mean_rule: false`.
- Artifacts (SHA256 from bytes):
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_median_absolute_deviation_shock_mr_costed_oos_20261111T132821Z.json` — `d5aa64cfd5270e0c4af4909998fb59ca078edd200ac29e82e81981d6e04c76e2`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_median_absolute_deviation_shock_mr_costed_oos.py` — `905b3bd4532ce38da290aec265ebc6539e3c79e3a39679c9f2890ee8abfee706`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T132612Z.json` — `d64ffe064c77714571955e5ffca29455c74d0b8c09e11edc42735c0dedab3e48`
  - Registry: `reports/strategy_edge_registry_20261111T133343Z.json` — `d676c82467a421eae715340d2b1e9b0aa81a26ab8cc1f04b56d47441332756e7`
  - Summary: `reports/campaign255_execution_summary_20261111T133343Z.json` — `7d10bd802f9180086b38d9f3974d875f4dab4a6f67f47716604fe0c0182c5944`

### C254 — COMPLETE (2026-11-11T13:04:10Z UTC)
- Strategy: `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEAN_ABSOLUTE_DEVIATION_SHOCK_MR`. `edge_claim: NONE`, `oos_edge_proven: false`.
- Evidence: fee0_slip0=-2.8516343128245802, fee5_slip5=-3.5576343128245806, fee10_slip10=-4.263634312824581, fee20_slip20=-5.675634312824582, fee40_slip40=-8.49963431282458; exposure true; all-cost-positive false; BH-beat false.
- Artifacts: OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_mean_absolute_deviation_shock_mr_costed_oos_20261111T125847Z.json` (`fa6324e9...`), script `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_mean_absolute_deviation_shock_mr_costed_oos.py` (`c388cfec...`), ingest `reports/real_feed_ingest_attempt_20261111T130409Z.json` (`6e6acf15...`), registry `reports/strategy_edge_registry_20261111T130410Z.json` (`4b546a84...`), summary `reports/campaign254_execution_summary_20261111T130410Z.json` (`ba41511e...`).

### C253 — COMPLETE (2026-11-11T12:48:32Z UTC)
- Strategy: `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_DEVIATION_SHOCK_MR`. `edge_claim: NONE`, `oos_edge_proven: false`.
- Evidence: fee0_slip0=-1.859703456753104, fee5_slip5=-3.003703456753105, fee10_slip10=-4.1477034567531055, fee20_slip20=-6.435703456753105, fee40_slip40=-11.011703456753104; exposure true; all-cost-positive false; BH-beat false.
- Artifacts: OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_quartile_deviation_shock_mr_costed_oos_20261111T124208Z.json` (`9145124d...`), script `..._quartile_deviation_shock_mr_costed_oos.py` (`f3011b61...`), ingest `reports/real_feed_ingest_attempt_20261111T124802Z.json` (`ad077d81...`), registry `reports/strategy_edge_registry_20261111T124803Z.json` (`6829a6dd...`), summary `reports/campaign253_execution_summary_20261111T124803Z.json` (`4382f884...`).

### C252 — COMPLETE (2026-11-11T12:20:52Z UTC)
- Strategy: `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_SKEW_SHOCK_MR`. `edge_claim: NONE`, `oos_edge_proven: false`.
- Evidence: fee0_slip0=2.3437845178451764, fee5_slip5=0.6557845178451747, fee10_slip10=-1.0322154821548257, fee20_slip20=-4.408215482154825, fee40_slip40=-11.160215482154824; exposure true; all-cost-positive false; BH-beat true (still no edge).
- Artifacts: OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_skew_shock_mr_costed_oos_20261111T121511Z.json` (`6f7fb512...`), registry `reports/strategy_edge_registry_20261111T122051Z.json` (`30b19d73...`), summary `reports/campaign252_execution_summary_20261111T122052Z.json` (`4d2b6ae8...`).

### C251 — COMPLETE
- Strategy: `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MIDRANGE_SHOCK_MR`. `edge_claim: NONE`, `oos_edge_proven: false`. All-cost sums negative; exposure true. OOS sha `8764897c...`, registry `e1c8ba8c...`, summary `fb89eb1c...`.

### C250 — COMPLETE
- Strategy: `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_YULE_K_SHOCK_MR`. `edge_claim: NONE`, `oos_edge_proven: false`. OOS sha `af1e3767...`, registry `37d4a9b6...`, summary `facee955...`.

### C249 — COMPLETE (research line)
- Strategy: `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_GROENEVELD_MEEDEN_SKEW_SHOCK_MR`. `edge_claim: NONE`, `oos_edge_proven: false`. OOS sha `042fa8fb...`, registry `e3a17b7c...`, summary `reports/campaign249_execution_summary_20261110T170949Z.json`.

### C14/C15 — COMPLETE
- C14 7/7 `insufficient_or_blocked`/`no_edge`; no cost-aware OOS triggered. C15 7/7 `no_edge`/`insufficient_or_blocked`; no cost-aware OOS triggered.

## HARD BANS

- ❌ No status-only work; no "planning/researching" as substitute for producing artifacts.
- ❌ No re-runs of C1–C15 or C249–C255 except evidence-backed defect fix.
- ❌ No network refetch (use `data/cache/` only).
- ❌ No synthetic/fabricated data (prices/IV/volume/fills/order books/labels/metrics).
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked for C1–C15).
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user.
- ❌ No early exit on C256 unless `oos_edge_proven: true`; otherwise emit honest `NONE` + evidence and update handoff.

## KEY FILES

- Latest template/pattern (C256): `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos.py`, `reports/campaign256_execution_summary_20261111T142621Z.json`, `reports/strategy_edge_registry_20261111T142620Z.json`.
- Prior patterns: C255/C254/C253/C252/C251/C250 scripts and summaries in `scripts/` and `reports/`.
- Strategy/gates (C1–C15 line): `strategies/pairs_trading.py`, `utils/cointegration.py`.
- Caches (real-only): `data/cache/*.{pkl,meta.json}`, `data/cache/volume_1h_full.provenance.json`.
- Locked separate line (do not edit): `research_state/state.yaml`.

**END OF DURABLE HANDOFF — 2026-11-11T14:26:28Z UTC.** Next heavy action: **Campaign #257 `RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE`** (grep-zero pre-verified, deps/caches ready). Execute now, emit SHA256-backed artifacts, record honest edge/no-edge with evidence, update this handoff.
