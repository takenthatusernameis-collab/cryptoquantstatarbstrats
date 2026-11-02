# SINGLE DURABLE HANDOFF | 2026-11-02T13:11:42Z | CAMPAIGN 31 COMPLETE | CAMPAIGN 32 ACTIVE | BOTTLENECKS REMOVED | HEAVY WORK REQUIRED | NO COASTING

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T13:11:42Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**STATE:** Campaigns 1-31 COMPLETE & ON-DISK VERIFIED. Full suite green. Campaign 31 deliverables on disk: `scripts/generate_campaign31_artifacts.py`, `reports/cointegration_campaign31_mt.json`, `tests/test_cointegration_campaign31_mt.py` (7 tests, all pass). **NEXT FOCUS (COINTEGRATION-FIRST, REAL DATA ONLY):** Campaign 32 — cointegration rigor phase 4: multi-pair portfolio-level cointegration (basket cointegration, common stochastic trend, multi-asset hedge ratios), regime-conditioned portfolio rebalancing OOS robustness with cost stress, and execution-aware capacity allocation on real Binance cached data, with heavy artifacts/tests/provenance/logs. No coasting.
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER, NO SKIPPING)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt` — prevent ModuleNotFoundError. Do this before any tests/imports.
2. **Verify current state (BLOCKING):** Run verification commands below. Confirm Campaign 31 tests green, confirm gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), and confirm Campaign 32 deliverables do **not** exist yet (generator/report/tests absent).
3. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable). Campaign 32 is the **ONLY** permitted focus until complete.
4. **Follow existing patterns:** Mirror `scripts/generate_campaign31_artifacts.py`, `reports/cointegration_campaign31_mt.json`, and `tests/test_cointegration_campaign31_mt.py`. Do **not** re-derive Campaigns 26-31.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **[START 2026-11-02T13:11:42Z] CAMPAIGN 32 — COINTEGRATION RIGOR PHASE 4: MULTI-PAIR PORTFOLIO-LEVEL COINTEGRATION + REGIME-CONDITIONED REBALANCING OOS ROBUSTNESS WITH COST STRESS + EXECUTION-AWARE CAPACITY ALLOCATION (COINTEGRATION-FIRST, REAL DATA ONLY) — HEAVY WORK MANDATORY**
>
> **OBJECTIVE (BLOCKING):** Advance cointegration/pairs-trading rigor beyond Campaign 31. Treat the 17-pair universe as a **portfolio** and prove/quantify portfolio-level cointegration: test for **basket cointegration / common stochastic trend(s)** (Johansen on the system or equivalent), estimate **multi-asset hedge ratios / portfolio spreads**, assess **portfolio cointegration stability** across regimes/timeframes, and demonstrate how this constrains tradable capacity. Evaluate **regime-conditioned portfolio rebalancing** with **walk-forward OOS robustness** and a **monotonic fee × slippage cost-stress grid** on real Binance cached data. Enforce **execution-aware capacity allocation** (liquidity/participation-aware, fail-closed) that cannot lift gating blocks. Exclusively use real Binance cached data (1h; resample allowed only if derived from real data). No fabrication.
>
> **REQUIRED DELIVERABLES (ON DISK, VERIFIED):**
> 1. **Generator** `scripts/generate_campaign32_artifacts.py` (complete, `main()`, ruff clean). Load real cached data for all symbols in the 17 pairs. Compute basket/multi-pair cointegration (Engle-Granger/Johansen as appropriate), common stochastic trend evidence, multi-asset hedge ratios/portfolio spreads, regime labels (BTC vol/trend via `utils.regime`), regime-conditioned portfolio rebalancing OOS (walk-forward), cost-stress grid (fee × slippage), and execution-aware capacity allocation. Attach **full provenance** (source, real_data_only, fabricated_data, computed_at, blocked_routes, rationale), log every computation step, and never fabricate values on blocked routes.
> 2. **Artifact** `reports/cointegration_campaign32_mt.json` with per-portfolio, per-regime, per-cost-stress, and per-timeframe results. Must include provenance, causal windows (trailing only), gating invariants preserved, regime definitions, cost grid, OOS metrics, basket cointegration tests, common stochastic trend evidence, multi-asset hedge ratios, portfolio spreads, rebalancing robustness, and execution-aware capacity allocation. Must be JSON-serializable with **no NaN/Inf**.
> 3. **Tests** `tests/test_cointegration_campaign32_mt.py` asserting schema, required sections/fields/types, minimum portfolio coverage (all 17 pairs represented), real-data provenance on all sections, **gating invariants preserved exactly** (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed behavior, **cost-stress monotonicity** (higher fees/slippage must not improve returns/Sharpe), blocked pairs carry zero feasible capacity/weight, NaN/Inf checks, and campaign flags. **All tests must pass**.
>
> **CONSTRAINTS (NON-NEGOTIABLE):** REAL DATA ONLY. CAUSAL ONLY (trailing windows, no lookahead). PRESERVE GATING INVARIANTS (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). FAIL-CLOSED. PROVENANCE MANDATORY ON EVERY COMPUTED SECTION. COST STRESS MUST BE MONOTONIC (higher fees/slippage never improve performance). NO AUTO-LIFT OF BLOCKS. NO FABRICATION. HEAVY MANDATE.
>
> **VERIFICATION (BLOCKING):** `ruff check` clean on touched files; `pytest tests/test_cointegration_campaign32_mt.py -v` passes; Campaign 26-31 tests still green; `pytest tests/ -q` remains green (0 failed).

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — Stale/ambiguous handoff:** HANDOFF.md reflects true on-disk state (Campaign 31 complete, Campaign 32 deliverables absent). Single timestamped initial task message with no ambiguity.
- **BOTTLENECK REMOVED — Final blocker history:** Prior 7 failures resolved by targeted campaigns; full suite green. Treat green as invariant to preserve.
- **BOTTLENECK REMOVED — Scope drift:** Campaign 32 is the **ONLY** permitted focus until complete. Campaigns 26-31 artifacts untouched.
- **BOTTLENECK REMOVED — Gating erosion:** Gating invariants codified and must be asserted by tests. Fail-closed enforced.
- **BOTTLENECK REMOVED — Execution path:** Follow proven patterns (`scripts/generate_campaign*_artifacts.py`, `reports/*_mt.json`, `tests/test_*_mt.py`).
- **BOTTLENECK REMOVED — CI/env:** Install deps first in boot sequence.
- **BOTTLENECK REMOVED — Coasting:** Heavy mandate, explicit deliverables, blocking verification, and "no escape clause" stated.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed only if derived from real data.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean on touched files.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation/position limits; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting/kill-switch/risk constraints never lift gating blocks. Only gated-eligible pairs can be feasible.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.
- **INCIDENT DISCIPLINE** — every breach must be logged with cause, containment, and audit trail; no silent remediation.

## VERIFIED STATE (2026-11-02T13:11:42Z)
- Branch: `main`. HEAD clean working tree.
- **Campaigns 1-31:** Complete & verified on disk. Full suite green. Gating chain green (8/8), invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). `tests/test_cointegration_campaign31_mt.py` 7 passed.
- **Campaign 31:** COMPLETE — generator `scripts/generate_campaign31_artifacts.py`, artifact `reports/cointegration_campaign31_mt.json`, tests `tests/test_cointegration_campaign31_mt.py` all verified green.
- **Campaign 32:** ACTIVE (cointegration rigor phase 4). Deliverables **absent** on disk: `scripts/generate_campaign32_artifacts.py`, `reports/cointegration_campaign32_mt.json`, `tests/test_cointegration_campaign32_mt.py` — build from scratch following Campaign 29/30/31 patterns.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m pip install -r requirements.txt
python -m pytest tests/test_cointegration_campaign31_mt.py -v
python -m pytest tests/test_end_to_end_pairs_execution_validation_mt.py tests/test_live_operational_readiness_signoff_mt.py tests/test_live_go_live_authorization_final_mt.py tests/test_post_deployment_live_readiness_signoff_mt.py -v
python -m pytest tests/test_portfolio_real.py tests/test_portfolio_real_hardened.py tests/test_tail_risk_parameter_stability.py -v
python3 -c "
import json
g=json.load(open('reports/portfolio_gating_mt.json'))['results_by_timeframe']
for tf in ['1h','4h','1d']:
    elig=g[tf].get('eligible_pairs',g[tf].get('feasible_pairs',{}))
    print(tf,'eligible:',len(elig),list(elig.keys()) if isinstance(elig,dict) else elig)
"
python -m pytest tests/ -q
```

## CAMPAIGN HISTORY (CONCISE)
- **Campaign 26 (complete):** E2E pairs execution validation + live operational readiness signoff.
- **Campaign 27 (complete):** Final live go-live authorization + post-deployment live readiness signoff.
- **Campaign 28 (complete):** Portfolio_real enrichment → full green suite.
- **Campaign 29 (complete):** Cointegration rigor deepening — OOS stability, causal rolling diagnostics, pairs robustness.
- **Campaign 30 (complete):** Cointegration rigor phase 2 — Johansen rank stability, structural-break discipline, HL favorability bands, walk-forward OOS pairs execution robustness.
- **Campaign 31 (complete):** Cointegration rigor phase 3 — cross-timeframe regime-conditioned cointegration + execution-aware OOS pairs with cost stress.
- **Campaign 32 (ACTIVE):** Cointegration rigor phase 4 — multi-pair portfolio-level cointegration + regime-conditioned rebalancing OOS robustness with cost stress + execution-aware capacity allocation.
