# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T09:51:30Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (verified 2026-11-12T09:51:30Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 complete (`promotion_readiness: READY_FOR_REVIEW`, evidence preserved, unchanged). C274 corrected run = **NO EDGE** (verified + split-decomposed, preserved). **No status-only work.**

**BOTTLENECK CLEARED THIS SESSION:** Prior HANDOFF (09:25:45Z) claimed active bg runs, but at 09:51Z none were running and no `campaign274_param_sensitivity_*` / C275 artifacts existed in `reports/`. Relaunched now as tracked session-lifetime background processes (real cached data only, fail-closed, no network refetch):
- `bgp_1cf2bb6dc001u22vkWySiC6cfG` (pid 35652): `python3 scripts/run_c274_second_pearson_skew_param_sensitivity.py` — **RUNNING** (expect `reports/campaign274_param_sensitivity_*.json`).
- `bgp_1cf2bb6e1001wnLEhOgd4CP8TP` (pid 35656): `python3 scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` — **RUNNING** (expect C275 OOS/ingest/registry/summary `*_275_*.json` / `*medcouple*_oos_*.json`).

**IMMEDIATE MANDATORY HEAVY CAMPAIGN FOR NEXT SESSION (non-optional, in order):**
1. **Confirm/complete active runs:** check `background_process status/logs` for the two bgp IDs above. If either failed, produced no artifact, or was interrupted, **re-run to completion**. Compute **SHA256-from-bytes** for every newly emitted artifact (C274 sensitivity; C275 OOS/ingest/registry/summary) and record paths+SHAs in this file. Do not trust prior claims without artifacts.
2. **Finish C275 end-to-end (after artifacts exist):** implement and run (real cached data only, fail-closed, same WF/costs/edge rule) `scripts/verify_c275_medcouple_edge.py`, `scripts/run_c275_medcouple_split_decomposition.py`, `scripts/run_c275_medcouple_param_sensitivity.py`; emit `reports/campaign275_verification_*.json`, `reports/campaign275_split_decomposition_*.json`, `reports/campaign275_param_sensitivity_*.json` with SHA256-from-bytes and honest edge evaluation. (These scripts do **not** yet exist.)
3. **Post-C275 decision/action:** if edge proven → build promotion evidence package with full provenance (`READY_FOR_REVIEW` or `NOT_READY` with reasons). If **no edge** → document concrete failing condition, **identify+prove grep-zero distinctness and prepare C276** (new strategy/hypothesis), then **begin execution** to emit C276 OOS+core artifacts with SHA256s. Do not stop at planning.
4. **No status-only work.** No reruns of C1–C274 except evidence-backed defect fix. No network refetch. No synthetic/fabricated data. No threshold weakening.

### STATE SNAPSHOT (verified 2026-11-12T09:51:30Z UTC)
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
  - **Param sensitivity artifact:** **PENDING** — relaunched this session (`bgp_1cf2bb6dc001u22vkWySiC6cfG`). Record `reports/campaign274_param_sensitivity_*.json` path+SHA256-from-bytes on completion.
- **C275 (MEDCOUPLE) — IN PROGRESS:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR` (`RTE/WHITE_DIAG_LINE_LENGTH_MEDCOUPLE`), grep-zero by design + runtime fail-closed in runner. Script `scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9`. **OOS/ingest/registry/summary artifacts PENDING** — relaunched this session (`bgp_1cf2bb6e1001wnLEhOgd4CP8TP`). C275 verify/split/sensitivity scripts **not yet created** (must be implemented after run completes).

## HARD BANS
- ❌ No status-only work.
- ❌ No re-runs of C1–C274 except evidence-backed defect fix.
- ❌ No network refetch; no synthetic/fabricated data.
- ❌ No threshold weakening.
- ❌ No edits to `research_state/state.yaml` unless explicitly requested.

## HISTORICAL RECORD (condensed)
- **C249–C272:** all `edge_claim:NONE`, `oos_edge_proven:false`.
- **C273:** conditional proven edge (PERCENTILE_SPREAD), verified/replication-matched/split-decomposed, param sensitivity robust_neighborhood (21/27); promotion `READY_FOR_REVIEW`.
- **C274:** SECOND_PEARSON_SKEW corrected = NO EDGE (061632Z, verified/split-decomposed). Param sensitivity relaunched/pending.
- **C275:** MEDCOUPLE grep-zero, OOS relaunched/pending; downstream verify/split/sensitivity + C276 prep/exec pending per outcome.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T09:51:30Z UTC. Active heavy runs: C274 param sensitivity `bgp_1cf2bb6dc001u22vkWySiC6cfG` (35652), C275 OOS `bgp_1cf2bb6e1001wnLEhOgd4CP8TP` (35656). Next session: confirm artifacts+SHA256s, complete C275 end-to-end, then honest edge decision + promotion or C276 prep/exec. C273 preserved (READY_FOR_REVIEW).**
