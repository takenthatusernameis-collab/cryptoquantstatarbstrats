# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T07:53:48Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (verified 2026-11-12T07:53:48Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 is complete and `promotion_readiness: READY_FOR_REVIEW` (evidence preserved, unchanged). C274 corrected run is **executed and verified as NO EDGE** on real cached data; end-to-end artifacts (OOS/ingest/registry/summary/verify/split-decomp) are complete. **C274 param sensitivity is RUNNING in background** (started 2026-11-12T07:50Z, background process `bgp_1cec4ac51001buAHD8HAb2OnNO`, cmd `python3 scripts/run_c274_second_pearson_skew_param_sensitivity.py`). Next session must **close C274 sensitivity to completion** (wait for finish, confirm `reports/campaign274_param_sensitivity_*.json` exists, compute/record SHA256-from-bytes), then immediately **identify/prepare/execute C275 end-to-end**. No status-only work.

**Bottleneck audit (2026-11-12T07:53:48Z UTC): blockers removed/unblocked for heavy progress.**
- `HANDOFF.md` is the single durable root handoff (this file).
- Deps: `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1, `pydantic` 2.14.3, `aiohttp` 3.14.5.
- `data/cache/` = 68 real files; **no refetch**, no network needed.
- C273 promotion evidence preserved/unchanged (`READY_FOR_REVIEW`) — do not undo/modify.
- C274 corrected core artifacts emitted (061632Z run) and verification + split decomposition complete. C274 **did not prove edge** (`edge_claim:NONE`, `oos_edge_proven:false`, `any_exposure_oos:false`, all OOS nets 0). Superseded buggy 055039Z artifacts must not be cited.
- **Removed blocker:** C274 param sensitivity was previously not executed; it is now actively running in background (`bgp_1cec4ac51001buAHD8HAb2OnNO`, started ~2026-11-12T07:50Z). No `reports/campaign274_param_sensitivity_*` artifact observed yet at 07:53:48Z — next session must ensure it finishes and record artifact path+SHA256.
- C275 is **pre-staged below** with grep-zero distinctness verified 2026-11-12T07:53Z so next session cannot avoid heavy implementation/execution.
- Test suite: 1082 passed, 4 failed (campaign13 cache schema issues — known, non-blocking), 2 skipped.

### C274 — CORRECTED RESULT: NO EDGE (FAIL-CLOSED), REAL DATA ONLY
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW_SHOCK_MR`
- **Family:** RQA WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW shock on delay-embedded log-volume returns.
- **Feature/params/WF/costs:** `W_RR=168, ALB=336, M_EMB=2, TAU=1, EPS_SCALE=0.5, W_MIN=2, ENTRY_Z=1.5, EXIT_Z=0.5, MAX_HOLD=24`; `train=720,test=168,step=168`; bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`.
- **Distinctness:** grep-zero at run (`grep_hits_nonself_at_run: 0`, `collision_fail_closed:false`) per OOS artifact distinctness block.
- **Outcome (concrete, from corrected artifacts):** `edge_claim:NONE`, `oos_edge_proven:false`, `any_exposure_oos:false`, `all_cost_slices_positive_oos_net_sum:false`, `all_cost_slices_beat_bh_mean_rule:false`, `cross_asset_oos_net_sums = {fee0_slip0:0, fee5_slip5:0, fee10_slip10:0, fee20_slip20:0, fee40_slip40:0}` (11 assets). Fails edge rule due to **zero OOS exposure and zero nets**. Do **not** weaken thresholds.
- **Corrected artifacts (061632Z+):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_second_pearson_skew_shock_mr_costed_oos_20261112T061632Z.json` — sha256 `57b86c398b4ae041c0ada5c77f6cf3ba3b235a9f12d891921f84a7e41f580669`
  - Ingest: `reports/real_feed_ingest_attempt_274_20261112T061632Z.json` — sha256 `66ef3ced7ea6392ea77a0373e0d850a9405a6d0bb866be2830d59a3ab10dabce`
  - Registry: `reports/strategy_edge_registry_274_20261112T061632Z.json` — sha256 `d05229dcdfbe31036019ddb2903f10393ce12a1cab01178ac05029a2f755b846`
  - Exec summary: `reports/campaign274_execution_summary_20261112T061632Z.json` — sha256 `44eced1140c385abcc69bb8dcb51bda34215ea1fab53b9a37f03b061897d5ee9`
  - Script (fast runner): `scripts/run_c274_second_pearson_skew_oos_fast.py` — sha256 `f7009f24c837169d4ee2057ed805071ee9637acf3b2d8a1c91629ef37cdba550`
  - Verification: `reports/campaign274_verification_20261112T062244Z.json` — sha256 `1cff4cf55dddc058556e61dc6ab12186ceea6febe17a094cfe5082ef68e76826` (`verification_passed:true, internal_consistency_passed:true, edge_rule_satisfied:false`)
  - Split decomposition: `reports/campaign274_split_decomposition_20261112T062431Z.json` — sha256 `61b3d6e7a16d35f6536d924b1ab693223f458433b05c196e2b23b4d79d73ea9e`
  - Split script: `scripts/run_c274_second_pearson_skew_split_decomposition.py` — sha256 `8f93642db396a499cda88e2c0645ad5def3d46bbb28a215e5c279bf615c135ce`
  - Param sensitivity script (prepared, **running**): `scripts/run_c274_second_pearson_skew_param_sensitivity.py` — sha256 `75d7d6d12a341af7597d630e3b75bda3405f84a2dc3a33ddd063f110e827da3a`
  - **Param sensitivity artifact:** `reports/campaign274_param_sensitivity_*.json` — **PENDING (process bgp_1cec4ac51001buAHD8HAb2OnNO started 07:50Z, not finished at 07:53:48Z)**; must complete, then record path+SHA256-from-bytes.
- **Superseded/invalid (do not cite):** 055039Z OOS/ingest/registry/summary (`bad_window_len`/zero-exposure bug artifacts).

### C275 — PRE-STAGED NEXT CAMPAIGN (MUST PREPARE AND EXECUTE IMMEDIATELY AFTER C274 SENSITIVITY CLOSES)
- **Candidate (selected, grep-zero verified 2026-11-12T07:53Z):** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR`
  - **Family:** RQA WHITE_DIAG_LINE_LENGTH_MEDCOUPLE shock on delay-embedded log-volume returns (same proven RQA/WHITE_DIAG_LINE_LENGTH ratio-shock MR scaffold as C125–C274).
  - **Feature (pre-stated):** denominator = **medcouple** (robust skewness measure of Brys, Hubert & Struyf) of lengths of qualifying WHITE diagonal segments (consecutive 0-cells/non-recurrent, `length >= W_MIN=2`) pooled over off-diagonal diagonals `k!=0` with >=1 qualifying segment; computed on pooled segment lengths with a fixed, deterministic implementation (numpy/pure python, pre-stated). Ratio/feature = `RTE / WHITE_DIAG_LINE_LENGTH_MEDCOUPLE` (or pre-state exact ratio form consistent with recent campaigns). **Fail-closed** if insufficient qualifying segments, undefined/non-finite medcouple/denominator, or any non-finite feature — no fabrication.
  - **Distinctness proof (must re-run at execution and record):** `grep -rnE 'RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE|WHITE_DIAG_LINE_LENGTH_MEDCOUPLE|MEDCOUPLE' scripts/ strategies/ backtest/ utils/ 2>&1` returned **0 hits** at 2026-11-12T07:53Z (pre-staging). Distinct from PEARSON_SKEW(C252), SECOND_PEARSON_SKEW(C274), GROENEVELD_MEEDEN_SKEW(C249), BOWLEY_SKEW(C247), KELLY_SKEW(C248), MODE_SKEWNESS(C269), SKEWNESS(C230) and all C125–C274 families.
  - **Collision/fallback rule:** if any non-self hit appears at C275 run time, **fail-closed**, pick next distinct fallback, record grep evidence, and proceed. Pre-checked fallbacks likely grep-zero (re-verify): `RTE_OVER_WHITE_DIAG_LINE_LENGTH_QUARTILE_COEFFICIENT_OF_SKEWNESS` (note: conceptually related to Bowley but different naming — only use if grep-zero and clearly distinct from C247 naming in-repo; prefer other) — better fallbacks to re-verify: `RTE_OVER_WHITE_DIAG_LINE_LENGTH_NONPARAMETRIC_SKEW`, `RTE_OVER_WHITE_DIAG_LINE_LENGTH_L_SCALE_SKEW`. **Do not assume; prove grep-zero before claiming.**
- **Required C275 deliverables (end-to-end, no shortcuts):** OOS runner + verification + split decomposition + param sensitivity scripts (real-data-only, fail-closed), corrected OOS execution on `data/cache/`, ingest/registry/exec summary artifacts, all **SHA256-from-bytes**, grep-zero distinctness recorded at run, WF `720/168/168`, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`. Apply same edge rule. If edge proven, build promotion evidence package (`READY_FOR_REVIEW` or `NOT_READY` with reasons). If not, document concrete failing condition and immediately identify+prepare C276.
- **Rules:** same edge rule, real data only, no threshold weakening, no reruns of C1–C274 except evidence-backed defect fix, no network refetch.

**IMMEDIATE MANDATORY HEAVY WORK (non-optional, in order):**
1. **Close C274 sensitivity:** confirm `bgp_1cec4ac51001buAHD8HAb2OnNO` (or rerun if dead) completes; verify `reports/campaign274_param_sensitivity_*.json` exists; compute SHA256-from-bytes and record path+SHA256 in this HANDOFF (and summary notes as appropriate). No promotion package (edge not proven).
2. **Implement C275 (MEDCOUPLE, grep-zero re-verified):** write deterministic OOS/verify/split-decomp/param-sensitivity scripts with pre-stated feature/params/fail-closed logic and recorded distinctness grep.
3. **Execute C275 end-to-end on cached real data:** OOS → ingest/registry/summary → verification → split decomposition → param sensitivity; emit all artifacts with SHA256-from-bytes. Evaluate edge rule honestly.
4. **If C275 no edge:** document failing condition, identify+prepare grep-zero C276 and begin execution. If edge proven: produce promotion evidence package with full provenance.

## STATE SNAPSHOT (2026-11-12T07:53:48Z UTC)
- **C1–C15, C249–C272:** complete, `oos_edge_proven: false`.
- **C273:** `CONDITIONAL_EDGE_PROVEN` / verified / replication-matched / split-decomposed / param-sensitivity `robust_neighborhood` (21/27). Promotion package `READY_FOR_REVIEW`.
  - JSON sha256 `b02ca846eebcdc1253c45b0686e28bef787714b9373e8e0c5118322b3ffe8fad`; MD sha256 `d03eab43502bd8c53845e692d981cb9d020c1f728bcb3afb21b7bb5453ba72b3`; builder sha256 `48ed28d0fc808092188939c44e04d3112ed489215b1b40be0e49d3552715ec33`.
- **C274:** `edge_claim:NONE`, `oos_edge_proven:false`, `any_exposure_oos:false`, nets all zero (061632Z corrected artifacts, verified & split-decomposed). **Param sensitivity running** (`bgp_1cec4ac51001buAHD8HAb2OnNO`, started 07:50Z) — artifact pending at handoff time.
- **C275:** pre-staged as `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_MEDCOUPLE_SHOCK_MR` (grep-zero 07:53Z, must re-verify) — to be implemented and executed end-to-end next.
- **Environment:** python3 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pydantic 2.14.3, aiohttp 3.14.5. Caches: `data/cache/` 68 real files.
- **state.yaml:** stale at C248, locked — do not edit unless explicitly requested.

## HARD BANS
- ❌ No status-only work.
- ❌ No re-runs of C1–C15 or C249–C273 except evidence-backed defect fix.
- ❌ No network refetch; no synthetic/fabricated data.
- ❌ No threshold weakening.
- ❌ No edits to `research_state/state.yaml` unless explicitly requested.

## HISTORICAL RECORD (condensed)
- **C249–C272:** all `edge_claim: NONE`, `oos_edge_proven: false`.
- **C273:** conditional proven edge (PERCENTILE_SPREAD), verified, replication-matched, split-decomposed, param sensitivity robust_neighborhood (21/27); promotion package READY_FOR_REVIEW.
- **C274:** SECOND_PEARSON_SKEW identified/prepared (grep-zero), corrected run executed & verified; 055039Z buggy artifacts superseded. Param sensitivity script started 2026-11-12T07:50Z (bgp_1cec4ac51001buAHD8HAb2OnNO), artifact pending.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T07:53:48Z UTC (immediate mandatory heavy work = finish C274 param sensitivity + record SHA256, then implement and execute C275 MEDCOUPLE real-data campaign end-to-end; C273 evidence preserved, READY_FOR_REVIEW).**