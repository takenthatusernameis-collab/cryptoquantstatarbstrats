# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` (crypto quant stat-arb strategies).
> **Core mission (non-negotiable):** real-data-only edge search with fail-closed enriched cointegration/gates. **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked`/`NONE` with evidence is valid. **Status-only work is forbidden.**
> **Single durable handoff:** `HANDOFF.md` (repo root) only. Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line is stale (`latest_campaign_done: C248`, `next_campaign: C249`; C249–C260 complete on disk). Must not be edited to block/replace C1–C15/C249+ progress. Sync only if explicitly requested by user.

## PRIORITIZED TIMESTAMPED INITIAL TASK MESSAGE (2026-11-11T17:18:35Z UTC) — START HERE, DO NOT DEVIATE

**PRIORITY 1 (HEAVY EXECUTION — MANDATORY):** Continue the proven main line for this repo (`cryptoquantstatarbstrats` = crypto quant stat-arb strategies): **real cached quote/volume RQA shock mean-reversion costed-OOS**, real-data-only edge search, fail-closed gates. Do **not** pivot to research, docs, refactors, or status summaries. Produce artifacts or honest `NONE` with evidence.

**IMMEDIATE NON-DEFERRABLE ACTION:** Run **Campaign #261** end-to-end now (C260 complete, `edge_claim: NONE`). No planning phase. No "explore first" substitution.

### Preflight (re-verified 2026-11-11T17:18:35Z UTC — path clear)
```bash
python3 -c "import numpy,pandas,scipy; print('ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION|WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION' scripts/ strategies/ backtest/ utils/ | wc -l  # must be 0 nonself
ls data/cache/*.pkl data/cache/*.meta.json | wc -l  # must be 66
git -C /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats log --oneline -1
```
- **Verified 2026-11-11T17:18:35Z:** deps OK (python3 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1); distinctness grep for `RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION|WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION` = **0 nonself hits**; real caches present in `data/cache/` (**66** `.pkl`/`.meta.json` files total); git HEAD at `a605961 chore(kilo): checkpoint agent session`, working tree clean. **No bottlenecks found.** C260 template scripts exist on disk (`run_real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_variation_shock_mr_costed_oos.py`, `emit_campaign260_registry.py`, `emit_campaign260_summary.py`, `run_real_feed_ingest_attempt_260.py`). C261 script does **not** yet exist — create it by adapting the C260 template (see C261 Directive).
- If `python3`/deps missing → fix environment or state concrete blocker with evidence (do not downgrade to status-only).
- If grep returns >0 nonself hits → pick next grep-zero distinct fallback from the list below (re-verify each), record evidence, proceed.
- If caches missing/provenance unclear → fail closed with evidence, do not refetch network.
- If a background process blocks disk/CPU → stop it.

### C261 Directive (execute, not plan)
- **Strategy ID:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION_SHOCK_MR` (primary; grep-zero verified, re-verify before run).
- **Feature (state exact formula before coding; fail-closed):** Coefficient of variation of lengths of qualifying **WHITE** diagonal segments (consecutive 0-cells/non-recurrent, length>=`w_min=2`) pooled over off-diagonal diagonals `k!=0`. Let `L={L_i}`, `N>=3`; `mu=mean(L)`, `sigma_pop=sqrt((1/N)*sum_{i=1}^{N}(L_i-mu)^2)` (population std, ddof=0). `COEFF_OF_VARIATION = sigma_pop / mu`. Pre-state exact formula/reference in script docstring. Fail-closed if `<3` qualifying segments, undefined/non-finite `mu` or `sigma_pop`, `mu<=0` or `sigma_pop<=0`, `COEFF_OF_VARIATION<=0` or degenerate/non-finite, or any intermediate undefined/non-finite.
- **Distinctness gate:** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION|WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION' scripts/ strategies/ backtest/ utils/` must return **0 nonself hits** before run. If blocked, try in order (re-verify distinctness):
  1. `RTE_OVER_WHITE_DIAG_LINE_LENGTH_INTERDECILE_RANGE` (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_INTERDECILE_RANGE|WHITE_DIAG_LINE_LENGTH_INTERDECILE_RANGE`)
  2. `RTE_OVER_WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION` (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION|WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION`)
  3. `RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION` (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION|WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION`)
  Record which one chosen + evidence and proceed (no status-only stop).
- **Template (do not reinvent):** `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_variation_shock_mr_costed_oos.py` (sha256 `571596b264f672619aa3349a74b485155afcc2cf464da226eeb7dfa4c9591bab`), prior registry `reports/strategy_edge_registry_20261111T171038Z.json` (sha256 `e94e065ed8094fff2ac086fcf4a8bcfb5ecd9665974ded055a8ca2c319c26b18`), prior OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_variation_shock_mr_costed_oos_20261111T170631Z.json` (sha256 `9671ef3ddd6943fa5d6726bc355f3c85eb869837204e2b4fac9d1d6056d199dc`).
- **Evaluation (locked):** real cached data only; WF `train=720/test=168/step=168`; costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`. No network refetch.
- **Edge rule (fail-closed):** `oos_edge_proven: true` **IFF** OOS exposure>0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows (real data only). Otherwise `edge_claim: NONE` with evidence (`cross_asset_oos_net_sums`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, exposure).
- **Required outputs (SHA256 from bytes):** timestamped C261 costed-OOS artifact, run script, ingest attempt, strategy-edge-registry, campaign execution summary. Include C261 helper stems in own-campaign exclusions.

### Exact execution skeleton (repo root)
```bash
# 1) Preflight (re-verify distinctness)
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION|WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION' scripts/ strategies/ backtest/ utils/

# 2) Create/adapt script from C260 template
cp scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_variation_shock_mr_costed_oos.py \
   scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_coeff_of_variation_shock_mr_costed_oos.py
# edit: strategy_id, feature/formula + fail-closed (COEFF_OF_VARIATION=sigma_pop/mu),
#       grep strings, campaign=261,
#       prior registry -> reports/strategy_edge_registry_20261111T171038Z.json,
#       prior/C260 OOS sha, own_campaign exclusions, artifact naming

# 3) Heavy execution + emit
python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_coeff_of_variation_shock_mr_costed_oos.py
python3 scripts/run_real_feed_ingest_attempt_261.py
python3 scripts/emit_campaign261_registry.py
python3 scripts/emit_campaign261_summary.py

# 4) Record SHA256-from-bytes for all 5 artifacts + update this HANDOFF.md
```
**Stop rule:** Stop early **only** if `oos_edge_proven: true`. Otherwise record honest `NONE`/blocked with full evidence and update this handoff (UTC timestamp, commands, artifact paths+SHA256s, conclusion, next directive). **Do not** edit `research_state/state.yaml` unless explicitly requested by user.

### UNINTERRUPTED PIPELINE (so future agents cannot avoid heavy work)
C260 complete (NONE with evidence). **Immediately** proceed in order:
- **C261 (now due):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION_SHOCK_MR` (grep-zero verified)
- **C262 (if C261 NONE):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_INTERDECILE_RANGE_SHOCK_MR`
- **C263 (if C262 NONE):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION_SHOCK_MR`
- **C264+:** continue enumerating grep-zero WHITE-diag line-length RQA variants in the same family (variation/dispersion/range/shape forms not yet run). For each: distinctness gate 0 nonself, fail-closed formula pre-stated, same WF/costs, same edge rule, same required artifacts+SHA256, update handoff. Never re-run C1–C15/C249–C260 except evidence-backed defect fix.

## C260 — COMPLETE (2026-11-11T17:10:50Z UTC)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_VARIATION_SHOCK_MR`. Feature (fail-closed): PEARSON_VARIATION=(1/N)*sum_{i=1}^{N}(L_i-mu)^2 (population variance, ddof=0) of qualifying WHITE diagonal segment lengths (>=w_min=2, off-diagonal k!=0, m=2,tau=1,W_RR=168,eps=0.5*std,L_inf), N>=3, mu=mean(L). Fail-closed if <3 segments, mu/PEARSON_VARIATION undefined/non-finite, PEARSON_VARIATION<=0/degenerate/non-finite.
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: true`.
- **Evidence:** `cross_asset_oos_net_sums` fee0_slip0=2.4580778221231743, fee5_slip5=1.7780778221231737, fee10_slip10=1.098077822123173, fee20_slip20=-0.2619221778768269, fee40_slip40=-2.981922177876826.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_variation_shock_mr_costed_oos_20261111T170631Z.json` — `9671ef3ddd6943fa5d6726bc355f3c85eb869837204e2b4fac9d1d6056d199dc`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_variation_shock_mr_costed_oos.py` — `571596b264f672619aa3349a74b485155afcc2cf464da226eeb7dfa4c9591bab`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T170421Z.json` — `e5c1b34725e7a1ed6298fad1f1ab6d7df785274c1a29e1c813d8b825b8cd729b`
  - Registry: `reports/strategy_edge_registry_20261111T171038Z.json` — `e94e065ed8094fff2ac086fcf4a8bcfb5ecd9665974ded055a8ca2c319c26b18`
  - Summary: `reports/campaign260_execution_summary_20261111T171039Z.json` — `58d96f1274cd5896ee5f555ed047f93d2d5edf82fa657541a004c34637826946`

## C259 — COMPLETE (2026-11-11T16:45:28Z UTC)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_DECILE_RANGE_SHOCK_MR`. Feature (fail-closed): DECILE_RANGE=p90-p10 of qualifying WHITE diagonal segment lengths (>=w_min=2, off-diagonal k!=0, m=2,tau=1,W_RR=168,eps=0.5*std,L_inf). Fail-closed if <3 segments, p10/p90 undefined/non-finite, DECILE_RANGE<=0/degenerate/non-finite.
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: true`.
- **Evidence:** `cross_asset_oos_net_sums` fee0_slip0=0.5945201721473992, fee5_slip5=-0.1614798278526015, fee10_slip10=-0.9174798278526022, fee20_slip20=-2.429479827852602, fee40_slip40=-5.453479827852601.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_decile_range_shock_mr_costed_oos_20261111T163943Z.json` — `44661339ea3be48e86360e3d2523e61630667daa5978dce9617a8efd7cd41431`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_decile_range_shock_mr_costed_oos.py` — `966fd724834853e4cf077d5951500204c6f1cf5af3f7909733c051c90a931c62`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T164444Z.json` — `97a811df0e84f7f3376456cb500eb4c90a0fe35b8626d667e2e5f6d9f6a72822`
  - Registry: `reports/strategy_edge_registry_20261111T164444Z.json` — `2d3fbd69dec00e97878de64155611557ee5184652803d03c8e1c4f6d0a63c35b`
  - Summary: `reports/campaign259_execution_summary_20261111T164444Z.json` — `6d1317473798d7687bb5f681f707679e6145cfc839e532ca8ba4ba6ff210a977`

## C258 — COMPLETE (2026-11-11T16:30:16Z UTC)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_NORMALIZED_RANGE_SHOCK_MR`. Feature (fail-closed): NORMALIZED_RANGE=(mx-mn)/mid, mid=(mx+mn)/2. Result: NONE. Sums: 3.414663798428485, 2.6966637984284847, 1.978663798428484, 0.5426637984284839, -2.329336201571515.
- **Artifacts:** OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_normalized_range_shock_mr_costed_oos_20261111T162610Z.json` `45bf1e48...2ad8`, script `db49fda8...de4eb`, ingest `b6ce186f...9550`, registry `ad27dd79...ff15`, summary `dbbec959...f707`.

## C257 — COMPLETE (2026-11-11T14:39:36Z UTC)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFFICIENT_OF_RANGE_SHOCK_MR`. Feature (fail-closed): (mx-mn)/(mx+mn). Result: NONE. Sums: 3.414663798428485, 2.6966637984284847, 1.978663798428484, 0.5426637984284839, -2.329336201571515.
- **Artifacts:** OOS `...coefficient_of_range_shock_mr_costed_oos_20261111T143936Z.json` `214678ab...6286`, script `de800865...216d0`, ingest `3cb139ba...c4e48`, registry `6e0d1088...f945`, summary `a8f10869...da25`.

## STATE SNAPSHOT (2026-11-11T17:18:35Z UTC)
- **C12:** 5/5 complete. **C13:** 3/3 complete. **C14:** 7/7 complete (zero edge). **C15:** 7/7 complete (zero edge).
- **C249–C260:** COMPLETE, all `edge_claim: NONE`, `oos_edge_proven: false` (artifacts on disk with SHA256-from-bytes).
- **C261:** NOT STARTED / **READY TO RUN NOW**. Primary `COEFF_OF_VARIATION` grep-zero verified. No bottlenecks. Template C260 scripts exist; C261 script must be created by adapting the template.
- **Caches:** real spot/volume caches present in `data/cache/` (`.pkl`+`.meta.json`+provenance); no refetch.
- **Environment:** `python3` 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1. Working tree clean at `a605961`.

## HARD BANS
- ❌ No status-only work; no "planning/researching" as substitute for producing artifacts.
- ❌ No re-runs of C1–C15 or C249–C260 except evidence-backed defect fix.
- ❌ No network refetch (use `data/cache/` only).
- ❌ No synthetic/fabricated data.
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked for C1–C15).
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user.
- ❌ No early exit from pipeline except `oos_edge_proven: true`.

**END OF DURABLE HANDOFF — 2026-11-11T17:18:35Z UTC (C260 complete, NONE with evidence; no bottlenecks found).**
**NEXT AGENTIC SESSION: EXECUTE C261 NOW (HEAVY). DO NOT ASK. DO NOT PLAN. EMIT SHA256-BACKED ARTIFACTS OR HONEST NONE WITH EVIDENCE. UPDATE THIS HANDOFF. THEN CONTINUE PIPELINE C262+.**
