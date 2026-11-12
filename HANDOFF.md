# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T06:14:27Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (verified 2026-11-12T06:05:20Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 is complete and `promotion_readiness: READY_FOR_REVIEW` (evidence preserved, unchanged). The next session must **not** revert to status-only work — it must complete the **C274** real-data costed OOS campaign (identified/prepared this session) on `data/cache/` only.

**Bottleneck audit (2026-11-12T06:14:27Z UTC): bottlenecks removed / path unblocked.**
- `HANDOFF.md` consolidated to this single authoritative block.
- Deps present: `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1.
- `data/cache/` = 68 real files (`.pkl`+`.meta.json`+provenance); **no refetch**, no network needed.
- C273 promotion evidence package/artifacts preserved (see STATE SNAPSHOT) — **do not undo/modify**.
- C274 target **identified and prepared** (grep-zero distinct, scripts present). No prior corrected C274 artifacts exist; the earlier 2026-11-12T05:50:39Z C274 artifacts (`*_274_20261112T055039Z.*` / `*_oos_20261112T055039Z.json`) were produced by a buggy runner (`bad_window_len` feature bug => zero exposure / `oos_edge_proven:false`) and are **superseded/invalid for C274 evidence** — do not cite as C274 result; replace with corrected artifacts.
- No stalled processes. Next agent may execute immediately.

### C274 — IDENTIFIED / PREPARED, RUN NOT YET COMPLETED (IMMEDIATE MANDATORY HEAVY WORK)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW_SHOCK_MR`
- **Family:** RQA WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW shock on delay-embedded log-volume returns.
- **Feature (pre-stated, causal, fail-closed):** on `r_t = ln(v_t)-ln(v_{t-1})`, delay embedding `X_i=(r_i,r_{i+tau})` with `m=2,tau=1` over trailing `W_RR=168`. Recurrence `R_{ij}=1` if `||X_i-X_j||_inf <= eps`, `eps = EPS_SCALE*std(r_window)`, `EPS_SCALE=0.5`. Signal = `3*(mean(L)-median(L))/std(L)` over qualifying WHITE diagonal segment lengths `L` pooled over off-diagonal diagonals `k!=0`, `length>=w_min=2`, `N>=3` (numpy mean/median/std `ddof=0`). **Fail-closed** if `N<3`, `std<=0`/non-finite, or feature non-finite/undefined.
- **Params:** `W_RR=168, ALB=336, M_EMB=2, TAU=1, EPS_SCALE=0.5, W_MIN=2, ENTRY_Z=1.5, EXIT_Z=0.5, MAX_HOLD=24`.
- **WF/costs:** `train=720, test=168, step=168`, cost grid bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.
- **Edge rule (unchanged):** `oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only.
- **Distinctness (grep-zero, verified this session):** `grep -rnE 'SECOND_PEARSON_SKEW|RTE_OVER_WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW|WHITE_DIAG_LINE_LENGTH_SECOND_PEARSON_SKEW' scripts/ strategies/ backtest/ utils/ 2>&1` → `grep_hits_nonself_at_run: 0` before run. Collision-fail-closed. Distinct from `GROENEVELD_MEEDEN_SKEW(C249)`, `PEARSON_MODE_SKEW(C269)`, `KELLY_SKEW(C248)`, `BOWLEY_SKEW(C247)`, moment `SKEWNESS(C230)`, and prior C125–C273 families.
- **Prepared scripts:**
  - Fast corrected OOS runner (preferred): `scripts/run_c274_second_pearson_skew_oos_fast.py`
  - Reference runner: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_second_pearson_skew_shock_mr_costed_oos.py`
  Both implement corrected `W_RR`-length return windows and include distinctness checks + full artifact emission (OOS, ingest attempt, registry, execution summary) with SHA256-from-bytes. Spot sanity check on first asset (fixed logic): `4944/4944` finite features, mean≈`0.917`, std≈`0.107`, `frac(|z|>=1.5)=0.0` (signalable distribution present; actual OOS outcome must be determined by full run).
- **Invalid/superseded (do not cite):** `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_second_pearson_skew_shock_mr_costed_oos_20261112T055039Z.json`, `reports/real_feed_ingest_attempt_274_20261112T055039Z.json`, `reports/strategy_edge_registry_274_20261112T055039Z.json`, `reports/campaign274_execution_summary_20261112T055039Z.json` (buggy `bad_window_len`).

**IMMEDIATE MANDATORY HEAVY WORK (non-optional, no planning phase): COMPLETE C274 END-TO-END.**
Execute immediately. Do not plan, summarize, or ask questions — produce concrete artifacts on real saved evidence only (no refetch, no synthetic).

1. **Run corrected C274 costed OOS (real cached data only):** `python3 scripts/run_c274_second_pearson_skew_oos_fast.py` (preferred). Confirm `pre_stated_distinctness.grep_hits_nonself_at_run == 0` in emitted artifacts and `collision_fail_closed == false`. Emit timestamped OOS + ingest attempt + edge registry + execution summary JSONs with SHA256-from-bytes for every artifact.
2. **Deterministic verification + decomposition + sensitivity (regardless of edge outcome, required artifacts):**
   - Build and run `scripts/verify_c274_second_pearson_skew_edge.py` → `reports/campaign274_verification_<ts>.json` recomputing/validating edge-rule compliance, cross-asset nets, and distinctness/params from saved OOS artifact.
   - Build and run split/asset decomposition script → `reports/campaign274_split_decomposition_<ts>.json` (per-asset nets by cost slice, split-level stats, replication-vs-OOS diffs/tolerances).
   - Build and run parameter-perturbation sensitivity (bounded grid around baseline, `EXIT_Z < ENTRY_Z`, same WF/costs/caches) → `reports/campaign274_param_sensitivity_<ts>.json` with edge-positive share and failing-combo details.
   All scripts/artifacts SHA256-from-bytes recorded.
3. **If C274 proves an edge (`oos_edge_proven: true` and all compliance flags true):** build `scripts/build_c274_promotion_evidence_package.py` (mirror C273 builder), emit `reports/campaign274_promotion_evidence_package_<ts>.json` + `.md`, compute SHA256-from-bytes for both + builder, set `promotion_readiness` (`READY_FOR_REVIEW` if complete/consistent/robust, else `NOT_READY` with reasons), and refresh this handoff in-place with C274 paths/SHA256/readiness and the next concrete step.
4. **If C274 does NOT prove an edge (expected possible):** document the specific failing condition concretely from artifacts (exact `cross_asset_oos_net_sums` by slice, `any_exposure_oos`, `all_cost_slices_positive_oos_net_sum`, `all_cost_slices_beat_bh_mean_rule`, per-asset breakdown). Do **not** weaken thresholds, do **not** rerun C1–C15/C249–C273, do **not** refetch. Update this handoff with C274 final result (paths/SHA256) and **identify+prepare C275** as the next distinct (grep-zero) real-data fail-closed costed OOS candidate to run immediately — future agents must not revert to status-only work.

## STATE SNAPSHOT (2026-11-12T06:14:27Z UTC)
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

**END OF DURABLE HANDOFF — refreshed 2026-11-12T06:14:27Z UTC (immediate mandatory heavy work = run/verify/decompose/sensitize/package C274 real-data campaign end-to-end; C273 evidence preserved, READY_FOR_REVIEW).**
