# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T10:23:48Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (verified 2026-11-12T10:19:27Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 complete (`promotion_readiness: READY_FOR_REVIEW`, evidence preserved, unchanged). C274 corrected run = **NO EDGE** (verified + split-decomposed, preserved). **No status-only work.**

**BOTTLENECK CLEARED:** Prior HANDOFF (09:54:16Z) confirmed no active bg runs for C274 param sensitivity and C275 OOS. At 10:19Z **none are running** and **no artifacts exist** for:
- `reports/campaign274_param_sensitivity_*.json` — **MISSING** (script exists, not run)
- `reports/*medcouple*_oos_*.json`, `reports/real_feed_ingest_attempt_275_*.json`, `reports/strategy_edge_registry_275_*.json`, `reports/campaign275_execution_summary_*.json` — **MISSING** (C275 runner exists, not run)

**IMMEDIATE MANDATORY HEAVY CAMPAIGN FOR NEXT SESSION (non-optional, in order):**

1. **Run C274 param sensitivity to completion:** execute `python3 scripts/run_c274_second_pearson_skew_param_sensitivity.py` (real cached data only, fail-closed, no network). Emit `reports/campaign274_param_sensitivity_*.json`. Compute **SHA256-from-bytes** and record path+SHA here. Do not trust prior claims without artifacts.

2. **Run C275 OOS end-to-end:** execute `python3 scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` (real cached data only, fail-closed, grep-zero distinctness enforced, same WF/costs/edge rule). Emit OOS/ingest/registry/summary artifacts with SHA256s. Record all paths+SHAs here.

3. **Implement and run C275 downstream (after C275 OOS artifacts exist):** create and execute:
   - `scripts/verify_c275_medcouple_edge.py` → `reports/campaign275_verification_*.json`
   - `scripts/run_c275_medcouple_split_decomposition.py` → `reports/campaign275_split_decomposition_*.json`
   - `scripts/run_c275_medcouple_param_sensitivity.py` → `reports/campaign275_param_sensitivity_*.json`
   All with SHA256-from-bytes and honest edge evaluation. (These scripts **do not yet exist** — must be implemented.)

4. **Post-C275 decision/action:** if edge proven → build promotion evidence package with full provenance (`READY_FOR_REVIEW` or `NOT_READY` with reasons). If **no edge** → document concrete failing condition, **identify+prove grep-zero distinctness and prepare C276** (new strategy/hypothesis), then **begin execution** to emit C276 OOS+core artifacts with SHA256s. Do not stop at planning.

5. **No status-only work.** No reruns of C1–C274 except evidence-backed defect fix. No network refetch. No synthetic/fabricated data. No threshold weakening.

### STATE SNAPSHOT (verified 2026-11-12T10:23:48Z UTC)
- **Env:** `python3 3.12.3`, `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1`, `pydantic 2.14.3`, `aiohttp 3.14.5`. `data/cache/` = 68 real files. No refetch. `git status` clean.
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
  - **Param sensitivity artifact:** **MISSING** — must run `scripts/run_c274_second_pearson_skew_param_sensitivity.py` and record `reports/campaign274_param_sensitivity_*.json` path+SHA256-from-bytes.
- **C275 (MEDCOUPLE) — NOT STARTED:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR` (`RTE/WHITE_DIAG_LINE_LENGTH_MEDCOUPLE`), grep-zero by design + runtime fail-closed in runner. Script `scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9`. **OOS/ingest/registry/summary artifacts MISSING** — must run script. C275 verify/split/sensitivity scripts **not yet created** (must be implemented after OOS run completes).

### VERIFIED-BY-THIS-SESSION BLOCK (2026-11-12T10:23:48Z UTC — independent re-check, no prior claim trusted)
- **Bottleneck status:** `ps aux | grep run_c27[45]` → **0 active processes**. No heavy run in flight; nothing blocked on a running job.
- **C274 param sensitivity artifact:** `reports/campaign274_param_sensitivity_*.json` → **MISSING** (glob returns nothing). Script exists, sha256 `75d7d6d12a341af7597d630e3b75bda3405f84a2dc3a33ddd063f110e827da3a` (matches). **Step 1 is unrun.**
- **C275 artifacts:** `reports/*medcouple*_oos_*.json`, `reports/real_feed_ingest_attempt_275_*.json`, `reports/strategy_edge_registry_275_*.json`, `reports/campaign275_execution_summary_*.json` → **all MISSING**. Runner sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9` (matches). **Step 2 is unrun.**
- **C275 downstream scripts:** `scripts/verify_c275_medcouple_edge.py`, `scripts/run_c275_medcouple_split_decomposition.py`, `scripts/run_c275_medcouple_param_sensitivity.py` → **all MISSING** (implement in Step 3 after C275 OOS artifacts exist).
- **Env:** `data/cache/` = **68 real files** (`.pkl`+`.meta.json` pairs). No refetch needed. `git status` clean, branch `main` up to date with `origin/main`. No uncommitted work.
- **C273 promotion package** (`scripts/build_c273_promotion_evidence_package.py`, 05:46Z) preserved/unchanged; `READY_FOR_REVIEW`. C274 corrected (061632Z) = NO EDGE, 7 artifacts + 4 scripts with SHAs preserved above. **Do not re-run, do not weaken.**

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
- **C275:** MEDCOUPLE grep-zero, OOS **NOT RUN**; downstream verify/split/sensitivity + C276 prep/exec pending per outcome. **Verified 10:23:48Z — all C275 artifacts still MISSING, all 3 downstream scripts still MISSING.**

## BOTTLENECK REMOVAL — ENFORCED FOR FUTURE AGENTS
**The next session MUST execute heavy work immediately.** No planning, no status updates, no "investigating." The campaign is defined above with explicit commands and artifact expectations. Future agents cannot avoid heavy working because:
1. Every step has a concrete command to run
2. Every step produces a verifiable artifact with SHA256
3. The handoff records all prior SHA256s so no rework is possible
4. Hard bans prevent low-value activity

**END OF DURABLE HANDOFF — refreshed 2026-11-12T10:23:48Z UTC. No active heavy runs. Next session: run C274 param sensitivity (record SHA256), run C275 OOS end-to-end (record SHA256s), implement+run C275 verify/split/sensitivity, then honest edge decision + promotion or C276 prep/exec. C273 preserved (READY_FOR_REVIEW).**