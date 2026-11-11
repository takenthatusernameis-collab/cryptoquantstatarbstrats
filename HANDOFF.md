# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` (crypto quant stat-arb strategies).
> **Core mission (non-negotiable):** real-data-only edge search with fail-closed enriched cointegration/gates. **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked`/`NONE` with evidence is valid. **Status-only work is forbidden.**
> **Single durable handoff:** `HANDOFF.md` (repo root) only. Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line is stale (`latest_campaign_done: C248`, `next_campaign: C249`; C249–C262 complete on disk). Must not be edited to block/replace C1–C15/C249+ progress. Sync only if explicitly requested by user.

## PRIORITIZED TIMESTAMPED INITIAL TASK MESSAGE (2026-11-11T18:21:24Z UTC) — START HERE, DO NOT DEVIATE

**PRIORITY 1 (HEAVY EXECUTION — MANDATORY):** Continue the proven main line for this repo (`cryptoquantstatarbstrats` = crypto quant stat-arb strategies): **real cached quote/volume RQA shock mean-reversion costed-OOS**, real-data-only edge search, fail-closed gates. Do **not** pivot to research, docs, refactors, or status summaries. Produce artifacts or honest `NONE` with evidence.

**IMMEDIATE NON-DEFERRABLE ACTION:** Run **Campaign #263** end-to-end now (C262 complete, `edge_claim: NONE`). No planning phase. No "explore first" substitution.

### Preflight (re-verified 2026-11-11T18:21:24Z UTC — path clear, no bottlenecks)
```bash
python3 -c "import numpy,pandas,scipy; print('ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION|WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION' scripts/ strategies/ backtest/ utils/ | wc -l  # must be 0 nonself
ls data/cache/*.pkl data/cache/*.meta.json | wc -l  # expect 66
git -C /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats status --short | head
```
- **Verified now:** deps OK (python3 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1); C263 primary distinctness grep = **0 nonself hits**; real caches present (`66` `.pkl`/`.meta.json` files in `data/cache/`); git tree clean. **No background/blocking bottlenecks found.** C262 artifacts complete on disk. C263 script does **not** yet exist — create by adapting the C262 template.
- If `python3`/deps missing → fix environment or state concrete blocker with evidence (do not downgrade to status-only).
- If grep returns >0 nonself hits → pick next grep-zero distinct fallback below (re-verify each), record evidence, proceed.
- If caches missing/provenance unclear → fail closed with evidence, do not refetch network.
- If a background process blocks disk/CPU → stop it.

### C263 Directive (execute, not plan)
- **Strategy ID:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION_SHOCK_MR` (primary; re-verify grep-zero before run).
- **Feature (state exact formula before coding; fail-closed):** Index of dispersion (variance-to-mean ratio) of lengths of qualifying **WHITE** diagonal segments (consecutive 0-cells/non-recurrent, length>=`w_min=2`) pooled over off-diagonal diagonals `k!=0`. Let `L={L_i}`, `N>=3`; `mu=mean(L)`, `sigma2_pop=(1/N)*sum((L_i-mu)^2)` (population variance, ddof=0). `INDEX_OF_DISPERSION = sigma2_pop / mu`. Fail-closed if `<3` qualifying segments, `mu`/`sigma2_pop` undefined/non-finite, `mu<=0` or `sigma2_pop<=0`, `INDEX_OF_DISPERSION<=0` or degenerate/non-finite, or any intermediate undefined/non-finite. Pre-state exact formula/reference in script docstring.
- **Distinctness gate:** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION|WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION' scripts/ strategies/ backtest/ utils/` must return **0 nonself hits** before run. If blocked, try in order (re-verify distinctness):
  1. `RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION` (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION|WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION`)
  2. `RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABSOLUTE_DEVIATION_FROM_MEDIAN_RATIO` (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDIAN_ABSOLUTE_DEVIATION_FROM_MEDIAN_RATIO|WHITE_DIAG_LINE_LENGTH_MEDIAN_ABSOLUTE_DEVIATION_FROM_MEDIAN_RATIO`)
  3. `RTE_OVER_WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE` (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE|WHITE_DIAG_LINE_LENGTH_RELATIVE_MEAN_ABSOLUTE_DIFFERENCE`)
  Record which one chosen + evidence and proceed (no status-only stop).
- **Template (do not reinvent):** `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_interdecile_range_shock_mr_costed_oos.py` (sha256 `bebe696026800e01b3a9a318513c1e4ee0524839ec4a1c063012ed63a1762e19`), prior registry `reports/strategy_edge_registry_20261111T181135Z.json` (sha256 `064e119d163d55c22917a639131bbc6fbef191e7f4d0cedfb930ca04f93085be`), prior OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_interdecile_range_shock_mr_costed_oos_20261111T180357Z.json` (sha256 `72a337ad8ff23570add956a7a2a7d77240ce546cd7bded8e4707a2b770c31717`).
- **Evaluation (locked):** real cached data only; WF `train=720/test=168/step=168`; costs `[[0,0],[5,5],[10,10],[20,20],[40,40]]`. No network refetch.
- **Edge rule (fail-closed):** `oos_edge_proven: true` **IFF** OOS exposure>0 **AND** for **ALL** cost slices OOS net sum > 0 **AND** mean OOS net > mean B&H OOS net on same WF windows (real data only). Otherwise `edge_claim: NONE` with evidence (`cross_asset_oos_net_sums`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, exposure).
- **Required outputs (SHA256 from bytes):** timestamped C263 costed-OOS artifact, run script, ingest attempt, strategy-edge-registry, campaign execution summary. Include C263 helper stems in own-campaign exclusions.

### Exact execution skeleton (repo root)
```bash
# 1) Preflight (re-verify distinctness)
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION|WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION' scripts/ strategies/ backtest/ utils/

# 2) Create/adapt script from C262 template
cp scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_interdecile_range_shock_mr_costed_oos.py \
   scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_index_of_dispersion_shock_mr_costed_oos.py
# edit: strategy_id, feature/formula + fail-closed (INDEX_OF_DISPERSION=sigma2_pop/mu),
#       grep strings, campaign=263,
#       prior registry -> reports/strategy_edge_registry_20261111T181135Z.json,
#       prior/C262 OOS sha, own_campaign exclusions, artifact naming

# 3) Heavy execution + emit
python3 scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_index_of_dispersion_shock_mr_costed_oos.py
python3 scripts/run_real_feed_ingest_attempt_263.py
python3 scripts/emit_campaign263_registry.py
python3 scripts/emit_campaign263_summary.py

# 4) Record SHA256-from-bytes for all 5 artifacts + update this HANDOFF.md
```
**Stop rule:** Stop early **only** if `oos_edge_proven: true`. Otherwise record honest `NONE`/blocked with full evidence and update this handoff (UTC timestamp, commands, artifact paths+SHA256s, conclusion, next directive). **Do not** edit `research_state/state.yaml` unless explicitly requested by user.

### UNINTERRUPTED PIPELINE (so future agents cannot avoid heavy work)
C262 complete (NONE with evidence). **Immediately** proceed in order:
- **C263 (now due):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION_SHOCK_MR` (grep-zero verified; re-verify at run)
- **C264 (if C263 NONE):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_DISPERSION_SHOCK_MR`
- **C265+:** continue enumerating grep-zero WHITE-diag line-length RQA variants in the same family (dispersion/shape/relative-spread forms not yet run). For each: distinctness gate 0 nonself, fail-closed formula pre-stated, same WF/costs, same edge rule, same required artifacts+SHA256, update handoff. Never re-run C1–C15/C249–C262 except evidence-backed defect fix.

## C262 — COMPLETE (2026-11-11T18:11:35Z UTC)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_INTERDECILE_RANGE_SHOCK_MR`. Feature (fail-closed): INTERDECILE_RANGE=p90(L)-p10(L) of lengths of qualifying WHITE diagonal segments (>=w_min=2, off-diagonal k!=0, m=2,tau=1,W_RR=168,eps=0.5*std,L_inf), N>=3, numpy percentile default linear interpolation (pre-stated fixed). Fail-closed if <3 segments, p10/p90 undefined/non-finite, INTERDECILE_RANGE<=0 or degenerate/non-finite, or any intermediate undefined/non-finite.
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: true`.
- **Evidence:** `cross_asset_oos_net_sums` fee0_slip0=0.5945201721473992, fee5_slip5=-0.1614798278526015, fee10_slip10=-0.9174798278526022, fee20_slip20=-2.429479827852602, fee40_slip40=-5.453479827852601.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_interdecile_range_shock_mr_costed_oos_20261111T180357Z.json` — `72a337ad8ff23570add956a7a2a7d77240ce546cd7bded8e4707a2b770c31717`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_interdecile_range_shock_mr_costed_oos.py` — `bebe696026800e01b3a9a318513c1e4ee0524839ec4a1c063012ed63a1762e19`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T181134Z.json` — `f65ea62599c0799b19782a7272847787cfc1d2a31e99a92eb68ee48ae2e7f351`
  - Registry: `reports/strategy_edge_registry_20261111T181135Z.json` — `064e119d163d55c22917a639131bbc6fbef191e7f4d0cedfb930ca04f93085be`
  - Summary: `reports/campaign262_execution_summary_20261111T181135Z.json` — `2f03d22149dbee855c1de05158be164516ba378be0ad7811ce76a3af1f0cb5ed`

## C261 — COMPLETE (2026-11-11T17:29:54Z UTC)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION_SHOCK_MR`. Feature (fail-closed): COEFF_OF_VARIATION=sigma_pop/mu of lengths of qualifying WHITE diagonal segments (>=w_min=2, off-diagonal k!=0), N>=3, sigma_pop=sqrt((1/N)*sum((L_i-mu)^2)) (ddof=0). Fail-closed if <3 segments, mu/sigma_pop undefined/non-finite, mu<=0 or sigma_pop<=0, COEFF_OF_VARIATION<=0/degenerate/non-finite.
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: true`.
- **Evidence:** `cross_asset_oos_net_sums` fee0_slip0=1.7166007102768368, fee5_slip5=0.772600710276836, fee10_slip10=-0.17139928972316476, fee20_slip20=-2.059399289723165, fee40_slip40=-5.835399289723164.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_coeff_of_variation_shock_mr_costed_oos_20261111T172954Z.json` — `04177b62907cf8bc40c0ad071633011c9b97951b02eff9ccaae161ba19d68d61`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_coeff_of_variation_shock_mr_costed_oos.py` — `380f16c482a07b1732f78785700b30894f78c4bdbf0f91c7e318f25ffe295b7b`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T173534Z.json` — `805335d6497dd53486f52ef0309d48fb14e9d064d01ee9b3b465c60c47eff911`
  - Registry: `reports/strategy_edge_registry_20261111T173535Z.json` — `7f27db8a79c91b473c893c5f74b501c1c64905e34fc0a8e7a70e202605a492e6`
  - Summary: `reports/campaign261_execution_summary_20261111T173613Z.json` — `48c96b73cb1dc7599fecf5e2874b654e4f806cccb24e4f96ef150347e8437b38`

## C260 — COMPLETE (2026-11-11T17:10:50Z UTC)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_VARIATION_SHOCK_MR`. Feature (fail-closed): PEARSON_VARIATION=(1/N)*sum_{i=1}^{N}(L_i-mu)^2 (population variance, ddof=0) of qualifying WHITE diagonal segment lengths (>=w_min=2, off-diagonal k!=0), N>=3. Fail-closed if <3 segments, mu/PEARSON_VARIATION undefined/non-finite, PEARSON_VARIATION<=0/degenerate/non-finite.
- **Result:** `edge_claim: NONE`, `oos_edge_proven: false`. `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: false`, `all_cost_slices_beat_bh_mean_rule: true`.
- **Evidence:** `cross_asset_oos_net_sums` fee0_slip0=2.4580778221231743, fee5_slip5=1.7780778221231737, fee10_slip10=1.098077822123173, fee20_slip20=-0.2619221778768269, fee40_slip40=-2.981922177876826.
- **Artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_variation_shock_mr_costed_oos_20261111T170631Z.json` — `9671ef3ddd6943fa5d6726bc355f3c85eb869837204e2b4fac9d1d6056d199dc`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_pearson_variation_shock_mr_costed_oos.py` — `571596b264f672619aa3349a74b485155afcc2cf464da226eeb7dfa4c9591bab`
  - Ingest: `reports/real_feed_ingest_attempt_20261111T170421Z.json` — `e5c1b34725e7a1ed6298fad1f1ab6d7df785274c1a29e1c813d8b825b8cd729b`
  - Registry: `reports/strategy_edge_registry_20261111T171038Z.json` — `e94e065ed8094fff2ac086fcf4a8bcfb5ecd9665974ded055a8ca2c319c26b18`
  - Summary: `reports/campaign260_execution_summary_20261111T171039Z.json` — `58d96f1274cd5896ee5f555ed047f93d2d5edf82fa657541a004c34637826946`

## STATE SNAPSHOT (2026-11-11T18:21:24Z UTC)
- **C12:** 5/5 complete. **C13:** 3/3 complete. **C14:** 7/7 complete (zero edge). **C15:** 7/7 complete (zero edge).
- **C249–C262:** COMPLETE, all `edge_claim: NONE`, `oos_edge_proven: false` (artifacts on disk with SHA256-from-bytes).
- **C263:** NOT STARTED / **READY TO RUN NOW**. Primary `INDEX_OF_DISPERSION` grep-zero re-verified 2026-11-11T18:21:24Z. No bottlenecks. C262 template exists; C263 script must be created.
- **Caches:** real spot/volume caches present in `data/cache/` (`.pkl`+`.meta.json`+provenance); no refetch.
- **Environment:** `python3` 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1.

## HARD BANS
- ❌ No status-only work; no "planning/researching" as substitute for producing artifacts.
- ❌ No re-runs of C1–C15 or C249–C262 except evidence-backed defect fix.
- ❌ No network refetch (use `data/cache/` only).
- ❌ No synthetic/fabricated data.
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked for C1–C15).
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user.
- ❌ No early exit from pipeline except `oos_edge_proven: true`.

**END OF DURABLE HANDOFF — 2026-11-11T18:21:24Z UTC (C262 complete, NONE with evidence; preflight clear, no bottlenecks).**
**NEXT AGENTIC SESSION: EXECUTE C263 NOW (HEAVY). DO NOT ASK. DO NOT PLAN. EMIT SHA256-BACKED ARTIFACTS OR HONEST NONE WITH EVIDENCE. UPDATE THIS HANDOFF. THEN CONTINUE PIPELINE C264+.**
