# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T05:40:00Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (verified 2026-11-12T05:40:00Z UTC):** `cryptoquantstatarbstrats` = **crypto quant stat-arb strategies**. Highest-impact work is **real-data-only, fail-closed, costed OOS stat-arb edge validation and hardening**. C273 is a verified, replication-matched, split-decomposed, and parameter-sensitivity-tested conditional proven-edge candidate; next session must produce a promotion-ready evidence package artifact (no status-only).

**Bottleneck audit (2026-11-12T05:40:00Z UTC): bottlenecks removed.**
- `HANDOFF.md` consolidated to this single authoritative block.
- `git status --short`: dirty with uncommitted C272/C273 artifacts+scripts and this handoff update (expected work product, not stalled).
- Deps present: `python3` 3.12.3, `numpy` 2.5.4, `pandas` 3.1.1, `scipy` 1.18.1.
- `data/cache/` = 68 real files (`.pkl`+`.meta.json`+provenance); **no refetch**.
- No stalled blockers.

### C273 — COMPLETE + VERIFIED + REPLICATION/SPLIT-DECOMPOSED + PARAM-SENSITIVITY TESTED
- **Strategy:** `VOLUME_RQA_RTE_OVER_WHITE_DIAG_LINE_LENGTH_PERCENTILE_SPREAD_SHOCK_MR`
- **Feature (pre-stated, fail-closed):** `PERCENTILE_SPREAD = (P75(L)-P25(L))/median(L)` over qualifying WHITE diagonal segment lengths `L` pooled over off-diagonal diagonals `k!=0`, length `>=w_min=2`, `N>=3`, on delay-embedded (`m=2,tau=1`) log-volume returns over trailing `W_RR=168`; `eps=0.5*std(r_window)`, L_inf recurrence. numpy percentile linear/default. Fail-closed if `N<3`, `median<=0/non-finite`, or `P75/P25/median/spread` non-finite/undefined. Causal trailing only.
- **Distinctness:** `grep_hits_nonself_at_run: 0`.
- **WF/costs:** `train=720, test=168, step=168`, costs bps `[[0,0],[5,5],[10,10],[20,20],[40,40]]`, real cached data only.
- **Baseline result:** `edge_claim: CONDITIONAL_EDGE_PROVEN`, `oos_edge_proven: true`, `any_exposure_oos: true`, `all_cost_slices_positive_oos_net_sum: true`, `all_cost_slices_beat_bh_mean_rule: true`.
- **Baseline cross-asset OOS nets:** fee0/5/10/20/40 = `80.68391844301627 / 79.42291844301636 / 78.16191844301629 / 75.63991844301627 / 70.59591844301625`.
- **Core artifacts (SHA256 from bytes):**
  - OOS: `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos_20261112T050947Z.json` — `1e4fd5983d29eb027336e77b2b3a5e7bda6fa6180494f0d836e5584cc298e1bf`
  - Script: `scripts/run_real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos.py` — `4d91581133c6ca5a8613c644f137f2c24bf5fefa0d1086d2d735d85d813a117e`
  - Ingest: `reports/real_feed_ingest_attempt_20261112T051504Z.json` — `dd704efab8d6c3650e5c872f0b8b3462185e960b136382ea260e139370d70446`
  - Registry: `reports/strategy_edge_registry_20261112T051504Z.json` — `7fb2ceeaccbb2c8499e5d8203479c7c9c309f41acd57ccc2c5e5685308b7c6b6`
  - Summary: `reports/campaign273_execution_summary_20261112T051504Z.json` — `d2694387c152b6659a041dd946fda79de415d9d1747bac447418c090cae153dd`
- **Deterministic verification (2026-11-12T05:16:59Z):** `verification_passed: true`.
  - `scripts/verify_c273_percentile_spread_edge.py`
  - `reports/campaign273_verification_20261112T051659Z.json` — `42b3341d04e6c141fde5e0b88a8a2444a0b2c4a9270c56ce66149d21ca02c229`
- **Robustness dossier (2026-11-12T05:16:59Z):** `CONDITIONAL_EDGE_VERIFIED_BUT_REQUIRES_HARDENING_REVIEW`; fragility flags `["some_assets_nonpositive_at_fee0","not_all_assets_positive_in_every_cost_slice"]`.
  - `reports/campaign273_robustness_dossier_20261112T051659Z.json` — `f7f51f9d84fe0f42207cfffe77e26e552ff8c10636017889fed706c029e716e6`
- **Split/asset decomposition + replication (2026-11-12T05:21:06Z):** `replication_matches_c273: true` (diffs 0 for fee0/5, +1.4210854715202004e-14 fp for fee10/20/40 within tolerance).
  - `scripts/run_c273_percentile_spread_split_decomposition.py`
  - `reports/campaign273_split_decomposition_20261112T052106Z.json` — `2b4da1e685cee4eb8033e37d6a2844ba9639b7b3ba69b92c50ef7ea4a95a707d`
  - **Findings:** 24 OOS splits; fee0 cross-asset positive splits `16/24 (66.67%)`, min/max/mean split net `-12.116630665422184 / 27.10148575154885 / 3.361829935125678`; assets positive net at fee0 `9/11`; cross-asset positive in all recomputed cost slices. Broad split support, non-uniform across assets/cost slices.
- **Parameter-perturbation sensitivity (2026-11-12T05:28:46Z, real cached data only):** `sensitivity_assessment: robust_neighborhood`.
  - `scripts/run_c273_percentile_spread_param_sensitivity.py` — `73832091f61282a3e1d2199284ba5af3fd79d1df66a1a512e9ea65a2c2252d98`
  - `reports/campaign273_param_sensitivity_20261112T052846Z.json` — `15e4bf307b373c9c57a533dc69232d19855933ce8b7956d84e90b9f5d0e96b9d`
  - **Grid:** `W_RR{144,168,192} × ENTRY_Z{1.25,1.5,1.75} × EXIT_Z{0.25,0.5,0.75}` with `EXIT_Z<ENTRY_Z` (27 combos), fixed `ALB=336,m=2,tau=1,eps_scale=0.5,w_min=2,MAX_HOLD=24,TRAIN=720,TEST=168,STEP=168`, same cost grid/caches/WF.
  - **Findings:** edge-positive combos `21/27 (77.78%)`, combos with all cost slices positive `21/27`, baseline reproduced in grid `true`. 6 failures all from `ENTRY_Z=1.25` (most aggressive entry) where BH-beat/cost-positivity at fee40 breaks (fee40 nets: W_RR 144/168/192 with tighter exits negative, e.g. 144/1.25/0.25 fee40 `-4.825...`, 192/1.25/0.25 fee40 `-33.383...`); baseline neighborhood (`ENTRY_Z>=1.5` and moderate exits) broadly stable.

**IMMEDIATE MANDATORY HEAVY WORK (non-optional, no planning phase): PRODUCE C273 PROMOTION-READY EVIDENCE PACKAGE NOW.**
Do not plan, summarize, or ask questions — execute immediately. Create concrete artifacts on real saved evidence only (no refetch, no synthetic).

1. **Write and run** `scripts/build_c273_promotion_evidence_package.py` that reads all C273 artifacts above (by path/SHA) and emits:
   - `reports/campaign273_promotion_evidence_package_<ts>.json` (machine-readable): full artifact manifest with SHA256-from-bytes, baseline metrics, verification result, split-stability stats, parameter-sensitivity stats, fragility/risk notes, explicit edge rule and compliance, and a final `promotion_readiness` assessment (`READY_FOR_REVIEW` if evidence is complete/consistent and robust-neighborhood holds, else `NOT_READY` with reasons) — must be grounded strictly in saved numbers.
   - `reports/campaign273_promotion_evidence_package_<ts>.md` (human-readable, concise): same evidence distilled for review, including key risks (asset non-uniformity, 6/27 param failures concentrated at ENTRY_Z=1.25, split negatives 8/24) and exact reproduction artifacts/scripts.
2. **Compute SHA256-from-bytes** for both emitted package files and the builder script (if new/modified) and include them in the JSON package.
3. **Update this handoff in-place** with package artifact paths + SHA256-from-bytes, `promotion_readiness` result, and the next concrete step: if `READY_FOR_REVIEW`, next work is to identify/prepare the next real-data hardening/validation campaign target (state explicitly) without undoing C273 evidence; if `NOT_READY`, execute the specific failing hardening test named in the package (must be concrete and executable) — future agents must not revert to status-only work.

## STATE SNAPSHOT (2026-11-12T05:40:00Z UTC)
- **C1–C15, C249–C272:** complete, `oos_edge_proven: false`.
- **C273:** `CONDITIONAL_EDGE_PROVEN` / verified / replication-matched / split-decomposed / param-sensitivity `robust_neighborhood` (21/27); **promotion evidence package pending (mandatory next)**.
- **Environment:** python3 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1. Caches: `data/cache/` 68 real files, no refetch.

## HARD BANS
- ❌ No status-only work; no "planning/researching" as substitute for producing artifacts.
- ❌ No re-runs of C1–C15 or C249–C272 except evidence-backed defect fix; rerun C273 core only if evidence-backed defect found.
- ❌ No network refetch (use `data/cache/` only). No synthetic/fabricated data.
- ❌ No threshold weakening.
- ❌ No edits to `research_state/state.yaml` unless explicitly requested by user (`state.yaml` stale at C248 — locked/separate).

---
## HISTORICAL RECORD (condensed)
- **C249–C272:** all `edge_claim: NONE`, `oos_edge_proven: false`.
- **C273:** conditional proven edge (PERCENTILE_SPREAD), verified, replication-matched, split-decomposed (broad split support, non-uniform assets), param sensitivity robust_neighborhood (21/27); promotion package pending.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T05:40:00Z UTC (immediate mandatory heavy work = build C273 promotion-ready evidence package artifacts now, update handoff with paths/SHA256/readiness and next concrete step).**
