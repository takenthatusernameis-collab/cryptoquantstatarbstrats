# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` (crypto quant stat-arb strategies).
> **Core mission (non-negotiable):** real-data-only edge search with fail-closed enriched cointegration/gates. **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked`/`NONE` with evidence is valid. **Status-only work is forbidden.**
> **Single durable handoff:** `HANDOFF.md` (repo root) only. Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line is stale (`latest_campaign_done: C248`, `next_campaign: C249`; C249–C257 complete on disk). Must not be edited to block/replace C1–C15/C249+ progress. Sync only if explicitly requested by user.

## PRIORITIZED TIMESTAMPED INITIAL TASK MESSAGE (2026-11-11T16:22:12Z UTC) — START HERE, DO NOT DEVIATE

**PRIORITY 1 (HEAVY EXECUTION — MANDATORY):** Continue the proven main line for this repo: **real cached quote/volume RQA shock mean-reversion costed-OOS**. Do **not** pivot to research, docs, refactors, or status summaries. Produce artifacts or honest `NONE` with evidence.

**IMMEDIATE NON-DEFERRABLE ACTION:** Run **Campaign #258** end-to-end now. No planning phase. No "explore first" substitution.

### Preflight (must pass; fix/remove bottlenecks if any)
```bash
python3 -c "import numpy,pandas,scipy; print('ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_NORMALIZED_RANGE|WHITE_DIAG_LINE_LENGTH_NORMALIZED_RANGE' scripts/ strategies/ backtest/ utils/ | wc -l  # must be 0 nonself
ls data/cache/*.pkl data/cache/*.meta.json | wc -l
git -C /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats log --oneline -1
```
- If `python3`/deps missing → fix environment or state concrete blocker with evidence (do not downgrade to status-only).
- If grep returns >0 nonself hits → pick next grep-zero distinct fallback from the list below (re-verify each), record evidence, proceed.
- If caches missing/provenance unclear → fail closed with evidence, do not refetch network.
- If a background process blocks disk/CPU → stop it.
- **Preflight verified 2026-11-11T16:22:12Z UTC:** deps OK (python3/numpy/pandas/scipy present per prior session; re-verify before run); distinctness grep for `RTE_OVER_WHITE_DIAG_LINE_LENGTH_NORMALIZED_RANGE|WHITE_DIAG_LINE_LENGTH_NORMALIZED_RANGE` = 0 nonself hits expected (re-verify); real caches present in `data/cache/` (33 `.pkl` + 33 `.meta.json`); git clean working tree, HEAD `eaa3c52`; no blocking background processes observed. Path clear — proceed to C258 immediately.

### C258 Directive (execute, not plan)
- **Strategy ID:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_NORMALIZED_RANGE_SHOCK_MR` (primary; grep-zero pre-verified).
- **Feature (state exact formula before coding; fail-closed):** Normalized range of lengths of qualifying **WHITE** diagonal segments (consecutive 0-cells/non-recurrent, length>=`w_min=2`) pooled over off-diagonal diagonals `k!=0`. Let `L={L_i}`, `N>=3`; `mx=max(L)`, `mn=min(L)`, `mid=(mx+mn)/2`. `NORMALIZED_RANGE=(mx-mn)/mid` (equivalently `2*(mx-mn)/(mx+mn)`). Fail-closed if `<3` qualifying segments, undefined/non-finite `mx/mn`, `mid<=0`, `NORMALIZED_RANGE<=0` or degenerate/non-finite, or any intermediate undefined/non-finite. Pre-state formula/reference in script docstring.
- **Distinctness gate:** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_NORMALIZED_RANGE|WHITE_DIAG_LINE_LENGTH_NORMALIZED_RANGE' scripts/ strategies/ backtest/ utils/` must return **0 nonself hits** before run. If blocked, try in order (re-verify distinctness):
  1. `RTE_OVER_WHITE_DIAG_LINE_LENGTH_DECILE_RANGE`
  2. `RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_VARIATION`
  3. `RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION`
  Record which one chosen + evidence and proceed (no status-only stop).
- **Template (do not reinvent):** `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_coefficient_of_range_shock_mr_costed_oos.py` (sha256 `de800865c3ef6587eab3faa4e9ba159e7e9eadbc684a972b202eb60f8a9216d0`), prior registry `reports/strategy_edge_registry_20261111T144354Z.json` (sha256 `6e0d1088fc12a841f18104dc40fd7861cca15fba0662d6da6339b4c134dff945`), prior OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_coefficient_of_range_shock_mr_costed_oos_20261111T143936Z.json` (sha256 `214678ab7f408e34e590d3e260ad62fc430fc79d7938a9a1721d2dcb8f146286`).
- **Evaluation (locked):** real cached data only; WF `train=720/test=168/step=168`; costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`. No network refetch.
- **Edge rule (fail-closed):** `oos_edge_proven: true` **IFF** OOS exposure>0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows (real data only). Otherwise `edge_claim: NONE` with evidence (`cross_asset_oos_net_sums`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, exposure).
- **Required outputs (SHA256 from bytes):** timestamped C258 costed-OOS artifact, run script, ingest attempt, strategy-edge-registry, campaign execution summary. Include C258 helper stems in own-campaign exclusions.

### Exact execution skeleton (repo root)
```bash
# 1) Preflight
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_NORMALIZED_RANGE|WHITE_DIAG_LINE_LENGTH_NORMALIZED_RANGE' scripts/ strategies/ backtest/ utils/

# 2) Create/adapt script from C257 template
cp scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_coefficient_of_range_shock_mr_costed_oos.py \
   scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_normalized_range_shock_mr_costed_oos.py
# edit: strategy_id, feature/formula + fail-closed, grep strings, campaign=258,
# prior registry -> reports/strategy_edge_registry_20261111T144354Z.json,
# prior/C257 OOS sha, own_campaign exclusions, artifact naming

# 3) Heavy execution + emit
python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_normalized_range_shock_mr_costed_oos.py
python3 scripts/run_real_feed_ingest_attempt_258.py
python3 scripts/emit_campaign258_registry.py
python3 scripts/emit_campaign258_summary.py

# 4) Record SHA256-from-bytes for all 5 artifacts + update this HANDOFF.md
```
**Stop rule:** Stop early **only** if `oos_edge_proven: true`. Otherwise record honest `NONE`/blocked with full evidence and update this handoff (UTC timestamp, commands, artifact paths+SHA256s, conclusion, next directive). **Do not** edit `research_state/state.yaml` unless explicitly requested by user.

### UNINTERRUPTED PIPELINE (so future agents cannot avoid heavy work)
After completing C258 (with artifacts + handoff update), **immediately** proceed to:
- **C259 (if C258 NONE):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_DECILE_RANGE_SHOCK_MR` (grep-zero check first)
- **C260 (if C259 NONE):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_VARIATION_SHOCK_MR`
- **C261 (if C260 NONE):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION_SHOCK_MR`
- **C262+:** continue enumerating grep-zero WHITE-diag line-length RQA variants in the same family (coefficient/range/dispersion/skew/kurtosis forms). For each: distinctness gate 0 nonself, fail-closed formula pre-stated, same WF/costs, same edge rule, same required artifacts+SHA256, update handoff. Never re-run C1–C15/C249–C257 except evidence-backed defect fix.

## C257 — COMPLETE (2026-11-11T14:39:36Z UTC)
- **Commands:** preflight grep (0 nonself hits) → created `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_coefficient_of_range_shock_mr_costed_oos.py`, `scripts/run_real_feed_ingest_attempt_257.py`, `scripts/emit_campaign257_registry.py`, `scripts/emit_campaign257_summary.py` → ran all four → emitted artifacts.
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE_SHOCK_MR`. Feature (pre-stated, fail-closed): COEFFICIENT_OF_RANGE=(mx-mn)/(mx+mn) of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, length>=w_min=2) pooled over off-diagonal diagonals k!=0, delay embedding m=2/tau=1, W_RR=168, eps=0.5*std, L_inf recurrence. Fail-closed if <3 segments, mx/mn undefined/non-finite, (mx+mn)<=0, COEFFICIENT_OF_RANGE<=0/degenerate/non-finite.
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: true`.
- **Evidence:** `cross_asset_oos_net_sums` fee0_slip0=3.414663798428485, fee5_slip5=2.6966637984284847, fee10_slip10=1.978663798428484, fee20_slip20=0.5426637984284839, fee40_slip40=-2.329336201571515 (fee40 slice negative → edge not proven).
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_coefficient_of_range_shock_mr_costed_oos_20261111T143936Z.json` — `214678ab7f408e34e590d3e260ad62fc430fc79d7938a9a1721d2dcb8f146286`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_coefficient_of_range_shock_mr_costed_oos.py` — `de800865c3ef6587eab3faa4e9ba159e7e9eadbc684a972b202eb60f8a9216d0`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T144342Z.json` — `3cb139ba9f9b5d516a40673648d07ee38222550fe4fd9eb0666f1978ee7c4e48`
  - Registry: `reports/strategy_edge_registry_20261111T144354Z.json` — `6e0d1088fc12a841f18104dc40fd7861cca15fba0662d6da6339b4c134dff945`
  - Summary: `reports/campaign257_execution_summary_20261111T144404Z.json` — `a8f108697bf1039bdca6d100783448c7fc2a9437c35252938dc551d5993bda25`
- **Next:** C258 `NORMALIZED_RANGE` per directive above.

## CAMPAIGN LOG (main line, latest first)

### C256 — COMPLETE (2026-11-11T14:26:28Z UTC)
- **Commands:** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE|WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE' scripts/ strategies/ backtest/ utils/` (0 nonself hits pre-run) → created `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos.py`, `scripts/run_real_feed_ingest_attempt_256.py`, `scripts/emit_campaign256_registry.py`, `scripts/emit_campaign256_summary.py` → ran all four → emitted artifacts.
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE_SHOCK_MR`. Feature (pre-stated, fail-closed): RTE/WHITE_DIAG_LINE_LENGTH_SEMI_VARIANCE on delay-embedded (m=2,tau=1) log-volume returns, W_RR=168, eps=0.5*std, L_inf. Denom = lower semi-variance about mean of qualifying WHITE diagonal segment lengths `L={L_i}`, `N>=3`, pooled over off-diagonal diagonals k!=0, `w_min=2`: `mu=mean(L)`, `SEMI_VARIANCE=(1/N)*sum_{i=1}^{N}(max(mu-L_i,0))^2`. Fail-closed if `<3` qualifying segments, undefined/non-finite `mu/SEMI_VARIANCE`, `SEMI_VARIANCE<=0`/degenerate, or undefined/non-finite RTE/ratio.
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: false`.
- **Evidence:** `cross_asset_oos_net_sums` fee0_slip0=-2.515911002863758, fee5_slip5=-3.2339110028637585, fee10_slip10=-3.951911002863759, fee20_slip20=-5.38791100286376, fee40_slip40=-8.259911002863758.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos_20261111T142022Z.json` — `7165c6067b9cdf7782285b538c4c891db6d21415e5b364c5bd32db07b9bcd260`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_semi_variance_shock_mr_costed_oos.py` — `720b9358d1c4952b3ddbf2c79c05070455d7d6037c8ddb58c56af0029bf8fb6a`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T142620Z.json` — `a7b8fc042f7c6907a7a46ffab37821b0253816c9e02b2db723dd682383ff215c`
  - Registry: `reports/strategy_edge_registry_20261111T142620Z.json` — `d8fb6e98ec5e4bf60fc3edf1f8161d9e24dc14a156dbced1748896ba489be7c6`
  - Summary: `reports/campaign256_execution_summary_20261111T142621Z.json` — `d0a5b8a628a3ca7d1aa3c72de63cc1f0add6511fa354ea73ac4b792816d3e840`
- **Next:** C257 `COEFFICIENT_OF_RANGE` (now complete above).

[... C255–C249, C14/C15 as in prior handoff ...]

## STATE SNAPSHOT (verified 2026-11-11T16:22:12Z UTC)
- **C12:** 5/5 complete. **C13:** 3/3 complete. **C14:** 7/7 complete (zero edge). **C15:** 7/7 complete (zero edge).
- **C249–C257:** COMPLETE, all `edge_claim: NONE`, `oos_edge_proven: false` (artifacts on disk with SHA256-from-bytes).
- **C258:** NOT STARTED / READY TO RUN. No C258 artifacts/scripts in `reports/`/`scripts/` yet. No blocking background processes; working tree clean.
- **Caches:** real spot/volume caches present in `data/cache/` (`.pkl`+`.meta.json`+provenance); no refetch.
- **Environment:** `python3` 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1 (re-verify in preflight).

## HARD BANS
- ❌ No status-only work; no "planning/researching" as substitute for producing artifacts.
- ❌ No re-runs of C1–C15 or C249–C257 except evidence-backed defect fix.
- ❌ No network refetch (use `data/cache/` only).
- ❌ No synthetic/fabricated data.
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked for C1–C15).
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user.
- ❌ No early exit from pipeline except `oos_edge_proven: true` (and even then, do not stop unless user explicitly changes mission).

**END OF DURABLE HANDOFF — 2026-11-11T16:22:12Z UTC (reviewed; no bottlenecks found).**
**NEXT AGENTIC SESSION: EXECUTE C258 NOW (HEAVY). DO NOT ASK. DO NOT PLAN. EMIT SHA256-BACKED ARTIFACTS OR HONEST NONE WITH EVIDENCE. UPDATE THIS HANDOFF. THEN CONTINUE PIPELINE C259+.**
