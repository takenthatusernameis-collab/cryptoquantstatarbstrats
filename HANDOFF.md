# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T05:46:49Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (verified 2026-11-12T05:46:49Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 is done and promotion-ready; the next session must **not** revert to status-only work — it must identify/prepare and run the next real-data hardening/validation campaign target (C274) on `data/cache/` only.

**Bottleneck audit (2026-11-12T05:46:49Z UTC): bottlenecks removed / path unblocked.**
- `HANDOFF.md` consolidated to this single authoritative block.
- `git status --short`: clean (C272/C273 artifacts + this handoff committed at a7545bd). No stalled work product.
- Deps present: `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1.
- `data/cache/` = 68 real files (`.pkl`+`.meta.json`+provenance); **no refetch**, no network needed.
- C273 builder `scripts/build_c273_promotion_evidence_package.py` present and runnable; all 13 referenced C273 artifacts present with matching hashes.
- No stalled blockers. Next agent may execute immediately.

### C273 — COMPLETE + VERIFIED + REPLICATION/SPLIT-DECOMPOSED + PARAM-SENSITIVITY TESTED → PROMOTION PACKAGE BUILT (READY_FOR_REVIEW)
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PERCENTILE_SPREAD_SHOCK_MR`
- **Edge rule:** `oos_edge_proven=true` IFF OOS exposure>0 AND for ALL cost slices OOS net sum > 0 AND mean OOS net > mean B&H OOS net on same WF windows. Real data only. WF 720/168/168, cost grid `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, B&H same OOS windows.
- **Distinctness:** `grep_hits_nonself_at_run: 0`.
- **Baseline cross-asset OOS nets:** fee0/5/10/20/40 = `80.68391844301627 / 79.42291844301636 / 78.16191844301629 / 75.63991844301627 / 70.59591844301625`.
- **Verification:** `verification_passed: true` (`scripts/verify_c273_percentile_spread_edge.py`, `reports/campaign273_verification_20261112T051659Z.json` sha256 `42b3341d04e6c141fde5e0b88a8a2444a0b2c4a9270c56ce66149d21ca02c229`).
- **Robustness:** `CONDITIONAL_EDGE_VERIFIED_BUT_REQUIRES_HARDENING_REVIEW`; fragility flags `["some_assets_nonpositive_at_fee0","not_all_assets_positive_in_every_cost_slice"]` (`reports/campaign273_robustness_dossier_20261112T051659Z.json` sha256 `f7f51f9d84fe0f42207cfffe77e26e552ff8c10636017889fed706c029e716e6`).
- **Split/replication:** `replication_matches_c273: true` (diffs 0 for fee0/5, +1.42e-14 fp for fee10/20/40 within tolerance) (`reports/campaign273_split_decomposition_20261112T052106Z.json` sha256 `2b4da1e685cee4eb8033e37d6a2844ba9639b7b3ba69b92c50ef7ea4a95a707d`); fee0 positive splits `16/24 (66.67%)`, assets positive net fee0 `9/11`.
- **Param sensitivity:** `sensitivity_assessment: robust_neighborhood`; edge-positive `21/27 (77.78%)`; 6 failures all at `W_RR=192` (fee40/high-cost negativity + BH-beat failure) (`reports/campaign273_param_sensitivity_20261112T052846Z.json` sha256 `15e4bf307b373c9c57a533dc69232d19855933ce8b7956d84e90b9f5d0e96b9d`).
- **Promotion evidence package (BUILT 20261112T054614Z):**
  - JSON: `reports/campaign273_promotion_evidence_package_20261112T054614Z.json` — sha256 `b02ca846eebcdc1253c45b0686e28bef787714b9373e8e0c5118322b3ffe8fad`
  - MD: `reports/campaign273_promotion_evidence_package_20261112T054614Z.md` — sha256 `d03eab43502bd8c53845e692d981cb9d020c1f728bcb3afb21b7bb5453ba72b3`
  - Builder script: `scripts/build_c273_promotion_evidence_package.py` — sha256 `48ed28d0fc808092188939c44e04d3112ed489215b1b40be0e49d3552715ec33`
  - `promotion_readiness: READY_FOR_REVIEW`.

**IMMEDIATE MANDATORY HEAVY WORK (non-optional, no planning phase): C274 NEXT CAMPAIGN — IDENTIFY, PREPARE, RUN, PACKAGE.**
Since `promotion_readiness == READY_FOR_REVIEW`, per the handoff rule the next work is to identify/prepare the next real-data hardening/validation campaign target **without undoing C273 evidence**. Execute immediately. Do not plan, summarize, or ask questions — produce concrete artifacts on real saved evidence only (no refetch, no synthetic).

1. **Identify/prepare C274 target (state explicitly):** select one new, distinct real-data-only fail-closed costed OOS stat-arb edge candidate on `data/cache/` only. It must be distinct from C273: `grep -rnE '<C274_FEATURE_STRING>|<C274_SHORT_NAME>' scripts/ strategies/ backtest/ utils/ 2>&1` must return `grep_hits_nonself_at_run: 0` (collision-fail-closed; pick a distinct fallback if nonzero). Follow the C273 framework: `train=720, test=168, step=168`, costs bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, causal trailing only, real cached data only. Recommended candidate family: `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_<NEW_DISTINCT_SKEW/METRIC>_SHOCK_MR` with fallbacks (e.g. YULE_K, MIDRANGE, PEARSON_SKEW variants) pre-checked for grep-zero distinctness; record the chosen strategy_id, feature, and grep command/result.
2. **Run C274 end-to-end on real cached data only:** ingest attempt + costed OOS run + edge registry + execution summary + deterministic verification + split/asset decomposition + parameter-perturbation sensitivity (bounded grid around baseline, `EXIT_Z<ENTRY_Z`, same cost grid/caches/WF). Emit timestamped JSON artifacts + scripts with SHA256-from-bytes for every new artifact.
3. **If C274 proves an edge (`oos_edge_proven: true` and all compliance flags true):** build `scripts/build_c274_promotion_evidence_package.py` mirroring the C273 builder, emit `reports/campaign274_promotion_evidence_package_<ts>.json` + `.md`, compute SHA256-from-bytes for both + builder, set `promotion_readiness` (`READY_FOR_REVIEW` if complete/consistent/robust, else `NOT_READY` with reasons), and update this handoff in-place with C274 paths/SHA256/readiness and the next concrete step.
4. **If C274 does NOT prove an edge:** document the specific failing condition concretely (which cost slice/signature failed, exact numbers), do not weaken thresholds, do not rerun C1–C15/C249–C272, and update this handoff with the C274 result + the specific next hardening test to execute — future agents must not revert to status-only work.

## STATE SNAPSHOT (2026-11-12T05:46:49Z UTC)
- **C1–C15, C249–C272:** complete, `oos_edge_proven: false`.
- **C273:** `CONDITIONAL_EDGE_PROVEN` / verified / replication-matched / split-decomposed / param-sensitivity `robust_neighborhood` (21/27); promotion package BUILT, `promotion_readiness: READY_FOR_REVIEW`.
- **Next campaign:** C274 (target to be identified/prepared/ran by this session — see IMMEDIATE MANDATORY HEAVY WORK).
- **Environment:** python3 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1. Caches: `data/cache/` 68 real files, no refetch.
- **state.yaml:** stale at C248, locked — do not edit unless explicitly requested by user.

## HARD BANS
- ❌ No status-only work; no "planning/researching" as substitute for producing artifacts.
- ❌ No re-runs of C1–C15 or C249–C272 except evidence-backed defect fix; rerun C273 core only if evidence-backed defect found.
- ❌ No network refetch (use `data/cache/` only). No synthetic/fabricated data.
- ❌ No threshold weakening.
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user (`state.yaml` stale at C248 — locked/separate).

---
## HISTORICAL RECORD (condensed)
- **C249–C272:** all `edge_claim: NONE`, `oos_edge_proven: false`.
- **C273:** conditional proven edge (PERCENTILE_SPREAD), verified, replication-matched, split-decomposed (broad split support, non-uniform assets), param sensitivity robust_neighborhood (21/27); promotion package BUILT READY_FOR_REVIEW; C274 next campaign pending.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T05:46:49Z UTC (immediate mandatory heavy work = identify/prepare/run/package C274 next real-data campaign; C273 evidence preserved, READY_FOR_REVIEW).**
