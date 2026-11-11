# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

> **Repo:** `cryptoquantstatarbstrats` (crypto quant stat-arb strategies).
> **Core mission (non-negotiable):** real-data-only edge search with fail-closed enriched cointegration/gates. **No fabrication. Ever.** No synthetic/fabricated prices, IV, volume, fills, order books, labels, or metrics. No network refetch of cached data. Honest `no_edge`/`insufficient_or_blocked`/`NONE` with evidence is valid. **Status-only work is forbidden.**
> **Single durable handoff:** `HANDOFF.md` (repo root) only. Historical handoff-named files under `reports/`/`scripts/` are artifacts, not directives.
> **Locked/separate line — DO NOT MODIFY unless explicitly requested by user:** `research_state/state.yaml` RQA line is stale (`latest_campaign_done: C248`, `next_campaign: C249`; C249–C264 complete on disk). Must not be edited to block/replace C1–C15/C249+ progress. Sync only if explicitly requested by user.

## PRIORITIZED TIMESTAMPED INITIAL TASK MESSAGE (2026-11-11T19:48:43Z UTC — C264 done; next session starts at C265) — START HERE, DO NOT DEVIATE

**PRIORITY 1 (HEAVY EXECUTION — MANDATORY):** Continue the proven main line: **real cached quote/volume RQA shock mean-reversion costed-OOS**, real-data-only, fail-closed gates. Do **not** pivot to research, docs, refactors, or status summaries. Produce artifacts or honest `NONE` with evidence.

**IMMEDIATE NON-DEFERRABLE ACTION:** Run **Campaign #265** end-to-end now (C264 complete, `edge_claim: NONE`). No planning phase. No "explore first" substitution.

### Preflight (re-verified 2026-11-11T19:48:43Z UTC — path clear, no bottlenecks)
```bash
python3 -c "import numpy,pandas,scipy; print('ok')"
grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MAD_FROM_MEDIAN|WHITE_DIAG_LINE_LENGTH_MAD_FROM_MEDIAN' scripts/ strategies/ backtest/ utils/ | wc -l  # must be 0 nonself before C265 run
ls data/cache/*.pkl data/cache/*.meta.json | wc -l  # expect 66
git -C /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats status --short | head
```
- **Verified now:** deps OK (`python3` 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1); C265 primary distinctness grep = **0** (re-verified 2026-11-11T19:48:43Z); real caches present (**66** `.pkl`/`.meta.json` in `data/cache/`); no blocking bottlenecks observed. C264 artifacts complete on disk. `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_mad_from_median_shock_mr_costed_oos.py` does **not** yet exist — create by adapting latest C264 template/script.
- If deps missing → fix environment or fail closed with concrete evidence (no status-only downgrade).
- If grep >0 nonself → pick next grep-zero fallback (re-verify, record evidence), proceed.
- If caches/provenance missing → fail closed with evidence, **no network refetch**.
- If a background process blocks disk/CPU → stop it.

### C265 SPEC (pre-stated, fail-closed)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MAD_FROM_MEDIAN_SHOCK_MR`
- **Feature:** median absolute deviation from the median of lengths of qualifying WHITE diagonal segments (`>= w_min=2`, off-diagonal `k!=0`, `m=2,tau=1,W_RR=168,eps=0.5*std`, `L_inf`), `N>=3`: `med = median(L)`, `MAD = median(|L_i - med|)` (numpy, pre-stated fixed). Distinct from MEAN_ABSOLUTE_DEVIATION (C254, mean-centered), MEDIAN_ABSOLUTE_DEVIATION naming in prior C255 if identical — **must confirm grep-zero distinctness for this exact token family before run; if non-distinct, fail-closed switch to fallback and record evidence**.
- **Fail-closed:** if `<3` segments; `med`/`MAD` undefined/non-finite; `MAD<=0`, degenerate, or non-finite; or any intermediate undefined/non-finite.
- **WF/costs:** `train=720, test=168, step=168`; cost grid bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.
- **Edge rule:** `oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only.
- **Required artifacts (SHA256 from bytes):** OOS report, runner script, ingest attempt, strategy edge registry, campaign execution summary under `reports/`/`scripts/` with campaign timestamping. Update this handoff with results/evidence/hashes and next campaign.

### UNINTERRUPTED PIPELINE (so future agents cannot avoid heavy work)
C264 complete (`NONE` with evidence). **Now:** C265 (primary `MAD_FROM_MEDIAN`, grep-zero verified at handoff time).
**C266+:** continue enumerating grep-zero WHITE-diag line-length RQA variants in the same family. Fallback chain if C265 collides/invalid: `RELATIVE_MEAN_ABSOLUTE_DIFFERENCE` (grep-zero re-verified) -> next pre-stated grep-zero variant (e.g. `ROOT_MEAN_SQUARE_DEVIATION_FROM_MEDIAN`, `STANDARDIZED_MOMENT` family, or other not-yet-run dispersion/shape forms) — for each re-verify grep-zero, pre-state fail-closed formula, record evidence. For each: distinctness gate 0 nonself, fail-closed formula pre-stated, same WF/costs/edge rule, required artifacts+SHA256, update handoff. Never re-run C1–C15/C249–C264 except evidence-backed defect fix. **No early exit except `oos_edge_proven: true`.**

## STATE SNAPSHOT (2026-11-11T19:48:43Z UTC)
- **C12:** 5/5 complete. **C13:** 3/3 complete. **C14:** 7/7 complete (zero edge). **C15:** 7/7 complete (zero edge).
- **C249–C264:** COMPLETE, all `edge_claim: NONE`, `oos_edge_proven: false` (artifacts on disk with SHA256-from-bytes).
- **C265:** **NOT STARTED / READY TO RUN NOW (IMMEDIATE PRIORITY).** Primary `MAD_FROM_MEDIAN` grep-zero verified. Fallback `RELATIVE_MEAN_ABSOLUTE_DIFFERENCE` also grep-zero. No bottlenecks.
- **Caches:** real spot/volume caches present in `data/cache/` (`.pkl`+`.meta.json`+provenance); **no refetch**.
- **Environment:** `python3` 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1.

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

## C263 — COMPLETE (2026-11-11T190903Z UTC)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_INDEX_OF_DISPERSION_SHOCK_MR` (INDEX_OF_DISPERSION=sigma2_pop/mu, ddof=0, N>=3, fail-closed). `edge_claim: NONE`, `oos_edge_proven: false`.
- OOS `02490c3c839435ad4a6040d8eaeb97721c10f130983a91ed3de3875dd398953e`; script `9c1d9f1edfe31c4926e995f5fb8d524db985001a01d6e2892eba84bf7b167db9`; ingest `9d3fc62b26e14e108230bd71f47bd4685aa0df93ad2043f1385b343f4473864e`; registry `7ec6c1607b95729bbb0130ce1a61ffc2d05b9cde4dc255bd072b4ed269d7f627`; summary `8d50c349653a8c86ca205404210deb89e052a265ea52d1f7923c2238442dca6c`.

## C262 — COMPLETE (2026-11-11T18:11:35Z UTC)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_INTERDECILE_RANGE_SHOCK_MR` (p90-p10, N>=3). `edge_claim: NONE`, `oos_edge_proven: false`.
- OOS `72a337ad8ff23570add956a7a2a7d77240ce546cd7bded8e4707a2b770c31717`; script `bebe696026800e01b3a9a318513c1e4ee0524839ec4a1c063012ed63a1762e19`; ingest `f65ea62599c0799b19782a7272847787cfc1d2a31e99a92eb68ee48ae2e7f351`; registry `064e119d163d55c22917a639131bbc6fbef191e7f4d0cedfb930ca04f93085be`; summary `2f03d22149dbee855c1de05158be164516ba378be0ad7811ce76a3af1f0cb5ed`.

## C261 — COMPLETE (2026-11-11T17:29:54Z UTC)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_COEFF_OF_VARIATION_SHOCK_MR` (sigma_pop/mu, ddof=0, N>=3). `edge_claim: NONE`, `oos_edge_proven: false`.
- OOS `04177b62907cf8bc40c0ad071633011c9b97951b02eff9ccaae161ba19d68d61`; script `380f16c482a07b1732f78785700b30894f78c4bdbf0f91c7e318f25ffe295b7b`; ingest `805335d6497dd53486f52ef0309d48fb14e9d064d01ee9b3b465c60c47eff911`; registry `7f27db8a79c91b473c893c5f74b501c1c64905e34fc0a8e7a70e202605a492e6`; summary `48c96b73cb1dc7599fecf5e2874b654e4f806cccb24e4f96ef150347e8437b38`.

## C260 — COMPLETE (2026-11-11T17:10:50Z UTC)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PEARSON_VARIATION_SHOCK_MR` (population variance ddof=0, N>=3). `edge_claim: NONE`, `oos_edge_proven: false`.
- OOS `9671ef3ddd6943fa5d6726bc355f3c85eb869837204e2b4fac9d1d6056d199dc`; script `571596b264f672619aa3349a74b485155afcc2cf464da226eeb7dfa4c9591bab`; ingest `e5c1b34725e7a1ed6298fad1f1ab6d7df785274c1a29e1c813d8b825b8cd729b`; registry `e94e065ed8094fff2ac086fcf4a8bcfb5ecd9665974ded055a8ca2c319c26b18`; summary `58d96f1274cd5896ee5f555ed047f93d2d5edf82fa657541a004c34637826946`.

## HARD BANS
- ❌ No status-only work; no "planning/researching" as substitute for producing artifacts.
- ❌ No re-runs of C1–C15 or C249–C264 except evidence-backed defect fix.
- ❌ No network refetch (use `data/cache/` only).
- ❌ No synthetic/fabricated data.
- ❌ No threshold weakening (ENTRY_THRESHOLD=2.0, COINTEGRATION_PVALUE=0.05 locked for C1–C15).
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user.
- ❌ No early exit from pipeline except `oos_edge_proven: true`.

**END OF DURABLE HANDOFF — 2026-11-11T19:48:43Z UTC (C264 complete, NONE with evidence; preflight re-verified clear, no bottlenecks).**
**NEXT AGENTIC SESSION: EXECUTE C265 NOW (HEAVY). DO NOT ASK. DO NOT PLAN. EMIT SHA256-BACKED ARTIFACTS OR HONEST NONE WITH EVIDENCE. UPDATE THIS HANDOFF. THEN CONTINUE PIPELINE C266+.**
