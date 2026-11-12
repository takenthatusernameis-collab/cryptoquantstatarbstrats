# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T09:25:45Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (verified 2026-11-12T09:25:45Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 is complete and `promotion_readiness: READY_FOR_REVIEW` (evidence preserved, unchanged). C274 corrected run is executed and verified as **NO EDGE** on real cached data; end-to-end artifacts (OOS/ingest/registry/summary/verify/split-decomp) are complete and unchanged.

**ACTIVE HEAVY RUNS (launched 2026-11-12T09:25:45Z UTC, background, session-lifetime):**
- `bgp_1cf1434f20013Gw77dW6Y1PrSa` (pid 32524): `python3 scripts/run_c274_second_pearson_skew_param_sensitivity.py` — **RUNNING/IN PROGRESS** (expected: `reports/campaign274_param_sensitivity_*.json`).
- `bgp_1cf1437d8001oQZPkNwQRQO1s7` (pid 32535): `python3 scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` — **RUNNING/IN PROGRESS** (expected: C275 OOS, ingest, registry, exec summary in `reports/`).

**Next session must execute the C275 focus campaign to completion and never substitute status-only work:** (1) wait for/confirm completion of the two active runs above; if a run failed or is missing artifacts, re-run it to completion (real cached data only, fail-closed). Compute SHA256-from-bytes for every newly emitted artifact and record paths+SHAs here; (2) complete C275 end-to-end by implementing and running verification, split decomposition, and param sensitivity scripts (same WF/costs, real cached data only, fail-closed); emit `reports/campaign275_verification_*.json`, `reports/campaign275_split_decomposition_*.json`, `reports/campaign275_param_sensitivity_*.json` with SHA256-from-bytes and honest edge evaluation; (3) evaluate edge rule honestly and act: if edge proven, build promotion evidence package with full provenance (`READY_FOR_REVIEW` or `NOT_READY` with reasons); if not, document failing condition, identify+prepare grep-zero C276 (prove distinctness, runtime grep-zero enforced) and begin execution to emit OOS+core artifacts with SHA256s.** No status-only work. No network refetch. No threshold weakening.

### BOTTLENECK AUDIT — 2026-11-12T09:25:45Z UTC
- **Cleared:** C274 param sensitivity and C275 OOS were previously not running; both launched this session as tracked background processes (see above). This removes the immediate execution bottleneck.
- **Remaining blockers/gaps (next session must close):** confirm bgp runs completed successfully and artifacts exist with recorded SHA256s; C275 verification/split/sensitivity scripts do not yet exist and must be implemented+run; C276 not yet identified/executed if C275 shows no edge.
- `HANDOFF.md` is the single durable root handoff (this file).
- Deps verified: `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1, `pydantic` 2.14.3, `aiohttp` 3.14.5 (`deps ok`).
- `data/cache/` = 68 real files; **no refetch**, no network needed. Real caches verified by prior campaigns.
- C273 promotion evidence preserved/unchanged (`READY_FOR_REVIEW`) — do not undo/modify.
- C274 corrected core artifacts (061632Z) and verification + split decomposition complete. **No edge** (`edge_claim:NONE`, `oos_edge_proven:false`, `any_exposure_oos:false`, cross-asset OOS net sums all 0). Superseded buggy 055039Z artifacts must not be cited.
- **C274 param sensitivity script:** `scripts/run_c274_second_pearson_skew_param_sensitivity.py` — sha256 `75d7d6d12a341af7597d630e3b75bda3405f84a2dc3a33ddd063f110e827da3a` — **launched (bgp_1cf1434f20013Gw77dW6Y1PrSa), artifact SHA pending completion**.
- **C275 MEDCOUPLE OOS script:** `scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` — sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9` — **launched (bgp_1cf1437d8001oQZPkNwQRQO1s7), artifact SHAs pending completion**.
- **C275 distinctness:** grep-zero re-verified pre-run (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE|WHITE_DIAG_LINE_LENGTH_MEDCOUPLE|MEDCOUPLE` → 0 hits in scripts/strategies/backtest/utils). Runner performs runtime grep and fail-closes on non-self hits.

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
  - **Param sensitivity artifact:** **PENDING** (run launched this session, bgp_1cf1434f20013Gw77dW6Y1PrSa) — record `reports/campaign274_param_sensitivity_*.json` path+SHA256-from-bytes when complete.
- **Superseded/invalid (do not cite):** 055039Z OOS/ingest/registry/summary.

### C275 — MEDCOUPLE (IN PROGRESS)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR`
- **Script:** `scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` — sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9`
- **Run status:** **launched this session** (bgp_1cf1437d8001oQZPkNwQRQO1s7). OOS/ingest/registry/summary artifacts and SHAs **pending completion** — must be recorded here.
- **Required to finish C275 end-to-end after run completes:**
  1. Record C275 OOS/ingest/registry/summary paths + SHA256-from-bytes.
  2. Write/run `scripts/verify_c275_medcouple_edge.py` + emit `reports/campaign275_verification_*.json` + SHA256.
  3. Write/run `scripts/run_c275_medcouple_split_decomposition.py` + emit split artifact + SHA256.
  4. Write/run `scripts/run_c275_medcouple_param_sensitivity.py` + emit sensitivity artifact + SHA256.
  5. Honest edge evaluation. If edge proven → build promotion evidence package with full provenance (`READY_FOR_REVIEW` or `NOT_READY` with reasons). If no edge → document concrete failure, identify+prepare grep-zero C276 and begin execution (emit artifacts with SHA256s).

**IMMEDIATE MANDATORY HEAVY WORK FOR NEXT SESSION (non-optional, in order):**
1. **Confirm active runs:** check `background_process status/logs` for bgp_1cf1434f20013Gw77dW6Y1PrSa and bgp_1cf1437d8001oQZPkNwQRQO1s7; ensure artifacts emitted. If failed/missing, re-run to completion. Compute SHA256-from-bytes for all new artifacts (C274 sensitivity, C275 OOS/ingest/registry/summary) and record paths+SHAs here.
2. **Complete C275 end-to-end:** implement and run verification, split decomposition, and param sensitivity (real cached data only, fail-closed, same WF/costs); emit artifacts with SHA256-from-bytes and honest edge evaluation.
3. **Post-C275 action:** if edge proven, build promotion evidence package with full provenance. If not, document failing condition, identify+prepare grep-zero C276 (prove distinctness) and begin execution.
4. **No status-only work.** No reruns of C1–C274 except evidence-backed defect fix. No network refetch. No threshold weakening.

## STATE SNAPSHOT (2026-11-12T09:25:45Z UTC)
- **C1–C15, C249–C272:** complete, `oos_edge_proven: false`.
- **C273:** `CONDITIONAL_EDGE_PROVEN` / verified / replication-matched / split-decomposed / param sensitivity `robust_neighborhood` (21/27). Promotion package `READY_FOR_REVIEW`.
  - JSON sha256 `b02ca846eebcdc1253c45b0686e28bef787714b9373e8e0c5118322b3ffe8fad`; MD sha256 `d03eab43502bd8c53845e692d981cb9d020c1f728bcb3afb21b7bb5453ba72b3`; builder sha256 `48ed28d0fc808092188939c44e04d3112ed489215b1b40be0e49d3552715ec33`.
- **C274:** corrected core = NO EDGE (verified & split-decomposed, preserved). Param sensitivity **in progress** (bgp launched this session).
- **C275:** MEDCOUPLE (`RTE/WHITE_DIAG_LINE_LENGTH_MEDCOUPLE`) grep-zero, OOS **in progress** (bgp launched this session); verify/split/sensitivity scripts not yet created.
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
- **C274:** SECOND_PEARSON_SKEW corrected run = NO EDGE (061632Z, verified/split-decomposed). Param sensitivity in progress.
- **C275:** MEDCOUPLE (`RTE/WHITE_DIAG_LINE_LENGTH_MEDCOUPLE`) grep-zero, OOS in progress.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T09:25:45Z UTC (active heavy runs: C274 param sensitivity bgp_1cf1434f20013Gw77dW6Y1PrSa, C275 OOS bgp_1cf1437d8001oQZPkNwQRQO1s7; next session must confirm artifacts+SHA256s, complete C275 verify/split/sensitivity, then honest edge decision and C276 prep/exec if no edge; C273 evidence preserved, READY_FOR_REVIEW).**
