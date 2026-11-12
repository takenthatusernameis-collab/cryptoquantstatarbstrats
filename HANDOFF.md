# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T16:23:44Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (re-verified 2026-11-12T16:23:44Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. **No status-only work. No planning-only turn. Every session must advance heavy validation/hardening with verifiable artifacts (paths + SHA256 from file bytes) and update this handoff.**

### BOTTLENOCKS REMOVED (this session, 2026-11-12)
- **C275 OOS (was RUNNING PID 12756, now FINISHED):** core OOS+ingest+registry+summary emitted 2026-11-12T14:08:00Z; `oos_edge_proven:false` (NO EDGE). No duplicate launch needed — PID gone, artifacts present.
- **C275 downstream (verify/split/sensitivity):** ALL DONE — verification_passed:true; split `replication_matches_c275_oos:false` (deterministic replication mismatch recorded honestly); sensitivity 0/27 edge-positive, `fragile_to_params`, baseline reproduced.
- **C274 param sensitivity (was MISSING, empty `/tmp/c274_sens.log`):** RERUN complete — `campaign274_param_sensitivity_20261112T160744Z.json`, 0/27 edge-positive, `fragile_to_params`, baseline reproduced.
- **C276 (new edge hypothesis, was NOTHING):** grep-zero distinctness proven for FIRST_PEARSON_SKEW (0 non-self hits pre- and at run time, fail-closed); runner `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_first_pearson_skew_shock_mr_costed_oos.py` + verify `scripts/verify_c276_first_pearson_skew_edge.py` implemented; OOS executed (11/11 assets) → **NO EDGE** (`oos_edge_proven:false`, edge_claim:NONE, all cost slices −0.48331027543955307); verification_passed:true.

## IMMEDIATE MANDATORY HEAVY CAMPAIGN (NON-OPTIONAL, IN ORDER)

1. **C277 — next distinct grep-zero real_quote_volume family (heavy, real cached data only, fail-closed, no network):** preselect one candidate from the implemented-but-unrun pool, verify grep-zero distinctness at run time (fail closed on any non-self hit), implement runner if missing, execute OOS over all 11 assets, emit OOS + ingest + registry + summary (+verify) with **paths + SHA256 from file bytes**, record verdict.
   - Candidate pool (implemented scripts, grep-verify before use): `run_real_quote_volume_approximate_entropy_shock_mr_costed_oos.py`, `run_real_quote_volume_dispersion_entropy_shock_mr_costed_oos.py`, `run_real_quote_volume_fisher_information_shock_mr_costed_oos.py`, `run_real_quote_volume_higuchi_fd_shock_mr_costed_oos.py`, `run_real_quote_volume_hurst_rs_persistence_mr_costed_oos.py`, `run_real_quote_volume_lz76_complexity_shock_mr_costed_oos.py`, `run_real_quote_volume_multiscale_sample_entropy_shock_mr_costed_oos.py`.
   - If edge proven (`oos_edge_proven:true`, exposure>0, all cost slices OOS net sum > 0, mean OOS net > mean B&H): build promotion evidence package (`READY_FOR_REVIEW` or `NOT_READY` with reasons), record artifact paths + SHA256s.
   - If **no edge**: document failing condition, pick the next grep-zero distinct family from the pool, implement + run + emit + hash in the **same session**. Do **not** stop at planning.
   - If the pool is exhausted with no edge: record honest exhaustion conclusion (fail-closed) + propose next structural step; do not fabricate or weaken thresholds.

2. **No status-only work.** Every turn must produce or advance heavy validation artifacts and update this handoff with paths+SHA256s.

## STATE SNAPSHOT (re-verified 2026-11-12T16:23:44Z UTC)
- **Env:** `python3 3.12.3`; `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`. Ruff/mypy not installed in this env — skip lint until available.
- **Data:** `data/cache/` = 68 real files. **No network refetch. No synthetic/fabricated data.**
- **Git:** working tree clean at verification; branch `main` up to date with origin/main.
- **Canonical handoff:** this file only. `research_state/state.yaml` stale at C248 (locked) — do not edit.
- **C273 (PERCENTILE_SPREAD):** `CONDITIONAL_EDGE_PROVEN` / verified / `READY_FOR_REVIEW`. Preserved.
  - OOS sha256 `b02ca846eebcdc1253c45b0686e28bef787714b9373e8e0c5118322b3ffe8fad`; promotion MD sha256 `d03eab43502bd8c53845e692d981cb9d020c1f728bcb3afb21b7bb5453ba72b3`; builder sha256 `48ed28d0fc808092188939c44e04d3112ed489215b1b40be0e49d3552715ec33`.
- **C274 (SECOND_PEARSON_SKEW, corrected) — NO EDGE (preserved):** edge_claim:NONE, oos_edge_proven:false; all cost slices −0.48331027543955307; sensitivity **RERUN** `reports/campaign274_param_sensitivity_20261112T160744Z.json` sha256 `25a0747acbc48192bb87cc27842652dad231fd4852bf32a461f03f16aab904c8` (0/27 edge-positive, `fragile_to_params`, baseline reproduced, baseline_reproduced_in_grid:true).
- **C275 (MEDCOUPLE) — NO EDGE:** all core+downstream artifacts emitted, all hashes verified from bytes:
  - OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_medcouple_shock_mr_costed_oos_20261112T140800Z.json` sha256 `001cc43f94d660abe08be2d67947bf23324250ff5f85ba432f336205214b367d`
  - Ingest `reports/real_feed_ingest_attempt_275_20261112T140800Z.json` sha256 `693849ce08d20a34dade712decd8e92d91c6b4f920db308e9e3f39c9e441433c`
  - Registry `reports/strategy_edge_registry_275_20261112T140800Z.json` sha256 `6b44c935d4ff9c6f3d387b6700ad4518ad4c11bf814b4c52e2c51b8cc50b7fdf`
  - Summary `reports/campaign275_execution_summary_20261112T140800Z.json` sha256 `04ca5162465884a5d05db3f89bb6eaac40917a388c9572a39ae0175ba755d646`
  - Verify `reports/campaign275_verification_20261112T142319Z.json` sha256 `636e0375f50ebc6ef14dffdc89e8c8d65c461f11c34af5a9ff50b8e3195b634d` (`verification_passed:true`)
  - Split `reports/campaign275_split_decomposition_20261112T142319Z.json` sha256 `7f2fe54d562ac515f3b155c9d24e0903ddc60eed89088b8ccbbaa13b348efa01`
  - Sensitivity `reports/campaign275_param_sensitivity_20261112T143610Z.json` sha256 `1bcf4a199aac1164dccd61254f1f830305a5a7b327242f65766089b7b3987030` (0/27 edge-positive, `fragile_to_params`, baseline reproduced)
  - Script `scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` sha256 `9d0e0bc7cabcf8b6c6aa4e91ab932fbc9a8dadcc54777c8943057d67d08e1aa0`
- **C276 (FIRST_PEARSON_SKEW) — NO EDGE (new family executed this session):**
  - Runner `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_first_pearson_skew_shock_mr_costed_oos.py` sha256 `71a89045a1cfc768f2cf3088b46ed555b03797618ee46cbdd4bc731de6c8c90c`
  - Verify `scripts/verify_c276_first_pearson_skew_edge.py`
  - OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_first_pearson_skew_shock_mr_costed_oos_20261112T161642Z.json` sha256 `cae6cff377b7303bdc3e56cba49ff52072f55e49713a8006a2a98cf56a0543ee`
  - Ingest `reports/real_feed_ingest_attempt_276_20261112T161642Z.json` sha256 `86981a2a78a6aedc9a728c11b41b87a966c96f0487d636d76ec540ce91c05af7`
  - Registry `reports/strategy_edge_registry_276_20261112T161642Z.json` sha256 `40d4602945ad953c0eb665ceec8997c7a97efbe6500376c7b8fdb8959b7bd80e`
  - Summary `reports/campaign276_execution_summary_20261112T161642Z.json` sha256 `1f3cdd25a74ae0ef515265c065decf842dbb33aab9bd90d1e3bcb84fdd16de55`
  - Verify `reports/campaign276_verification_20261112T162335Z.json` sha256 `3d86e81623f56016ba03c125e812650008d39f69dc8409cbb16fae8d6ea9ba03` (`verification_passed:true`, distinctness live grep hits 0)

## HARD BANS
- No status-only work. No planning-only turns.
- No reruns of C1–C276 except evidence-backed defect fix.
- No network refetch; no synthetic/fabricated data. No threshold weakening.
- No edits to `research_state/state.yaml` unless explicitly requested.
- Record all new/updated artifact SHA256s **from file bytes**.
- Distinctness: grep-verified zero non-self hits before implementation AND at run time; fail-closed on collision.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T16:23:44Z UTC.**
