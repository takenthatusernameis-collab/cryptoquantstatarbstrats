# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T06:58:30Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (verified 2026-11-12T06:58:30Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 is complete and `promotion_readiness: READY_FOR_REVIEW` (evidence preserved, unchanged). C274 corrected run is **executed and verified as NO EDGE** on real cached data; required end-to-end artifacts are mostly complete, but **param sensitivity (heavy) may still be running** — next session must finish C274 closure (sensitivity artifact + SHA256 record) and immediately move to **C275 identify+prepare+execute** end-to-end. No status-only work.

**Bottleneck audit (2026-11-12T06:58:30Z UTC): bottlenecks removed / path unblocked.**
- `HANDOFF.md` is single durable root handoff.
- Deps: `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1.
- `data/cache/` = 68 real files; **no refetch**, no network needed.
- C273 promotion evidence preserved/unchanged (`READY_FOR_REVIEW`) — do not undo/modify.
- C274 corrected core artifacts emitted (061632Z run) and verification + split decomposition complete. C274 **did not prove edge** (`any_exposure_oos=false`, all OOS nets 0). Superseded buggy 055039Z artifacts must not be cited.
- Param sensitivity script is running in background (`bgp_1ce89b12c001t72UB5HHML5DN1`, `python3 scripts/run_c274_second_pearson_skew_param_sensitivity.py`) as of this handoff update; it may or may not have completed before session end — next session must check for `reports/campaign274_param_sensitivity_*.json` and, if absent, rerun to completion.

### C274 — CORRECTED RESULT: NO EDGE (FAIL-CLOSED), REAL DATA ONLY
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW_SHOCK_MR`
- **Family:** RQA WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW shock on delay-embedded log-volume returns.
- **Feature/params/WF/costs:** `W_RR=168, ALB=336, M_EMB=2, TAU=1, EPS_SCALE=0.5, W_MIN=2, ENTRY_Z=1.5, EXIT_Z=0.5, MAX_HOLD=24`; `train=720,test=168,step=168`; bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.
- **Distinctness:** grep-zero at run (`grep_hits_nonself_at_run: 0`, `collision_fail_closed:false`) per OOS artifact distinctness block.
- **Outcome (concrete, from corrected artifacts):** `edge_claim:NONE`, `oos_edge_proven:false`, `any_exposure_oos:false`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, `cross_asset_oos_net_sums = {fee0_slip0:0, fee5_slip5:0, fee10_slip10:0, fee20_slip20:0, fee40_slip40:0}` (11 assets). Fails edge rule due to **zero OOS exposure and zero nets** (no cost slice positive; cannot beat B&H). Do **not** weaken thresholds.
- **Corrected artifacts (061632Z+):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_second_pearson_skew_shock_mr_costed_oos_20261112T061632Z.json` — sha256 `57b86c398b4ae041c0ada5c77f6cf3ba3b235a9f12d891921f84a7e41f580669`
  - Ingest: `reports/real_feed_ingest_attempt_274_20261112T061632Z.json` — sha256 `66ef3ced7ea6392ea77a0373e0d850a9405a6d0bb866be2830d59a3ab10dabce`
  - Registry: `reports/strategy_edge_registry_274_20261112T061632Z.json` — sha256 `d05229dcdfbe31036019ddb2903f10393ce12a1cab01178ac05029a2f755b846`
  - Exec summary: `reports/campaign274_execution_summary_20261112T061632Z.json` — sha256 `44eced1140c385abcc69bb8dcb51bda34215ea1fab53b9a37f03b061897d5ee9`
  - Script (fast runner): `scripts/run_c274_second_pearson_skew_oos_fast.py` — sha256 `f7009f24c837169d4ee2057ed805071ee9637acf3b2d8a1c91629ef37cdba550`
  - Verification: `reports/campaign274_verification_20261112T062244Z.json` — sha256 `1cff4cf55dddc058556e61dc6ab12186ceea6febe17a094cfe5082ef68e76826` (`verification_passed:true, internal_consistency_passed:true, edge_rule_satisfied:false`)
  - Split decomposition: `reports/campaign274_split_decomposition_20261112T062431Z.json` — sha256 `61b3d6e7a16d35f6536d924b1ab693223f458433b05c196e2b23b4d79d73ea9e`
  - Split script: `scripts/run_c274_second_pearson_skew_split_decomposition.py` — sha256 `8f93642db396a499cda88e2c0645ad5def3d46bbb28a215e5c279bf615c135ce`
  - Param sensitivity script (prepared): `scripts/run_c274_second_pearson_skew_param_sensitivity.py` — sha256 `75d7d6d12a341af7597d630e3b75bda3405f84a2dc3a33ddd063f110e827da3a`
  - **Param sensitivity artifact:** `reports/campaign274_param_sensitivity_*.json` — **PENDING/VERIFY** (was running at handoff; if missing, must be produced by running script above to completion; record path+SHA256).
- **Superseded/invalid (do not cite):** 055039Z OOS/ingest/registry/summary (`bad_window_len`/zero-exposure bug artifacts).

### C275 — NEXT (MUST IDENTIFY, PREPARE, AND RUN IMMEDIATELY AFTER C274 CLOSURE)
- **Status:** not yet identified/prepared in this session (C274 closure took priority). Next session must **immediately** pick a genuinely distinct, pre-stated, causal, fail-closed, real-data-only costed OOS candidate in the RQA/WHITE_DIAG_LINE_LENGTH family neighborhood consistent with repo trajectory, prove `grep_hits_nonself_at_run == 0` collision-fail-closed against `scripts/ strategies/ backtest/ utils/`, prepare OOS/verify/split/sensitivity scripts, and execute end-to-end on `data/cache/`.
- **Candidate hints (must re-verify grep-zero before claiming):** state.yaml historically suggested `GROENEVELD_MEEDEN_SKEW/YULE_K/MIDRANGE/PEARSON_SKEW` family variants; `PEARSON_MODE_SKEW`=C269 and `GROENEVELD_MEEDEN_SKEW`=C249 already used — confirm exact unused name via grep. Prefer a statistically distinct moment/location/shape of WHITE_DIAG_LINE_LENGTH not in C125–C274 (e.g. `RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_SKEWNESS` / `YULE_K` / `MIDRANGE` / other clear unused form) — but **do not assume; select only after grep-zero proof**. If collision, pick next distinct fallback and record evidence.
- **Rules:** same edge rule, WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, real data only, SHA256-from-bytes for all artifacts, no threshold weakening, no reruns of C1–C274 except evidence-backed defect fix.

**IMMEDIATE MANDATORY HEAVY WORK (non-optional):**
1. **Close C274:** check for `reports/campaign274_param_sensitivity_*.json`. If missing, run `python3 scripts/run_c274_second_pearson_skew_param_sensitivity.py` to completion; compute SHA256-from-bytes and record in handoff/state summary notes. (No promotion package needed because edge not proven.)
2. **Identify+prepare C275:** choose distinct (grep-zero) candidate, document pre-stated feature/params/fail-closed logic, create runner/verify/split/sensitivity scripts.
3. **Execute C275 end-to-end:** corrected OOS on cached data → verification → split decomposition → param sensitivity; emit ingest/registry/summary; all SHA256-from-bytes. If edge proven, build promotion evidence package (`READY_FOR_REVIEW` or `NOT_READY` with reasons). If not, document concrete failing condition and identify+prepare C276.

## STATE SNAPSHOT (2026-11-12T06:58:30Z UTC)
- **C1–C15, C249–C272:** complete, `oos_edge_proven: false`.
- **C273:** `CONDITIONAL_EDGE_PROVEN` / verified / replication-matched / split-decomposed / param-sensitivity `robust_neighborhood` (21/27). Promotion package `READY_FOR_REVIEW`.
  - JSON sha256 `b02ca846eebcdc1253c45b0686e28bef787714b9373e8e0c5118322b3ffe8fad`; MD sha256 `d03eab43502bd8c53845e692d981cb9d020c1f728bcb3afb21b7bb5453ba72b3`; builder sha256 `48ed28d0fc808092188939c44e04d3112ed489215b1b40be0e49d3552715ec33`.
- **C274:** `edge_claim:NONE`, `oos_edge_proven:false`, `any_exposure_oos:false`, nets all zero by cost slice (061632Z corrected artifacts, verified & split-decomposed). Param sensitivity artifact pending/verify.
- **C275:** to be identified/prepared/run next (grep-zero distinct, real-data fail-closed).
- **Environment:** python3 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1. Caches: `data/cache/` 68 real files.
- **state.yaml:** stale at C248, locked — do not edit unless explicitly requested.

## HARD BANS
- ❌ No status-only work.
- ❌ No re-runs of C1–C15 or C249–C273 except evidence-backed defect fix.
- ❌ No network refetch; no synthetic/fabricated data.
- ❌ No threshold weakening.
- ❌ No edits to `research_state/state.yaml` unless explicitly requested.

## STATE SNAPSHOT (2026-11-12T06:52:39Z UTC)
- **C1–C15, C249–C272:** complete, `oos_edge_proven: false`.
- **C273:** `CONDITIONAL_EDGE_PROVEN` / verified / replication-matched / split-decomposed / param-sensitivity `robust_neighborhood` (21/27). Promotion package BUILT `promotion_readiness: READY_FOR_REVIEW`.
  - JSON: `reports/campaign273_promotion_evidence_package_20261112T054614Z.json` — sha256 `b02ca846eebcdc1253c45b0686e28bef787714b9373e8e0c5118322b3ffe8fad`
  - MD: `reports/campaign273_promotion_evidence_package_20261112T054614Z.md` — sha256 `d03eab43502bd8c53845e692d981cb9d020c1f728bcb3afb21b7bb5453ba72b3`
  - Builder: `scripts/build_c273_promotion_evidence_package.py` — sha256 `48ed28d0fc808092188939c44e04d3112ed489215b1b40be0e49d3552715ec33`
- **C274:** target identified/prepared (`SECOND_PEARSON_SKEW`, grep-zero), corrected scripts ready; **corrected run pending** (055039Z artifacts invalid/buggy — superseded).
- **Environment:** python3 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1. Caches: `data/cache/` 68 real files, no refetch.
- **state.yaml:** stale at C248, locked — do not edit unless explicitly requested by user.

## HARD BANS
- ❌ No status-only work; no "planning/researching" as substitute for producing artifacts.
- ❌ No re-runs of C1–C15 or C249–C273 except evidence-backed defect fix; rerun C273 core only if evidence-backed defect found.
- ❌ No network refetch (use `data/cache/` only). No synthetic/fabricated data.
- ❌ No threshold weakening.
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user.

---
## HISTORICAL RECORD (condensed)
- **C249–C272:** all `edge_claim: NONE`, `oos_edge_proven: false`.
- **C273:** conditional proven edge (PERCENTILE_SPREAD), verified, replication-matched, split-decomposed, param sensitivity robust_neighborhood (21/27); promotion package READY_FOR_REVIEW.
- **C274:** SECOND_PEARSON_SKEW identified/prepared (grep-zero), corrected run pending; 055039Z buggy artifacts superseded.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T06:52:39Z UTC (immediate mandatory heavy work = run/verify/decompose/sensitize/package C274 real-data campaign end-to-end; C273 evidence preserved, READY_FOR_REVIEW).**