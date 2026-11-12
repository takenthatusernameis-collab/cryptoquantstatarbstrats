# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T09:06:40Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (verified 2026-11-12T09:06:40Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 is complete and `promotion_readiness: READY_FOR_REVIEW` (evidence preserved, unchanged). C274 corrected run is executed and verified as **NO EDGE** on real cached data; end-to-end artifacts (OOS/ingest/registry/summary/verify/split-decomp) are complete and unchanged. **C274 param sensitivity and C275 MEDCOUPLE OOS are RUNNING now** (background processes, no artifacts yet). **Next session must: (1) confirm/wait for `reports/campaign274_param_sensitivity_*.json` and the C275 OOS+ingest+registry+summary artifacts, compute SHA256-from-bytes for each, and record paths+SHAs here; (2) complete C275 end-to-end (verify, split decomposition, param sensitivity scripts + executions + SHA256s) using the pre-stated MEDCOUPLE feature/params/WF/costs; (3) evaluate edge rule honestly and act (promotion evidence if edge proven, else document failing condition and immediately identify+prepare/execute grep-zero C276).** No status-only work. No network refetch. No threshold weakening.

**Bottleneck audit (2026-11-12T09:06:40Z UTC): blockers removed/unblocked for heavy progress.**
- `HANDOFF.md` is the single durable root handoff (this file).
- Deps present: `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1, `pydantic` 2.14.3, `aiohttp` 3.14.5.
- `data/cache/` = 68 real files; **no refetch**, no network needed. Real caches verified by prior campaigns (spot `...631fcf7.pkl` sha256 `5607573...`, volume pkl/meta/prov as in state/artifacts).
- C273 promotion evidence preserved/unchanged (`READY_FOR_REVIEW`) — do not undo/modify.
- C274 corrected core artifacts (061632Z) and verification + split decomposition complete. **No edge** (`edge_claim:NONE`, `oos_edge_proven:false`, `any_exposure_oos:false`, cross-asset OOS net sums all 0). Superseded buggy 055039Z artifacts must not be cited.
- **Active processes (started this session, RUNNING as of 09:06Z):**
  - C274 param sensitivity: `bgp_1cef716dc001VojD4pAvbI4Ohi` (PID 28055), cmd `python3 scripts/run_c274_second_pearson_skew_param_sensitivity.py`, cwd repo root. **Artifact pending:** `reports/campaign274_param_sensitivity_*.json` not present at 09:06Z.
  - C275 MEDCOUPLE OOS: `bgp_1cefcc2ca001vt22WgxO4O9cu8` (PID 28193), cmd `python3 scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py`, cwd repo root. **Artifacts pending:** C275 OOS/ingest/registry/summary not present at 09:06Z.
- **C275 prepared and launched (heavy work done this session):** grep-zero distinctness re-verified 2026-11-12T08:52Z (`RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE|WHITE_DIAG_LINE_LENGTH_MEDCOUPLE|MEDCOUPLE` → 0 hits in scripts/strategies/backtest/utils). OOS runner created and syntax-checked.
  - Script: `scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` — sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9`
  - Feature (pre-stated, fail-closed): `RTE(black diagonal line entropy) / MEDCOUPLE(white diagonal segment lengths)` from delay-embedded log-volume returns; white segments = consecutive 0-cells, length>=`W_MIN=2`, pooled over off-diagonals `k!=0`; require >=3 qualifying white segments and finite nonzero medcouple (Brys–Hubert–Struyf, deterministic inline implementation). Undefined/non-finite/zero-denom → no feature (NaN).
  - Params/WF/costs: `W_RR=168, ALB=336, M_EMB=2, TAU=1, EPS_SCALE=0.5, W_MIN=2, ENTRY_Z=1.5, EXIT_Z=0.5, MAX_HOLD=24`; `train=720,test=168,step=168`; bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.
  - Strategy: `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR` (C275). Distinct from C125–C274 families (PEARSON_SKEW C252, SECOND_PEARSON_SKEW C274, GROENEVELD_MEEDEN_SKEW C249, BOWLEY_SKEW C247, KELLY_SKEW C248, MODE_SKEWNESS C269, SKEWNESS C230, etc.).
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
  - **Param sensitivity artifact:** `reports/campaign274_param_sensitivity_*.json` — **RUNNING (bgp_1cef716dc001VojD4pAvbI4Ohi, PID 28055, started ~08:50Z)**; next session must confirm artifact exists, compute SHA256-from-bytes, record path+SHA256 here.
- **Superseded/invalid (do not cite):** 055039Z OOS/ingest/registry/summary.

### C275 — IN PROGRESS (MEDCOUPLE, GREP-ZERO VERIFIED, OOS RUNNING)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR`
- **Script (created this session):** `scripts/run_c275_rte_over_white_diag_medcouple_shock_mr_costed_oos.py` — sha256 `8ce8fda46800d92ca2333120fed1ab11b285bec9e86164491004d0830735c9d9`
- **Distinctness:** grep-zero re-verified 2026-11-12T08:52Z (0 hits). Runner performs runtime grep and fail-closes on non-self hits.
- **Process:** `bgp_1cefcc2ca001vt22WgxO4O9cu8` (PID 28193) — RUNNING, artifacts pending.
- **Required to finish C275 end-to-end:** (a) collect OOS/ingest/registry/summary artifacts + SHA256-from-bytes; (b) write/run `scripts/verify_c275_medcouple_edge.py` + emit `reports/campaign275_verification_*.json`; (c) write/run `scripts/run_c275_medcouple_split_decomposition.py` + emit split artifact; (d) write/run `scripts/run_c275_medcouple_param_sensitivity.py` + emit sensitivity artifact; (e) record all paths+SHA256s, edge evaluation. If no edge, document concrete failure and immediately identify+prepare/execute grep-zero C276.

**IMMEDIATE MANDATORY HEAVY WORK (non-optional, in order):**
1. **Finalize in-flight runs:** wait/monitor `bgp_1cef716dc001VojD4pAvbI4Ohi` (C274 sensitivity) and `bgp_1cefcc2ca001vt22WgxO4O9cu8` (C275 OOS) to completion; confirm artifacts exist; compute SHA256-from-bytes for each and record here.
2. **Complete C275 end-to-end:** implement and run verification, split decomposition, and param sensitivity (real cached data only, fail-closed, same WF/costs); emit artifacts with SHA256-from-bytes and honest edge evaluation.
3. **Post-C275 action:** if edge proven, build promotion evidence package with full provenance (`READY_FOR_REVIEW` or `NOT_READY` with reasons). If not, document failing condition, identify+prepare grep-zero C276 (prove distinctness) and begin execution.
4. **No status-only work.** No reruns of C1–C274 except evidence-backed defect fix. No network refetch. No threshold weakening.

## STATE SNAPSHOT (2026-11-12T09:06:40Z UTC)
- **C1–C15, C249–C272:** complete, `oos_edge_proven: false`.
- **C273:** `CONDITIONAL_EDGE_PROVEN` / verified / replication-matched / split-decomposed / param-sensitivity `robust_neighborhood` (21/27). Promotion package `READY_FOR_REVIEW`.
  - JSON sha256 `b02ca846eebcdc1253c45b0686e28bef787714b9373e8e0c5118322b3ffe8fad`; MD sha256 `d03eab43502bd8c53845e692d981cb9d020c1f728bcb3afb21b7bb5453ba72b3`; builder sha256 `48ed28d0fc808092188939c44e04d3112ed489215b1b40be0e49d3552715ec33`.
- **C274:** corrected core = NO EDGE (verified & split-decomposed, preserved). **Param sensitivity RUNNING** (bgp_1cef716dc001VojD4pAvbI4Ohi, PID 28055) — artifact pending.
- **C275:** MEDCOUPLE pre-staged & OOS runner executed (RUNNING, bgp_1cefcc2ca001vt22WgxO4O9cu8, PID 28193) — core artifacts pending; verify/split/sensitivity pending.
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
- **C274:** SECOND_PEARSON_SKEW corrected run = NO EDGE (061632Z, verified/split-decomposed). Param sensitivity in-flight.
- **C275:** MEDCOUPLE (`RTE/WHITE_DIAG_LINE_LENGTH_MEDCOUPLE`) grep-zero, OOS in-flight.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T09:06:40Z UTC (immediate mandatory heavy work = finalize C274 sensitivity + C275 OOS, complete C275 verify/split/sensitivity with SHA256s, then honest edge decision and C276 prep/exec if no edge; C273 evidence preserved, READY_FOR_REVIEW).**
