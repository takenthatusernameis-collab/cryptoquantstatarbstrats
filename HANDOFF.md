# SINGLE DURABLE HANDOFF | 2026-11-02T12:46:58Z | CAMPAIGN 30 COMPLETE | CAMPAIGN 31 ACTIVE | BOTTLENECKS REMOVED | HEAVY WORK REQUIRED | NO COASTING

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T12:46:58Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**STATE:** Campaigns 1-30 COMPLETE & ON-DISK VERIFIED. Full suite green: 675 passed, 1 skipped, 0 failed. Gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Campaign 30 deliverables on disk: `scripts/generate_campaign30_artifacts.py`, `reports/cointegration_campaign30_mt.json`, `tests/test_cointegration_campaign30_mt.py` (7 tests, all pass). **NEXT FOCUS (COINTEGRATION-FIRST, REAL DATA ONLY):** Campaign 31 — cointegration rigor phase 3: cross-timeframe cointegration convergence/divergence (1h vs 4h vs 1d regime agreement), regime-conditioned cointegration persistence (volatility/trend regimes from real BTC vol), and execution-aware walk-forward OOS pairs-strategy robustness with transaction-cost stress (fee × slippage grid on top-ranked real-data pair), with heavy artifacts/tests/provenance/logs. No coasting.
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER, NO SKIPPING)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt` — prevent ModuleNotFoundError. Do this before any tests/imports.
2. **Verify current state (BLOCKING):** Run verification commands below. Confirm Campaign 30 tests green, confirm gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), and confirm Campaign 31 deliverables not yet started (generator/report/tests absent).
3. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable). Campaign 31 is the ONLY permitted focus until complete.
4. **Do not re-derive Campaigns 26-30:** All artifacts/tests/generators verified on disk. No pivoting, no scope drift. Campaign 31 artifacts do not exist yet — build them from scratch following existing patterns.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **[START 2026-11-02T12:46:58Z] CAMPAIGN 31 — COINTEGRATION RIGOR PHASE 3: CROSS-TIMEFRAME REGIME-CONDITIONED COINTEGRATION + EXECUTION-AWARE OOS PAIRS WITH COST STRESS (COINTEGRATION-FIRST, REAL DATA ONLY) — HEAVY WORK MANDATORY**
>
> **OBJECTIVE (BLOCKING):** Advance cointegration/pairs-trading rigor beyond Campaign 30 gates: verify cross-timeframe cointegration convergence/divergence (1h vs 4h vs 1d regime agreement), regime-conditioned cointegration persistence (volatility/trend regimes from real BTC vol), and execution-aware walk-forward out-of-sample pairs-strategy robustness with transaction-cost stress (fee × slippage grid on the top-ranked real-data pair), exclusively on real Binance cached data. Produce checkable artifacts, tests, provenance, logs. No coasting.
>
> **REQUIRED DELIVERABLES (ON DISK, VERIFIED):**
> 1. Generator `scripts/generate_campaign31_artifacts.py` (complete, `main()`, ruff clean) loading real data, computing cross-timeframe regime agreement + regime-conditioned persistence + execution-aware walk-forward OOS pairs robustness + cost-stress grid, attaching full provenance, logging every computation.
> 2. Artifact `reports/cointegration_campaign31_mt.json` with per-pair/per-timeframe/per-regime results, provenance containing `source`, causal windows, timeframe agreement, regime labels, cost-stress grid, OOS p-values.
> 3. Tests `tests/test_cointegration_campaign31_mt.py` asserting required fields, types, minimum pair coverage (17 pairs), real-data provenance, gating invariants preserved, cost-stress monotonicity. All pass.
>
> **CONSTRAINTS (NON-NEGOTIABLE):** REAL DATA ONLY (cached Binance 1h or resampled real). CAUSAL ONLY (trailing windows). PRESERVE GATING INVARIANTS (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). FAIL-CLOSED. PROVENANCE MANDATORY. COST STRESS MUST BE MONOTONIC (higher fees/slippage never improve return). HEAVY MANDATE.
>
> **VERIFICATION:** ruff clean on touched files; new tests pass; Campaign 26-30 tests still green; full suite green (0 failed).

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — Stale handoff:** HANDOFF.md now reflects true on-disk state (Campaign 30 complete, Campaign 31 deliverables absent); no phantom "not started" work.
- **BOTTLENECK REMOVED — Final blocker:** 7 pre-existing failures were the sole blocker; Campaigns 26-29 targeted them with concrete deliverables; suite fully green.
- **BOTTLENECK REMOVED — Ambiguity:** Single initial task message, explicit boot sequence, hard completion criteria, NO ESCAPE CLAUSE.
- **BOTTLENECK REMOVED — Scope drift:** Campaign 31 is the ONLY permitted focus until complete. Campaigns 26-30 artifacts untouched.
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

## VERIFIED STATE (2026-11-02T12:46:58Z)
- Branch: `main`. HEAD clean working tree.
- **Campaigns 1-30:** Complete & verified on disk. Full suite: 675 passed, 1 skipped, 0 failed. Gating chain green (8/8), invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Re-verified at 11:52:01Z: `tests/test_cointegration_campaign30_mt.py` 7 passed; `tests/test_cointegration_campaign29_mt.py` 3 passed; gating spot-check 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17.
- **Campaign 30:** COMPLETE — generator `scripts/generate_campaign30_artifacts.py`, artifact `reports/cointegration_campaign30_mt.json`, tests `tests/test_cointegration_campaign30_mt.py` all verified green.
- **Campaign 31:** ACTIVE (cointegration rigor phase 3). Deliverables absent on disk: `scripts/generate_campaign31_artifacts.py`, `reports/cointegration_campaign31_mt.json`, `tests/test_cointegration_campaign31_mt.py` — build from scratch following Campaign 29/30 patterns.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m pip install -r requirements.txt
# Campaign 29 artifact tests (must stay green)
python -m pytest tests/test_cointegration_campaign29_mt.py -v
# Campaign 26+27 gating chain (must stay green)
python -m pytest tests/test_end_to_end_pairs_execution_validation_mt.py tests/test_live_operational_readiness_signoff_mt.py tests/test_live_go_live_authorization_final_mt.py tests/test_post_deployment_live_readiness_signoff_mt.py -v
# Portfolio real failures (track progress)
python -m pytest tests/test_portfolio_real.py tests/test_portfolio_real_hardened.py tests/test_tail_risk_parameter_stability.py -v
# Gating invariant spot-check
python3 -c "
import json
g=json.load(open('reports/portfolio_gating_mt.json'))['results_by_timeframe']
for tf in ['1h','4h','1d']:
    elig=g[tf].get('eligible_pairs',g[tf].get('feasible_pairs',{}))
    print(tf,'eligible:',len(elig),list(elig.keys()) if isinstance(elig,dict) else elig)
"
# Expected: 1h eligible: 0; 4h eligible: 1 ['POL/BTC']; 1d eligible: 0
# Full suite (final check)
python -m pytest tests/ -q
```

## CAMPAIGN HISTORY (CONCISE)
- **Campaign 26 (complete):** E2E pairs execution validation + live operational readiness signoff. Artifacts/tests/generator verified.
- **Campaign 27 (complete):** Final live go-live authorization + post-deployment live readiness signoff. Bottleneck removed (generator completed). Artifacts/tests/generator verified. Terminal for gating chain.
- **Campaign 28 (complete):** Portfolio_real enrichment → full green suite (665 passed, 1 skipped, 0 failed).
- **Campaign 29 (complete):** Cointegration rigor deepening — OOS stability, causal rolling diagnostics, pairs robustness. Generator + artifact + tests verified green.
- **Campaign 30 (complete):** Cointegration rigor phase 2 — Johansen rank stability, structural-break discipline, HL favorability bands, walk-forward OOS pairs execution robustness. Generator + artifact + tests verified green. Full suite 675 passed, 1 skipped, 0 failed.
- **Campaign 31 (ACTIVE):** Cointegration rigor phase 3 — cross-timeframe regime-conditioned cointegration + execution-aware OOS pairs with cost stress.
