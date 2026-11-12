# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T13:02:31Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (re-verified 2026-11-12T13:02:31Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 preserved (`promotion_readiness: READY_FOR_REVIEW`). C274 corrected = **NO EDGE** (preserved). **No status-only work.**

### BOTTLENECKS REMOVED / HEAVY WORK IN FLIGHT (verified 2026-11-12T13:02:31Z)
- **C274 param sensitivity RUNNING (verified):** PID **7673** (`python3 scripts/run_c274_second_pearson_skew_param_sensitivity.py`, ppid chain 7672/7671, started ~12:46Z). Script sha256 `75d7d6d12a341af7597d630e3b75bda3405f84a2dc3a33ddd063f110e827da3a`. Expected artifact: `reports/campaign274_param_sensitivity_*.json` (**MISSING as of 13:02:31Z**).
- **C275 OOS RUNNING (verified, restarted this session):** PID **8269** (`python3 scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py`, ppid 8268, started ~13:02Z), log `/tmp/c275_oos.log`. Script sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9`. Expected artifacts (**all MISSING as of 13:02:31Z**): `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_medcouple_shock_mr_costed_oos_*.json`, `reports/real_feed_ingest_attempt_275_*.json`, `reports/strategy_edge_registry_275_*.json`, `reports/campaign275_execution_summary_*.json`.
- **C275 downstream scripts IMPLEMENTED and ready (grep-zero distinctness preserved):**
  - `scripts/verify_c275_medcouple_edge.py` sha256 `282ba827b4b7857fda9b7fb76c68293f16cd9ea1b58267b57bb3d66ada960e50`
  - `scripts/run_c275_medcouple_split_decomposition.py` sha256 `9bac5d1e76488d21e7e0ccd1c470a241e9d46f60bbd0d0b5c5d11bb9ae29ae9d`
  - `scripts/run_c275_medcouple_param_sensitivity.py` sha256 `02be7056f65f84c256c4f522d3e9a9fb92bb83afb6a2a219ad0080ecaa3b8aca`

## IMMEDIATE MANDATORY HEAVY CAMPAIGN FOR NEXT SESSION (NON-OPTIONAL, IN ORDER)

1. **Finalize C274 param sensitivity (heavy):** confirm PID 7673 chain completed and `/tmp/c274_sens.log`/process exit indicate success. Locate `reports/campaign274_param_sensitivity_*.json`, record full path + **SHA256 computed from file bytes** in this handoff. If failed, diagnose from logs/artifacts and fix only with evidence, then rerun (only allowed rerun for evidenced defect).
2. **Finalize C275 OOS (heavy):** confirm PID 8269 completed and `/tmp/c275_oos.log` shows emitted artifacts. Record paths + **SHA256-from-bytes** for: OOS, ingest-275, registry-275, summary-275. If failed, fix evidenced defect and rerun.
3. **Run C275 downstream immediately after C275 OOS artifacts exist (heavy, real cached data only, fail-closed, no network):**
   - `python3 scripts/verify_c275_medcouple_edge.py` → record `reports/campaign275_verification_*.json` path+SHA256
   - `python3 scripts/run_c275_medcouple_split_decomposition.py` → record `reports/campaign275_split_decomposition_*.json` path+SHA256
   - `python3 scripts/run_c275_medcouple_param_sensitivity.py` → record `reports/campaign275_param_sensitivity_*.json` path+SHA256
4. **Post-C275 honest edge decision + action (must produce artifacts):**
   - If edge proven by rule (`oos_edge_proven:true` with exposure>0, all cost slices OOS net sum > 0, mean OOS net > mean B&H on same WF windows): build promotion evidence package with full provenance (mark `READY_FOR_REVIEW` or `NOT_READY` with reasons) and record artifact paths+SHA256s.
   - If **no edge**: document concrete failing condition, **identify and prove grep-zero distinctness** for C276 (new hypothesis/feature family), implement C276 runner(s), and **begin execution** to emit C276 OOS+core artifacts with SHA256s in the same session. Do **not** stop at planning.
5. **No status-only work.** No planning-only turn. Every session must advance heavy validation/hardening with verifiable artifacts.

## STATE SNAPSHOT (re-verified 2026-11-12T13:02:31Z UTC)
- **Env:** `python3 3.12.3`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1` (per prior verified state; no reinstall).
- **Data:** `data/cache/` = **68 real files** (spot/volume/meta/provenance set). **No network refetch. No synthetic/fabricated data.**
- **Git:** working tree clean at verification time (`git status --short` empty).
- **Canonical handoff:** this file only. `research_state/state.yaml` stale at C248 (locked; do not edit unless explicitly requested).
- **C1–C15, C249–C272:** complete, `oos_edge_proven:false`.
- **C273 (PERCENTILE_SPREAD):** `CONDITIONAL_EDGE_PROVEN` / verified / replication-matched / split-decomposed / param sensitivity `robust_neighborhood` (21/27). Promotion `READY_FOR_REVIEW`. **Preserved/unchanged.**
  - OOS JSON sha256 `b02ca846eebcdc1253c45b0686e28bef787714b9373e8e0c5118322b3ffe8fad`
  - Promotion MD sha256 `d03eab43502bd8c53845e692d981cb9d020c1f728bcb3afb21b7bb5453ba72b3`
  - Builder sha256 `48ed28d0fc808092188939c44e04d3112ed489215b1b40be0e49d3552715ec33`
- **C274 (SECOND_PEARSON_SKEW, corrected 2026-11-12T06:16:32Z) — NO EDGE (preserved):** `edge_claim:NONE`, `oos_edge_proven:false`, `any_exposure_oos:false`, all cost slices positive OOS net sum false, all cost slices beat B&H mean rule false, cross-asset OOS net sums all 0 (11 assets). **Do not weaken thresholds.** Superseded buggy `20261112T055039Z` artifacts must not be cited.
  - OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_second_pearson_skew_shock_mr_costed_oos_20261112T061632Z.json` sha256 `57b86c398b4ae041c0ada5c77f6cf3ba3b235a9f12d891921f84a7e41f580669`
  - Ingest `reports/real_feed_ingest_attempt_274_20261112T061632Z.json` sha256 `66ef3ced7ea6392ea77a0373e0d850a9405a6d0bb866be2830d59a3ab10dabce`
  - Registry `reports/strategy_edge_registry_274_20261112T061632Z.json` sha256 `d05229dcdfbe31036019ddb2903f10393ce12a1cab01178ac05029a2f755b846`
  - Summary `reports/campaign274_execution_summary_20261112T061632Z.json` sha256 `d66b2f5db020ac106081db3dc36a5db15b0ee35f742a634a59295c21c3a2c68d`
  - Verify `reports/campaign274_verification_20261112T062244Z.json` sha256 `1cff4cf55dddc058556e61dc6ab12186ceea6febe17a094cfe5082ef68e76826` (`verification_passed:true, internal_consistency_passed:true, edge_rule_satisfied:false`)
  - Split `reports/campaign274_split_decomposition_20261112T062431Z.json` sha256 `61b3d6e7a16d35f6536d924b1ab693223f458433b05c196e2b23b4d79d73ea9e`
  - Param sensitivity: **RUNNING (PID 7673)** — artifact `reports/campaign274_param_sensitivity_*.json` **MISSING** as of 13:02:31Z.
  - Scripts: `run_c274_second_pearson_skew_oos_fast.py` sha256 `f7009f24c837169d4ee2057ed805071ee9637acf3b2d8a1c91629ef37cdba550`; `verify_c274_second_pearson_skew_edge.py` sha256 `066523af9b2c54eb97c6554c7d7d8b326e5988205aa05d7f4d4c052d9d85d7e6`; `run_c274_second_pearson_skew_split_decomposition.py` sha256 `8f93642db396a499cda88e2c0645ad5def3d46bbb28a215e5c279bf615c135ce`; `run_c274_second_pearson_skew_param_sensitivity.py` sha256 `75d7d6d12a341af7597d630e3b75bda3405f84a2dc3a33ddd063f110e827da3a`.
- **C275 (MEDCOUPLE) — OOS RUNNING:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR` (`RTE/WHITE_DIAG_LINE_LENGTH_MEDCOUPLE`), grep-zero by design + runtime fail-closed. OOS/ingest/registry/summary artifacts **MISSING** as of 13:02:31Z.
  - Runner `scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9` (PID 8269, log `/tmp/c275_oos.log`).

## VERIFIED-BY-THIS-SESSION BLOCK (2026-11-12T13:02:31Z UTC)
- **Processes:** C274 sensitivity PID **7673 RUNNING** (chain 7671/7672/7673). C275 OOS PID **8269 RUNNING** (ppid 8268), log `/tmp/c275_oos.log`. No other relevant workers found.
- **Artifacts:** no `reports/campaign274_param_sensitivity_*`; no C275 OOS/ingest/registry/summary/verify/split/sensitivity artifacts. C274 corrected evidence + C273 evidence present and hashes consistent with preserved records above.
- **Data/env/git:** `data/cache/` **68 files**. No refetch performed. Working tree clean.
- **Bottlenecks addressed:** C274 sensitivity left running to completion; C275 OOS started (restarted this session); C275 downstream scripts implemented and hashed. Future session must complete the pipeline and emit/record artifacts — not re-plan.

## HARD BANS
- No status-only work.
- No reruns of C1–C274 except evidence-backed defect fix.
- No network refetch; no synthetic/fabricated data.
- No threshold weakening.
- No edits to `research_state/state.yaml` unless explicitly requested.
- Record all new/updated artifact SHA256s **from file bytes**.

## BOTTLENECK REMOVAL — ENFORCED FOR FUTURE AGENTS
Future agents cannot avoid heavy working:
1. Each step specifies a concrete command and expected artifact.
2. Completion requires recording artifact paths + SHA256-from-bytes here.
3. Prior evidence is hash-pinned; no redundant investigation/reruns allowed.
4. If C275 shows no edge, C276 distinctness+implementation+execution must begin in-session.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T13:02:31Z UTC.**
