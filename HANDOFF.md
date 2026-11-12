# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T09:16:27Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (verified 2026-11-12T09:16:27Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 is complete and `promotion_readiness: READY_FOR_REVIEW` (evidence preserved, unchanged). C274 corrected run is executed and verified as **NO EDGE** on real cached data; end-to-end artifacts (OOS/ingest/registry/summary/verify/split-decomp) are complete and unchanged. **C274 param sensitivity and C275 MEDCOUPLE OOS are NOT RUNNING** (prior background processes completed/failed without producing artifacts; no active processes now). **Next session must execute the C275 focus campaign to completion and never substitute status-only work:** (1) run `scripts/run_c274_second_pearson_skew_param_sensitivity.py` to completion, compute SHA256-from-bytes for the artifact, and record path+SHA here; (2) run `scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` to completion, compute SHA256-from-bytes for all 4 artifacts (OOS, ingest, registry, summary), and record paths+SHAs here; (3) complete C275 end-to-end by implementing and running verification, split decomposition, and param sensitivity scripts (real cached data only, fail-closed, same WF/costs); emit artifacts with SHA256-from-bytes and honest edge evaluation; (4) evaluate edge rule honestly and act: if edge proven, build promotion evidence package with full provenance (`READY_FOR_REVIEW` or `NOT_READY` with reasons); if not, document failing condition, identify+prepare grep-zero C276 and begin execution.** No status-only work. No network refetch. No threshold weakening.

**Focus campaign (C275 MEDCOMPLE) — must not be deferred:** run C274 param sensitivity → run C275 OOS → C275 verify/split/sensitivity → honest edge decision → C276 prep/exec if no edge. Every step emits a SHA256-from-bytes artifact recorded in this handoff.

### BOTTLENECK AUDIT — 2026-11-12T09:16:27Z UTC (CLEARED — no active blockers)
- No background `run_c27*` processes active (pgrep clean). Prior incomplete runs did not produce artifacts; scripts are present and syntax-checked, ready to execute.
- `HANDOFF.md` is the single durable root handoff (this file).
- Deps present: `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1, `pydantic` 2.14.3, `aiohttp` 3.14.5.
- `data/cache/` = 68 real files; **no refetch**, no network needed. Real caches verified by prior campaigns (spot `...631fcf7.pkl` sha256 `5607573...`, volume pkl/meta/prov as in state/artifacts).
- C273 promotion evidence preserved/unchanged (`READY_FOR_REVIEW`) — do not undo/modify.
- C274 corrected core artifacts (061632Z) and verification + split decomposition complete. **No edge** (`edge_claim:NONE`, `oos_edge_proven:false`, `any_exposure_oos:false`, cross-asset OOS net sums all 0). Superseded buggy 055039Z artifacts must not be cited.
- **C274 param sensitivity script:** `scripts/run_c274_second_pearson_skew_param_sensitivity.py` — sha256 `75d7d6d12a341af7597d630e3b75bda3405f84a2dc3a33ddd063f110e827da3a` — **NOT RUN YET** (must execute to completion).
- **C275 MEDCOUPLE OOS script:** `scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` — sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9` — **NOT RUN YET** (must execute to completion).
- **C275 prepared (heavy work done this session):** grep-zero distinctness re-verified (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE|WHITE_DIAG_LINE_LENGTH_MEDCOUPLE|MEDCOUPLE` → 0 hits in scripts/strategies/backtest/utils). OOS runner created and syntax-checked.
- **Gaps to close next session:** C274 param sensitivity artifact+SHA256; C275 OOS artifacts+SHA256s; C275 verification, split decomposition, param sensitivity (scripts + runs + SHA256s); decision/promotion evidence if edge proven, else C276 prep/exec.

### C274 — CORRECTED RESULT: NO EDGE (FAIL-CLOSED), REAL DATA ONLY (PRESERVED)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW_SHOCK_MR`
- **Outcome:** `edge_claim:NONE`, `oos_edge_proven:false`, `any_exposure_oos:false`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, `cross_asset_oos_net_sums = {fee0_slip0:0, fee5_slip5:0, fee10_slip10:0, fee20_slip20:0, fee40_slip40:0}` (11 assets). Do **not** weaken thresholds.
- **Corrected artifacts (061632Z+):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_second_pearson_skew_shock_mr_costed_oos_20261112T061632Z.json` — sha256 `57b86c398b4ae041c0ada5c77f6cf3ba3b235a9f12d891921f84a7e41f580669`
  - Ingest: `reports/real_feed_ingest_attempt_274_20261112T061632Z.json` — sha256 `66ef3ced7ea6392ea77a0373e0d850a9405a6d0bb866be2830d59a3ab10dabce`
  - Registry: `reports/strategy_edge_registry_274_20261112T061632Z.json` — sha256 `d05229dcdfbe31036019ddb2903f10393ce12a1cab01178ac05029a2f755b846`
  - Exec summary: `reports/campaign274_execution_summary_20261112T061632Z.json` — sha256 `44eced1140c385abcc69bb8dcb51bda34215ea1fab53b061897d5ee9`
  - Script (fast runner): `scripts/run_c274_second_pearson_skew_oos_fast.py` — sha256 `f7009f24c837169d4ee2057ed805071ee9637acf3b2d8a1c91629ef37cdba550`
  - Verification: `reports/campaign274_verification_20261112T062244Z.json` — sha256 `1cff4cf55dddc058556e61dc6ab12186ceea6febe17a094cfe5082ef68e76826` (`verification_passed:true, internal_consistency_passed:true, edge_rule_satisfied:false`)
  - Split decomposition: `reports/campaign274_split_decomposition_20261112T062431Z.json` — sha256 `61b3d6e7a16d35f6536d924b1ab693223f458433b05c196e2b23b4d79d73ea9e`
  - Split script: `scripts/run_c274_second_pearson_skew_split_decomposition.py` — sha256 `8f93642db396a499cda88e2c0645ad5def3d46bbb28a215e5c279bf615c135ce`
  - Param sensitivity script: `scripts/run_c274_second_pearson_skew_param_sensitivity.py` — sha256 `75d7d6d12a341af7597d630e3b75bda3405f84a2dc3a33ddd063f110e827da3a`
  - **Param sensitivity artifact:** `reports/campaign274_param_sensitivity_*.json` — **NOT RUN YET** (must execute, then record path+SHA256 here).
- **Superseded/invalid (do not cite):** 055039Z OOS/ingest/registry/summary.

### C275 — PRE-STAGED, NOT RUN (MEDCOUPLE, GREP-ZERO VERIFIED)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR`
- **Script (created this session):** `scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` — sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9`
- **Distinctness:** grep-zero re-verified (0 hits). Runner performs runtime grep and fail-closes on non-self hits.
- **Required to finish C275 end-to-end:**
  1. Run C275 OOS script to completion; collect OOS/ingest/registry/summary artifacts + SHA256-from-bytes; record paths+SHAs here.
  2. Write/run `scripts/verify_c275_medcouple_edge.py` + emit `reports/campaign275_verification_*.json` + SHA256.
  3. Write/run `scripts/run_c275_medcouple_split_decomposition.py` + emit split artifact + SHA256.
  4. Write/run `scripts/run_c275_medcouple_param_sensitivity.py` + emit sensitivity artifact + SHA256.
  5. Record all paths+SHA256s, edge evaluation. If no edge, document concrete failure and immediately identify+prepare/execute grep-zero C276.

**IMMEDIATE MANDATORY HEAVY WORK (non-optional, in order):**
1. **Execute C274 param sensitivity:** run `python3 scripts/run_c274_second_pearson_skew_param_sensitivity.py` to completion (may take 5-15 min); confirm artifact exists at `reports/campaign274_param_sensitivity_*.json`; compute SHA256-from-bytes and record path+SHA256 here.
2. **Execute C275 OOS:** run `python3 scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` to completion (may take 5-15 min); confirm 4 artifacts exist (OOS, ingest, registry, summary); compute SHA256-from-bytes for each and record paths+SHAs here.
3. **Complete C275 end-to-end:** implement and run verification, split decomposition, and param sensitivity (real cached data only, fail-closed, same WF/costs); emit artifacts with SHA256-from-bytes and honest edge evaluation.
4. **Post-C275 action:** if edge proven, build promotion evidence package with full provenance (`READY_FOR_REVIEW` or `NOT_READY` with reasons). If not, document failing condition, identify+prepare grep-zero C276 (prove distinctness) and begin execution.
5. **No status-only work.** No reruns of C1–C274 except evidence-backed defect fix. No network refetch. No threshold weakening.

## STATE SNAPSHOT (2026-11-12T09:16:27Z UTC)
- **C1–C15, C249–C272:** complete, `oos_edge_proven: false`.
- **C273:** `CONDITIONAL_EDGE_PROVEN` / verified / replication-matched / split-decomposed / param-sensitivity `robust_neighborhood` (21/27). Promotion package `READY_FOR_REVIEW`.
  - JSON sha256 `b02ca846eebcdc1253c45b0686e28bef787714b9373e8e0c5118322b3ffe8fad`; MD sha256 `d03eab43502bd8c53845e692d981cb9d020c1f728bcb3afb21b7bb5453ba72b3`; builder sha256 `48ed28d0fc808092188939c44e04d3112ed489215b1b40be0e49d3552715ec33`.
- **C274:** corrected core = NO EDGE (verified & split-decomposed, preserved). **Param sensitivity NOT RUN YET** (script ready, sha256 `75d7d6d12a341af7597d630e3b75bda3405f84a2dc3a33ddd063f110e827da3a`).
- **C275:** MEDCOUPLE (`RTE/WHITE_DIAG_LINE_LENGTH_MEDCOUPLE`) grep-zero, OOS script ready **NOT RUN YET** (sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9`); verify/split/sensitivity scripts not yet created.
- **Environment:** python3 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pydantic 2.14.3, aiohttp 3.14.5. Caches: `data/cache/` 68 real files.
- **state.yaml:** stale at C248, locked — do not edit unless explicitly requested.

## HARD BANS
- ❌ No status-only work.
- ❌ No re-runs of C1–C15 or C249–C274 except evidence-backed defect fix.
- ❌ No network refetch; no synthetic/fabricated data.
- ❌ No threshold weakening.
- ❌ No edits to `research_state/state.yaml` unless explicitly requested.

## HISTORICAL RECORD (condensed)
- **C249–C272:** all `edge_claim: NONE`, `oos_edge_proven: false`.
- **C273:** conditional proven edge (PERCENTILE_SPREAD), verified, replication-matched, split-decomposed, param sensitivity robust_neighborhood (21/27); promotion package READY_FOR_REVIEW.
- **C274:** SECOND_PEARSON_SKEW corrected run = NO EDGE (061632Z, verified/split-decomposed). Param sensitivity NOT RUN.
- **C275:** MEDCOUPLE (`RTE/WHITE_DIAG_LINE_LENGTH_MEDCOUPLE`) grep-zero, OOS script ready NOT RUN.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T09:16:27Z UTC (immediate mandatory heavy work = execute C274 param sensitivity + C275 OOS, complete C275 verify/split/sensitivity with SHA256s, then honest edge decision and C276 prep/exec if no edge; C273 evidence preserved, READY_FOR_REVIEW).**
