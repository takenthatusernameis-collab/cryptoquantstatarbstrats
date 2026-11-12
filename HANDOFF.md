# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T13:57:31Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (re-verified 2026-11-12T13:57:31Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 preserved (`promotion_readiness: READY_FOR_REVIEW`). C274 corrected = **NO EDGE** (preserved). **No status-only work.**

### BOTTLENECKS REMOVED / HEAVY WORK STATUS (verified 2026-11-12T13:57:31Z)
- **C274 param sensitivity: BLOCKED/FAILED (must rerun).** Prior PID 7673 exited; `/tmp/c274_sens.log` is empty (0 bytes) and `reports/campaign274_param_sensitivity_*` **MISSING**. Script present/hashed: `scripts/run_c274_second_pearson_skew_param_sensitivity.py` sha256 `75d7d6d12a341af7597d630e3b75bda3405f84a2dc3a33ddd063f110e827da3a`. **Action:** diagnose silent failure (check exit code/logging/disk/oom if evidence available), fix only evidenced defect, then rerun `python3 scripts/run_c274_second_pearson_skew_param_sensitivity.py` (capture stdout/stderr to a log) and record emitted artifact path + SHA256-from-bytes.
- **C275 OOS: RUNNING (heavy, do not duplicate).** PID **8269** (`python3 scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py`, started ~13:04Z, ~99% CPU observed). `/tmp/c275_oos.log` tail shows `done ADA`, `done AVAX`, `done BNB` (28 bytes total) as of 13:57Z. Expected artifacts still **MISSING**: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_medcouple_shock_mr_costed_oos_*.json`, `reports/real_feed_ingest_attempt_275_*.json`, `reports/strategy_edge_registry_275_*.json`, `reports/campaign275_execution_summary_*.json`. Script sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9`.
- **C275 downstream scripts IMPLEMENTED/ready (grep-zero distinctness preserved):** `scripts/verify_c275_medcouple_edge.py` sha256 `282ba827b4b7857fda9b7fb76c68293f16cd9ea1b58267b57bb3d66ada960e50`; `scripts/run_c275_medcouple_split_decomposition.py` sha256 `9bac5d1e76488d21e7e0ccd1c470a241e9d46f60bbd0d0b5c5d11bb9ae29ae9d`; `scripts/run_c275_medcouple_param_sensitivity.py` sha256 `02be7056f65f84c256c4f522d3e9a9fb92bb83afb6a2a219ad0080ecaa3b8aca`. Run only after C275 OOS+core artifacts exist.

## IMMEDIATE MANDATORY HEAVY CAMPAIGN (NON-OPTIONAL, IN ORDER)
1. **Monitor/finalize C275 OOS (heavy):** wait for PID 8269 to exit; confirm `/tmp/c275_oos.log` and `reports/` contain emitted C275 OOS, ingest-275, registry-275, summary-275. Record each path + **SHA256 computed from file bytes**. If it fails, diagnose evidenced defect, fix minimally, and rerun.
2. **Run C275 downstream immediately after C275 core artifacts exist (heavy, real cached data only, fail-closed, no network):**
   - `python3 scripts/verify_c275_medcouple_edge.py` → `reports/campaign275_verification_*.json` path+SHA256
   - `python3 scripts/run_c275_medcouple_split_decomposition.py` → `reports/campaign275_split_decomposition_*.json` path+SHA256
   - `python3 scripts/run_c275_medcouple_param_sensitivity.py` → `reports/campaign275_param_sensitivity_*.json` path+SHA256
3. **Rerun C274 param sensitivity (heavy, unblock missing evidence):** `python3 scripts/run_c274_second_pearson_skew_param_sensitivity.py` (after diagnosing empty-log failure; avoid CPU contention with C275 if still running). Record `reports/campaign274_param_sensitivity_*.json` path+SHA256.
4. **Post-C275 honest edge decision + action (must produce artifacts):**
   - If edge proven (`oos_edge_proven:true`, exposure>0, all cost slices OOS net sum > 0, mean OOS net > mean B&H on same WF windows): build promotion evidence package with full provenance (`READY_FOR_REVIEW` or `NOT_READY` with reasons) and record artifact paths+SHA256s.
   - If **no edge**: document concrete failing condition; **identify and prove grep-zero distinctness** for C276 (new hypothesis/feature family), implement C276 runner(s), and **begin execution** to emit C276 OOS+core artifacts with SHA256s in the same session. Do **not** stop at planning.
5. **No status-only work.** No planning-only turn. Every session must advance heavy validation/hardening with verifiable artifacts and update this handoff with paths+SHA256s.

## STATE SNAPSHOT (re-verified 2026-11-12T13:57:31Z UTC)
- **Env:** `python3 3.12.3` (confirmed). Deps previously verified `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`.
- **Data:** `data/cache/` = **68 real files**. **No network refetch. No synthetic/fabricated data.**
- **Git:** working tree clean at verification (only handoff update in progress).
- **Canonical handoff:** this file only. `research_state/state.yaml` stale at C248 (locked).
- **C273 (PERCENTILE_SPREAD):** `CONDITIONAL_EDGE_PROVEN` / verified / replication-matched / split-decomposed / param sensitivity `robust_neighborhood` (21/27). Promotion `READY_FOR_REVIEW`. Preserved.
  - OOS sha256 `b02ca846eebcdc1253c45b0686e28bef787714b9373e8e0c5118322b3ffe8fad`; promotion MD sha256 `d03eab43502bd8c53845e692d981cb9d020c1f728bcb3afb21b7bb5453ba72b3`; builder sha256 `48ed28d0fc808092188939c44e04d3112ed489215b1b40be0e49d3552715ec33`.
- **C274 (SECOND_PEARSON_SKEW, corrected) — NO EDGE (preserved):** `edge_claim:NONE`, `oos_edge_proven:false`, `any_exposure_oos:false`, all cost slices positive OOS net sum false, all beat-B&H mean rule false, cross-asset OOS net sums all 0 (11 assets). Do not weaken thresholds. Superseded buggy `20261112T055039Z` artifacts must not be cited.
  - OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_second_pearson_skew_shock_mr_costed_oos_20261112T061632Z.json` sha256 `57b86c398b4ae041c0ada5c77f6cf3ba3b235a9f12d891921f84a7e41f580669`
  - Ingest `reports/real_feed_ingest_attempt_274_20261112T061632Z.json` sha256 `66ef3ced7ea6392ea77a0373e0d850a9405a6d0bb866be2830d59a3ab10dabce`
  - Registry `reports/strategy_edge_registry_274_20261112T061632Z.json` sha256 `d05229dcdfbe31036019ddb2903f10393ce12a1cab01178ac05029a2f755b846`
  - Summary `reports/campaign274_execution_summary_20261112T061632Z.json` sha256 `d66b2f5db020ac106081db3dc36a5db15b0ee35f742a634a59295c21c3a2c68d`
  - Verify `reports/campaign274_verification_20261112T062244Z.json` sha256 `1cff4cf55dddc058556e61dc6ab12186ceea6febe17a094cfe5082ef68e76826` (`verification_passed:true, internal_consistency_passed:true, edge_rule_satisfied:false`)
  - Split `reports/campaign274_split_decomposition_20261112T062431Z.json` sha256 `61b3d6e7a16d35f6536d924b1ab693223f458433b05c196e2b23b4d79d73ea9e`
  - Param sensitivity: **ARTIFACT MISSING — MUST RERUN** (prior run exited, `/tmp/c274_sens.log` empty).
- **C275 (MEDCOUPLE):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR` (`RTE/WHITE_DIAG_LINE_LENGTH_MEDCOUPLE`), grep-zero by design + runtime fail-closed. **OOS running PID 8269**; core/downstream artifacts MISSING as of 13:57Z.

## VERIFIED-BY-THIS-SESSION BLOCK (2026-11-12T13:57:31Z UTC)
- **Processes:** C275 PID **8269 RUNNING** (~52m CPU time observed); `/tmp/c275_oos.log` tail: `done ADA`, `done AVAX`, `done BNB`. No C274 sensitivity process running. No other relevant workers.
- **Artifacts:** no `reports/campaign274_param_sensitivity_*`; no C275 OOS/ingest/registry/summary/verify/split/sensitivity artifacts. Preserved C274 corrected + C273 evidence present and hashes consistent above.
- **Scripts (SHA256):** C274 sens `75d7d6d...da3a`; C275 OOS `8ce8fd...c9d9`; C275 verify `282ba8...0e50`; C275 split `9bac5d...9e9d`; C275 sens `02be70...8aca`.
- **Data/env/git:** `data/cache/` 68 files; `python3 3.12.3`; git clean at verification. No refetch.
- **Bottlenecks addressed:** stale handoff timestamp/state refreshed; C275 in-progress state confirmed; C274 missing-artifact blocker made explicit with mandatory rerun; downstream/next-edge actions fully specified with required artifact+hash recording.

## HARD BANS
- No status-only work. No reruns of C1–C274 except evidence-backed defect fix.
- No network refetch; no synthetic/fabricated data. No threshold weakening.
- No edits to `research_state/state.yaml` unless explicitly requested.
- Record all new/updated artifact SHA256s **from file bytes**.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T13:57:31Z UTC.**
