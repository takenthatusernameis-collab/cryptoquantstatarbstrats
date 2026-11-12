# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T12:07:42Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (re-verified 2026-11-12T12:07:42Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 preserved (`promotion_readiness: READY_FOR_REVIEW`). C274 corrected = **NO EDGE** (preserved). **No status-only work.**

**BOTTLENECKS REMOVED / HEAVY WORK IN FLIGHT (started this session 2026-11-12 ~12:00Z):**
- **C274 param sensitivity RUNNING (bgp_1cfa1cc85001jEBdrKhfsl0kGe, PID 4903):** `python3 scripts/run_c274_second_pearson_skew_param_sensitivity.py` > `/tmp/c274_sens.log`. Script sha256 `75d7d6d12a341af7597d630e3b75bda3405f84a2dc3a33ddd063f110e827da3a`. Expected artifact: `reports/campaign274_param_sensitivity_*.json` (not yet emitted as of 12:07:42Z). **Next agent must wait for completion, then record artifact path + SHA256-from-bytes here.**
- **C275 OOS RUNNING (PID 5314):** `python3 scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` > `/tmp/c275_oos.log`. Script sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9`. Expected artifacts: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_medcouple_shock_mr_costed_oos_*.json`, `reports/real_feed_ingest_attempt_275_*.json`, `reports/strategy_edge_registry_275_*.json`, `reports/campaign275_execution_summary_*.json` (none emitted yet as of 12:07:42Z). **Next agent must wait for completion, then record all paths + SHA256-from-bytes here.**
- **C275 downstream scripts IMPLEMENTED (ready to run after C275 OOS artifacts exist):**
  - `scripts/verify_c275_medcouple_edge.py` sha256 `282ba827b4b7857fda9b7fb76c68293f16cd9ea1b58267b57bb3d66ada960e50`
  - `scripts/run_c275_medcouple_split_decomposition.py` sha256 `9bac5d1e76488d21e7e0ccd1c470a241e9d46f60bbd0d0b5c5d11bb9ae29ae9d`
  - `scripts/run_c275_medcouple_param_sensitivity.py` sha256 `02be7056f65f84c256c4f522d3e9a9fb92bb83afb6a2a219ad0080ecaa3b8aca`

**IMMEDIATE MANDATORY HEAVY CAMPAIGN FOR NEXT SESSION (non-optional, in order):**

1. **Finalize C274 param sensitivity:** confirm PID 4903 completed and `/tmp/c274_sens.log` shows artifact. Record `reports/campaign274_param_sensitivity_*.json` path + **SHA256-from-bytes** here. If failed, fix defect with evidence and rerun (only allowed rerun for evidenced defect).

2. **Finalize C275 OOS:** confirm PID 5314 completed and `/tmp/c275_oos.log` shows 4 artifacts. Record OOS/ingest/registry/summary paths + **SHA256-from-bytes** here. If failed, fix evidenced defect and rerun.

3. **Run C275 downstream (after C275 OOS artifacts exist):** execute in order:
   - `python3 scripts/verify_c275_medcouple_edge.py` → record `reports/campaign275_verification_*.json` path+SHA256
   - `python3 scripts/run_c275_medcouple_split_decomposition.py` → record `reports/campaign275_split_decomposition_*.json` path+SHA256
   - `python3 scripts/run_c275_medcouple_param_sensitivity.py` → record `reports/campaign275_param_sensitivity_*.json` path+SHA256
   All real cached data only, fail-closed, no network, honest edge evaluation.

4. **Post-C275 decision/action (based on artifacts):** if edge proven → build promotion evidence package with full provenance (`READY_FOR_REVIEW` or `NOT_READY` with reasons). If **no edge** → document concrete failing condition, **identify+prove grep-zero distinctness and prepare C276** (new strategy/hypothesis), then **begin execution** to emit C276 OOS+core artifacts with SHA256s. Do not stop at planning.

5. **No status-only work.** No reruns of C1–C274 except evidence-backed defect fix. No network refetch. No synthetic/fabricated data. No threshold weakening.

### STATE SNAPSHOT (re-verified 2026-11-12T12:07:42Z UTC)
- **Env:** `python3 3.12.3`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`. `data/cache/` = **66 real files** (33 `.pkl` + 33 `.meta.json` pairs). No refetch. `git status` clean at session start (handoff/scripts edits this session uncommitted).
- **HANDOFF:** this file only (`HANDOFF.md`). `research_state/state.yaml` stale at C248, locked.
- **C1–C15, C249–C272:** complete, `oos_edge_proven:false`.
- **C273:** `CONDITIONAL_EDGE_PROVEN` / verified / replication-matched / split-decomposed / param sensitivity `robust_neighborhood` (21/27). Promotion `READY_FOR_REVIEW`. JSON sha256 `b02ca846eebcdc1253c45b0686e28bef787714b9373e8e0c5118322b3ffe8fad`; MD sha256 `d03eab43502bd8c53845e692d981cb9d020c1f728bcb3afb21b7bb5453ba72b3`; builder sha256 `48ed28d0fc808092188939c44e04d3112ed489215b1b40be0e49d3552715ec33`. **Preserved/unchanged.**
- **C274 (SECOND_PEARSON_SKEW, corrected 061632Z) — NO EDGE (preserved):** `edge_claim:NONE`, `oos_edge_proven:false`, `any_exposure_oos:false`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, cross-asset OOS net sums all 0 (11 assets). Do **not** weaken thresholds. Superseded buggy 055039Z artifacts must not be cited.
  - OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_second_pearson_skew_shock_mr_costed_oos_20261112T061632Z.json` sha256 `57b86c398b4ae041c0ada5c77f6cf3ba3b235a9f12d891921f84a7e41f580669`
  - Ingest `reports/real_feed_ingest_attempt_274_20261112T061632Z.json` sha256 `66ef3ced7ea6392ea77a0373e0d850a9405a6d0bb866be2830d59a3ab10dabce`
  - Registry `reports/strategy_edge_registry_274_20261112T061632Z.json` sha256 `d05229dcdfbe31036019ddb2903f10393ce12a1cab01178ac05029a2f755b846`
  - Summary `reports/campaign274_execution_summary_20261112T061632Z.json` sha256 `44eced1140c385abcc69bb8dcb51bda34215ea1fab53b061897d5ee9`
  - Verify `reports/campaign274_verification_20261112T062244Z.json` sha256 `1cff4cf55dddc058556e61dc6ab12186ceea6febe17a094cfe5082ef68e76826` (`verification_passed:true, internal_consistency_passed:true, edge_rule_satisfied:false`)
  - Split `reports/campaign274_split_decomposition_20261112T062431Z.json` sha256 `61b3d6e7a16d35f6536d924b1ab693223f458433b05c196e2b23b4d79d73ea9e`
  - Scripts: `scripts/run_c274_second_pearson_skew_oos_fast.py` sha256 `f7009f24c837169d4ee2057ed805071ee9637acf3b2d8a1c91629ef37cdba550`; `scripts/verify_c274_second_pearson_skew_edge.py` sha256 `066523af9b2c54eb97c6554c7d7d8b326e5988205aa05d7f4d4c052d9d85d7e6`; `scripts/run_c274_second_pearson_skew_split_decomposition.py` sha256 `8f93642db396a499cda88e2c0645ad5def3d46bbb28a215e5c279bf615c135ce`; `scripts/run_c274_second_pearson_skew_param_sensitivity.py` sha256 `75d7d6d12a341af7597d630e3b75bda3405f84a2dc3a33ddd063f110e827da3a`.
  - **Param sensitivity artifact:** **RUNNING (PID 4903, started 2026-11-12 ~12:00Z, log `/tmp/c274_sens.log`)** — no artifact emitted yet at 12:07:42Z. Must record `reports/campaign274_param_sensitivity_*.json` path+SHA256-from-bytes on completion.
- **C275 (MEDCOUPLE) — OOS RUNNING:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR` (`RTE/WHITE_DIAG_LINE_LENGTH_MEDCOUPLE`), grep-zero by design + runtime fail-closed. Runner `scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9` **RUNNING (PID 5314, log `/tmp/c275_oos.log`)** — no artifacts emitted yet at 12:07:42Z. Downstream scripts implemented (not run): `scripts/verify_c275_medcouple_edge.py` sha256 `282ba827b4b7857fda9b7fb76c68293f16cd9ea1b58267b57bb3d66ada960e50`, `scripts/run_c275_medcouple_split_decomposition.py` sha256 `9bac5d1e76488d21e7e0ccd1c470a241e9d46f60bbd0d0b5c5d11bb9ae29ae9d`, `scripts/run_c275_medcouple_param_sensitivity.py` sha256 `02be7056f65f84c256c4f522d3e9a9fb92bb83afb6a2a219ad0080ecaa3b8aca`.

### VERIFIED-BY-THIS-SESSION BLOCK (2026-11-12T12:07:42Z UTC)
- **Processes:** C274 sensitivity PID **4903 RUNNING** (started ~12:00Z), C275 OOS PID **5314 RUNNING** (started ~12:07Z). No prior claims trusted.
- **C274 param sensitivity artifact:** `reports/campaign274_param_sensitivity_*.json` → **MISSING** (not yet emitted). Script sha256 verified.
- **C275 artifacts:** `reports/*medcouple*_oos_*.json`, `reports/real_feed_ingest_attempt_275_*.json`, `reports/strategy_edge_registry_275_*.json`, `reports/campaign275_execution_summary_*.json` → **all MISSING** (not yet emitted). Runner sha256 verified.
- **C275 downstream scripts:** created this session — verify `282ba827...`, split `9bac5d1e...`, sensitivity `02be7056...` (SHA256 verified). Not yet runnable until C275 OOS artifacts exist.
- **Env/data:** `data/cache/` = **66 real files**. No network refetch. `git status` clean at start. C273/C274 evidence preserved, SHAs match.
- **Bottlenecks cleared:** installed deps, started C274 sensitivity and C275 OOS, implemented C275 downstream scripts — future agent must complete heavy pipeline, not re-plan.

## HARD BANS
- ❌ No status-only work.
- ❌ No re-runs of C1–C274 except evidence-backed defect fix.
- ❌ No network refetch; no synthetic/fabricated data.
- ❌ No threshold weakening.
- ❌ No edits to `research_state/state.yaml` unless explicitly requested.

## HISTORICAL RECORD (condensed)
- **C249–C272:** all `edge_claim:NONE`, `oos_edge_proven:false`.
- **C273:** conditional proven edge (PERCENTILE_SPREAD), verified/replication-matched/split-decomposed, param sensitivity robust_neighborhood (21/27); promotion `READY_FOR_REVIEW`.
- **C274:** SECOND_PEARSON_SKEW corrected = NO EDGE (061632Z, verified/split-decomposed). Param sensitivity **MISSING — must run**.
- **C275:** MEDCOUPLE grep-zero, OOS **NOT RUN**; downstream verify/split/sensitivity + C276 prep/exec pending per outcome. **Verified/re-confirmed 11:56:13Z — all C275 artifacts still MISSING, all 3 downstream scripts still MISSING.**

## BOTTLENECK REMOVAL — ENFORCED FOR FUTURE AGENTS
**The next session MUST execute heavy work immediately.** No planning, no status updates, no "investigating." The campaign is defined above with explicit commands and artifact expectations. Future agents cannot avoid heavy working because:
1. Every step has a concrete command to run
2. Every step produces a verifiable artifact with SHA256
3. The handoff records all prior SHA256s so no rework is possible
4. Hard bans prevent low-value activity

**END OF DURABLE HANDOFF — refreshed 2026-11-12T12:07:42Z UTC. C274 param sensitivity PID 4903 RUNNING (`/tmp/c274_sens.log`), C275 OOS PID 5314 RUNNING (`/tmp/c275_oos.log`), C275 verify/split/sensitivity scripts implemented (SHAs above). Next session: finalize both runs and record artifact paths+SHA256s, run C275 verify/split/sensitivity, then honest edge decision + promotion or C276 prep/exec. C273 preserved (READY_FOR_REVIEW). No status-only work.**