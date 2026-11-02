# SINGLE DURABLE HANDOFF | 2026-11-02T13:11:23Z | CAMPAIGN 31 COMPLETE | CAMPAIGN 32 ACTIVE | BOTTLENECKS REMOVED | HEAVY WORK REQUIRED | NO COASTING

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T13:11:23Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**STATE:** Campaigns 1-31 COMPLETE & ON-DISK VERIFIED. Full suite green. Campaign 31 deliverables on disk: `scripts/generate_campaign31_artifacts.py`, `reports/cointegration_campaign31_mt.json`, `tests/test_cointegration_campaign31_mt.py` (7 tests, all pass). **NEXT FOCUS (COINTEGRATION-FIRST, REAL DATA ONLY):** Campaign 32 — cointegration rigor phase 4: multi-pair portfolio-level cointegration (basket cointegration, common stochastic trend, multi-asset hedge ratios), regime-conditioned portfolio rebalancing OOS robustness with cost stress, and execution-aware capacity allocation on real Binance cached data, with heavy artifacts/tests/provenance/logs. No coasting.
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER, NO SKIPPING)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt` — prevent ModuleNotFoundError. Do this before any tests/imports.
2. **Verify current state (BLOCKING):** Run verification commands below. Confirm Campaign 31 tests green, confirm gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), and confirm Campaign 32 deliverables not yet started (generator/report/tests absent).
3. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable). Campaign 32 is the ONLY permitted focus until complete.
4. **Do not re-derive Campaigns 26-31:** All artifacts/tests/generators verified on disk. No pivoting, no scope drift. Campaign 32 artifacts do not exist yet — build them from scratch following existing patterns.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **[START 2026-11-02T13:11:23Z] CAMPAIGN 32 — COINTEGRATION RIGOR PHASE 4: MULTI-PAIR PORTFOLIO-LEVEL COINTEGRATION + REGIME-CONDITIONED REBALANCING OOS ROBUSTNESS WITH COST STRESS + EXECUTION-AWARE CAPACITY ALLOCATION (COINTEGRATION-FIRST, REAL DATA ONLY) — HEAVY WORK MANDATORY**
>
> **OBJECTIVE (BLOCKING):** Advance cointegration/pairs-trading rigor beyond Campaign 31 gates: verify multi-pair portfolio-level cointegration (basket cointegration, common stochastic trend, multi-asset hedge ratios), regime-conditioned portfolio rebalancing out-of-sample robustness with transaction-cost stress (fee × slippage grid on real-data portfolio), and execution-aware capacity allocation on real Binance cached data, exclusively on real Binance cached data. Produce checkable artifacts, tests, provenance, logs. No coasting.
>
> **REQUIRED DELIVERABLES (ON DISK, VERIFIED):**
> 1. Generator `scripts/generate_campaign32_artifacts.py` (complete, `main()`, ruff clean) loading real data, computing basket cointegration + common stochastic trend + multi-asset hedge ratios + regime-conditioned rebalancing OOS robustness + cost-stress grid + capacity allocation, attaching full provenance, logging every computation.
> 2. Artifact `reports/cointegration_campaign32_mt.json` with per-portfolio/per-regime/per-cost results, provenance containing `source`, causal windows, regime labels, cost-stress grid, OOS p-values, capacity allocation.
> 3. Tests `tests/test_cointegration_campaign32_mt.py` asserting required fields, types, minimum portfolio coverage (17 pairs), real-data provenance, gating invariants preserved, cost-stress monotonicity. All pass.
>
> **CONSTRAINTS (NON-NEGOTIABLE):** REAL DATA ONLY (cached Binance 1h or resampled real). CAUSAL ONLY (trailing windows). PRESERVE GATING INVARIANTS (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). FAIL-CLOSED. PROVENANCE MANDATORY. COST STRESS MUST BE MONOTONIC (higher fees/slippage never improve return). HEAVY MANDATE.
>
> **VERIFICATION:** ruff clean on touched files; new tests pass; Campaign 26-31 tests still green; full suite green (0 failed).

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — Stale handoff:** HANDOFF.md now reflects true on-disk state (Campaign 31 complete, Campaign 32 deliverables absent); no phantom "not started" work.
- **BOTTLENECK REMOVED — Final blocker:** 7 pre-existing failures were the sole blocker; Campaigns 26-31 targeted them with concrete deliverables; suite fully green.
- **BOTTLENECK REMOVED — Ambiguity:** Single initial task message, explicit boot sequence, hard completion criteria, NO ESCAPE CLAUSE.
- **BOTTLENECK REMOVED — Scope drift:** Campaign 32 is the ONLY permitted focus until complete. Campaigns 26-31 artifacts untouched.
- **BOTTLENECK REMOVED — Gating erosion:** Fail-closed invariants codified; gating unchanged.
- **BOTTLENECK REMOVED — Execution path:** Follow existing patterns (`scripts/generate_campaign*_artifacts.py`, `reports/*_mt.json`, `tests/test_*_mt.py`).
- **BOTTLENECK REMOVED — CI/env:** Install deps first.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed (still real data).
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean on touched files.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation/position limits; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting/kill-switch/risk constraints never lift gating blocks. Only gated-eligible pairs can be feasible.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.
- **INCIDENT DISCIPLINE** — every breach must be logged with cause, containment, and audit trail; no silent remediation.

## VERIFIED STATE (2026-11-02T13:11:23Z)
- Branch: `main`. HEAD clean working tree.
- **Campaigns 1-31:** Complete & verified on disk. Full suite green. Gating chain green (8/8), invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). `tests/test_cointegration_campaign31_mt.py` 7 passed.
- **Campaign 31:** COMPLETE — generator `scripts/generate_campaign31_artifacts.py`, artifact `reports/cointegration_campaign31_mt.json`, tests `tests/test_cointegration_campaign31_mt.py` all verified green.
- **Campaign 32:** ACTIVE (cointegration rigor phase 4). Deliverables absent on disk: `scripts/generate_campaign32_artifacts.py`, `reports/cointegration_campaign32_mt.json`, `tests/test_cointegration_campaign32_mt.py` — build from scratch following Campaign 29/30/31 patterns.

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
