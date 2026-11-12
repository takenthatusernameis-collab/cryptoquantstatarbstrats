# DURABLE HANDOFF — CryptoQuant Stat Arb Strategies (SINGLE, NEXT SESSION STARTS HERE)

## INITIAL TASK MESSAGE — 2026-11-12T16:35:45Z UTC (AUTHORITATIVE — NEXT SESSION STARTS HERE)

**Repo-prioritized focus (re-derived from repo name `cryptoquantstatarbstrats` = crypto quant stat-arb strategies):** the only defensible, highest-value work is **real-data-only, fail-closed, costed OOS stat-arb edge VALIDATION and HARDENING**. This repo has produced **exactly ONE edge-positive family (C273 PERCENTILE_SPREAD)**; everything else (C274, C275, C276, and the 7 "C277 pool" families) is **NO EDGE**. The correct next move is **NOT** another speculative feature — it is **hardening the only real edge into (or out of) promotion** via deterministic stability testing. **Every session must advance heavy validation with verifiable artifacts (paths + SHA256 from file bytes) and update this handoff.**

### ⚠️ BOTTLENECK REMOVED — STALE "UNRUN POOL" CLAIM IS FALSE (verified 2026-11-12T16:35Z)
The prior handoff told the next agent to "execute the unrun C277 candidate pool." **That claim is factually wrong and is itself the bottleneck** — it would waste a full session re-running completed work. Verified truth:
- **All 7 pool candidates were already executed on 2026-11-06/07 and all are `oos_edge_proven:false` (NO EDGE):**
  - `reports/real_quote_volume_approximate_entropy_shock_mr_costed_oos_20261106T201839Z.json`
  - `reports/real_quote_volume_dispersion_entropy_shock_mr_costed_oos_20261107T000606Z.json` (+ `..._20261107T021053Z.json`)
  - `reports/real_quote_volume_fisher_information_shock_mr_costed_oos_20261107T001916Z.json`
  - `reports/real_quote_volume_higuchi_fd_shock_mr_costed_oos_20261106T151757Z.json`
  - `reports/real_quote_volume_hurst_rs_persistence_shock_mr_costed_oos_20261106T213620Z.json`
  - `reports/real_quote_volume_lz76_complexity_shock_mr_costed_oos_20261106T143358Z.json`
  - `reports/real_quote_volume_multiscale_sample_entropy_shock_mr_costed_oos_20261107T030455Z.json`
- **Coverage is effectively exhausted, not "one candidate away":** 49 RQA diag-line-length feature families + ~216 non-RQA volume families are already run, all NO EDGE except C273. **Do NOT add another single-feature "try the next statistic" run** — that pattern is the actual dead end.
- **No active processes. Working tree clean at `main`, up to date with origin/main.**

### IMMEDIATE MANDATORY HEAVY CAMPAIGN (NON-OPTIONAL) — C277 = C273 HARDENING / STABILITY SUITE
C273 is the **only** `oos_edge_proven:true` result, but its own robustness dossier classifies it `CONDITIONAL_EDGE_VERIFIED_BUT_REQUIRES_HARDENING_REVIEW` with documented fragility. C277 is therefore **deterministic stress/hardening of C273**, computed **only from saved real cached data** (`data/cache/`, no network, no synthetic), **reusing the exact C273 feature/params spec**, to decide **PROMOTE vs REJECT**. This is the single most decision-relevant heavy task remaining.

**C273 baseline to defend (all verified from file bytes, 2026-11-12T16:35Z):**
- OOS `reports/real_quote_volume_rqa_rte_over_white_diag_line_length_percentile_spread_shock_mr_costed_oos_20261112T050947Z.json` sha256 `1e4fd5983d29eb027336e77b2b3a5e7bda6fa6180494f0d836e5584cc298e1bf`
- Spec: W_RR=168, ALB=336, m=2, tau=1, eps_scale=0.5, w_min=2, ENTRY_Z=1.5, EXIT_Z=0.5, MAX_HOLD=24; WF train=720/test=168/step=168; cost grid [[0,0],[5,5],[10,10],[20,20],[40,40]] bps.
- Cross-asset OOS net sums: fee0 +80.68, fee5 +79.42, fee10 +78.16, fee20 +75.64, fee40 +70.60 (all >0).
- Fragility (from `campaign273_robustness_dossier_20261112T051659Z.json` sha256 `f7f51f9d84fe0f42207cfffe77e26e552ff8c10636017889fed706c029e716e6`): only 9/11 assets positive (DOT −2.18, SOL −2.22 at fee0); top1 (BNB) = 23.9% and top3 = 64.7% of positive fee0 net; **not all assets positive in every cost slice**.
- Sensitivity (`campaign273_param_sensitivity_20261112T052846Z.json` sha256 `15e4bf307b373c9c57a533dc69232d19855933ce8b7956d84e90b9f5d0e96b9d`): 21/27 edge-positive (`robust_neighborhood`); **all 6 failures are W_RR=192** (ENTRY_Z 1.25 & 1.5 → fee0 as low as −33.22, fee40 −44.78). Baseline W_RR=168 reproduces.

**C277 deliverables (ALL required, in order; each emitted with path + SHA256 from file bytes):**
1. **Cost break-even curve** — for C273 baseline, sweep total round-trip cost from 0 → 60 bps (1 bps steps) and report the **break-even cost bps** where cross-asset OOS net sum crosses 0; report net-sum and mean-per-bar at 0/5/10/20/40/break-even. Answers "is the edge real after realistic fees?"
2. **Per-asset statistical significance** — per asset, block-bootstrap (stationary/circular, ≥2000 resamples, fixed seed) the OOS net-sum distribution; report 95% CI and fraction of resamples > 0, plus a cross-asset combined p-value (e.g. sign/permutation test on the 24 WF split sums). Identify which assets are statistically indistinguishable from zero.
3. **Regime / subperiod stability** — split the OOS window chronologically into ≥3 contiguous subperiods; per subperiod report cross-asset net sum and exposure, and flag any subperiod with negative net. Tests whether the edge is time-localized (data-snooping risk).
4. **Concentration / leave-one-asset-out** — recompute cross-asset net at each cost slice dropping each of the 11 assets in turn; report the range of cross-asset net across drops (does BNB/top1 carry it?) and identify assets whose removal flips the sign.
5. **Verdict + promotion update** — emit a C277 verdict artifact: `PROMOTE_READY` only if break-even cost ≥ a stated conservative threshold (e.g. ≥20 bps) AND all subperiods non-negative AND LOO never flips cross-asset sign to negative; otherwise `NOT_PROMOTED` with the precise failing condition. Append C277 result to the handoff.

- **Reuse existing code, do not re-derive the feature:** import from `scripts/run_c273_percentile_spread_split_decomposition.py` (`_white_diag_line_length_percentile_spread`, `wf_splits`, `load_spot`, `load_volume`) and the C273 runner. Copy the exact feature/params/spec from the C273 OOS artifact. **Fail-closed:** any missing cache / non-finite / spec mismatch → abort with a clear error, never fabricate.
- **Session completion rule:** the session is NOT complete until C277 items 1–5 exist on disk as JSON with SHA256s recorded and this handoff updated. A planning-only, status-only, or "add another feature" turn FAILS this rule.

### HARD BANS
- No status-only work. No planning-only turns. No re-running any completed family (C1–C276, and all 7 "pool" families) — evidence already exists.
- No network refetch; no synthetic/fabricated data; no threshold weakening; no edits to `research_state/state.yaml` unless explicitly requested.
- No edits to the frozen C273 artifacts. C277 reads them; it does not rewrite them.
- Record all new/updated artifact SHA256s **from file bytes**.
- Do not repeat the dead-end pattern of "next single statistic feature"; the value now is decision-grade hardening of the only edge.

## STATE SNAPSHOT (verified 2026-11-12T16:35Z UTC)
- **Env:** `python3 3.12.3`; `numpy 2.5.4`, `pandas 3.1.1`, `scipy 1.18.1` (has `scipy.stats`). Ruff/mypy not installed here — skip lint/typecheck until available.
- **Data:** `data/cache/` = 68 real files; volume feed `volume_1h_full.pkl` (dict keyed by symbol) + meta + provenance; spot cache `0bab5d6a...pkl`. **No network refetch. No synthetic data.**
- **Git:** working tree clean at `main`, HEAD `df50966`, up to date with origin/main.
- **Canonical handoff:** this file only.
- **C273 (PERCENTILE_SPREAD) — CONDITIONAL_EDGE_PROVEN / READY_FOR_REVIEW (the only positive):** see OOS sha `1e4fd598...` above. Supporting artifacts: promotion MD `campaign273_promotion_evidence_package_20261112T054614Z.md`; promotion JSON `..._20261112T054614Z.json` sha256 `7aff2e6031d5ca0aa9a00c05d1320800b13cc767328df4c5664b9b5964c0975c`; split `campaign273_split_decomposition_20261112T052106Z.json` sha256 `2b4da1e685cee4eb8033e37d6a2844ba9639b7b3ba69b92c50ef7ea4a95a707d`; verification `campaign273_verification_20261112T051659Z.json` (verification_passed:true).
- **C274/C275/C276 — NO EDGE (preserved):** C274 SECOND_PEARSON_SKEW (0/27 edge-positive); C275 MEDCOUPLE (verification_passed:true, all slices −0.4833); C276 FIRST_PEARSON_SKEW (verification_passed:true, all slices −0.4833). No action needed.
- **C277 (C273 HARDENING SUITE) — PENDING:** no artifacts yet; this session's sole mandated deliverable.

**END OF DURABLE HANDOFF — refreshed 2026-11-12T16:35:45Z UTC.**