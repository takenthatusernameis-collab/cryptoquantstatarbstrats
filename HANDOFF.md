# SINGLE DURABLE HANDOFF | 2026-11-02T18:01:47Z | CAMPAIGN 34 ACTIVE | BOTTLENECKS REMOVED | HEAVY WORK REQUIRED | NO COASTING

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T18:01:47Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**STATE:** Campaigns 1-33 COMPLETE & ON-DISK VERIFIED. Full suite green (702 passed, 1 skipped, 0 failed). Campaign 33 deliverables verified: `scripts/generate_campaign33_artifacts.py`, `reports/cointegration_campaign33_mt.json`, `tests/test_cointegration_campaign33_mt.py` (11 tests, all pass). `ruff check` clean. Gating invariants preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
**NEXT FOCUS (COINTEGRATION-FIRST, REAL DATA ONLY):** Campaign 34 — cointegration rigor phase 6: fail-closed kill-switch / circuit-breaker execution that halts capacity (zero weight/fills) when regime-transition stress degrades basket cointegration evidence beyond threshold; regime-transition stress amplification on multi-asset hedge-ratio stability across volatility/trend regime switches; multi-regime basket cointegration walk-forward OOS capacity/rebalancing robustness under stress regimes (high-vol, trend-breakdown) with a monotonic fee × slippage cost-stress grid per regime; breach-alert-driven execution halting (fail-closed, cannot lift gating blocks). Real Binance cached data only. Heavy artifacts/tests/provenance/logs mandatory. No coasting.

**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER, NO SKIPPING)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt` — prevent ModuleNotFoundError.
2. **Verify current state (BLOCKING):** Confirm Campaign 33 tests green, gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), Campaign 33 deliverables present, `ruff check` clean on Campaign 33 files.
3. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable). Campaign 34 is the **ONLY** permitted focus until complete.
4. **Follow existing patterns:** Mirror `scripts/generate_campaign33_artifacts.py`, `reports/cointegration_campaign33_mt.json`, and `tests/test_cointegration_campaign33_mt.py`. Do **not** re-derive Campaigns 26-33.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **[START 2026-11-02T18:01:47Z] CAMPAIGN 34 — COINTEGRATION RIGOR PHASE 6: FAIL-CLOSED KILL-SWITCH/CIRCUIT-BREAKER EXECUTION + REGIME-TRANSITION STRESS AMPLIFICATION ON HEDGE-RATIO STABILITY + MULTI-REGIME WALK-FORWARD OOS CAPACITY/REBALANCING UNDER STRESS (COINTEGRATION-FIRST, REAL DATA ONLY) — HEAVY WORK MANDATORY**
>
> **OBJECTIVE (BLOCKING):** Advance cointegration/pairs-trading rigor beyond Campaign 33. Integrate a **fail-closed kill-switch / circuit-breaker** that halts execution (zero capacity/weight/fills) when regime-transition stress degrades basket cointegration evidence (rank, common stochastic trend, hedge-ratio stability) beyond threshold — blocks cannot auto-lift. Amplify **regime-transition stress on multi-asset hedge-ratio stability** across BTC volatility/trend regime switches via `utils.regime`. Demonstrate **multi-regime basket cointegration walk-forward OOS capacity/rebalancing robustness** under stress regimes (high-vol, trend-breakdown) with a **monotonic fee × slippage cost-stress grid per regime** on real Binance cached data. Quantify how regime transitions degrade hedge-ratio stability and tighten tradable capacity; breach alerts must drive execution halting. Exclusively use real Binance cached data (1h; resample allowed only if derived from real data). No fabrication.
>
> **REQUIRED DELIVERABLES (ON DISK, VERIFIED):**
> 1. **Generator** `scripts/generate_campaign34_artifacts.py` (complete, `main()`, ruff clean). Load real cached data for all symbols in the 17 pairs. Compute regime-transition stress amplification on hedge-ratio stability across regime switches, fail-closed kill-switch/circuit-breaker execution halting (zero capacity when stress threshold breached), multi-regime basket cointegration walk-forward OOS capacity/rebalancing robustness with per-regime monotonic cost-stress grid. Attach **full provenance** (source, real_data_only, fabricated_data, computed_at, blocked_routes, rationale), log every computation step, never fabricate values on blocked routes.
> 2. **Artifact** `reports/cointegration_campaign34_mt.json` with per-portfolio, per-regime, per-regime-transition, per-cost-stress, per-timeframe, and per-kill-switch-state results. Must include provenance, causal windows (trailing only), gating invariants preserved, regime definitions, regime-transition stress, hedge-ratio stability across transitions, kill-switch/circuit-breaker triggers and halted states, cost grid per regime, OOS metrics, basket cointegration tests, common stochastic trend evidence, multi-asset hedge ratios, portfolio spreads, rebalancing robustness under stress, execution-aware capacity allocation with breach alerts driving halts. Must be JSON-serializable with **no NaN/Inf**.
> 3. **Tests** `tests/test_cointegration_campaign34_mt.py` asserting schema, required sections/fields/types, minimum portfolio coverage (all 17 pairs represented), real-data provenance on all sections, **gating invariants preserved exactly** (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed kill-switch behavior (breached stress → zero capacity/weight, cannot auto-lift), **cost-stress monotonicity per regime**, blocked pairs carry zero feasible capacity/weight, regime-transition stress quantified (non-trivial degradation or explicit evidence), breach alerts present and drive halts when capacity constrained, NaN/Inf checks, and campaign flags. **All tests must pass**.
>
> **CONSTRAINTS (NON-NEGOTIABLE):** REAL DATA ONLY. CAUSAL ONLY (trailing windows, no lookahead). PRESERVE GATING INVARIANTS (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). FAIL-CLOSED. KILL-SWITCH / CIRCUIT-BREAKER HALTS EXECUTION ON STRESS BREACH — NO AUTO-LIFT. PROVENANCE MANDATORY ON EVERY COMPUTED SECTION. COST STRESS MUST BE MONOTONIC PER REGIME (higher fees/slippage never improve performance). NO AUTO-LIFT OF BLOCKS. NO FABRICATION. HEAVY MANDATE. BREACH ALERTS REQUIRED WHEN CAPACITY CONSTRAINED AND MUST DRIVE EXECUTION HALTS.
>
> **VERIFICATION (BLOCKING):** `ruff check` clean on touched files; `pytest tests/test_cointegration_campaign34_mt.py -v` passes; Campaign 26-33 tests still green; `pytest tests/ -q` remains green (0 failed).

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — Stale/ambiguous handoff:** HANDOFF.md refreshed to current timestamp with true on-disk state (Campaign 33 complete & verified, Campaign 34 deliverables absent).
- **BOTTLENECK REMOVED — Scope drift:** Campaign 34 is the **ONLY** permitted focus until complete. Campaigns 26-33 artifacts untouched.
- **BOTTLENECK REMOVED — Gating erosion:** Gating invariants codified and must be asserted by tests. Fail-closed enforced; kill-switch halts on stress breach, no auto-lift.
- **BOTTLENECK REMOVED — Execution path:** Follow proven patterns from Campaign 33.
- **BOTTLENECK REMOVED — CI/env:** Install deps first in boot sequence.
- **BOTTLENECK REMOVED — Coasting:** Heavy mandate, explicit deliverables, blocking verification, and "no escape clause" stated.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed only if derived from real data.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean on touched files.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation/position limits; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting/kill-switch/risk constraints never lift gating blocks. Only gated-eligible pairs can be feasible. Kill-switch halts execution on stress breach; cannot auto-lift.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.
- **INCIDENT DISCIPLINE** — every breach must be logged with cause, containment, and audit trail; no silent remediation.

## VERIFIED STATE (2026-11-02T18:01:47Z)
- Branch: `main`. HEAD clean working tree.
- **Campaigns 1-33:** Complete & verified on disk. Full suite green (702 passed, 1 skipped, 0 failed). Gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
- **Campaign 33:** COMPLETE — generator `scripts/generate_campaign33_artifacts.py`, artifact `reports/cointegration_campaign33_mt.json`, tests `tests/test_cointegration_campaign33_mt.py` all verified green (11 tests), ruff clean.
- **Campaign 34:** ACTIVE (cointegration rigor phase 6). Deliverables **absent** on disk: `scripts/generate_campaign34_artifacts.py`, `reports/cointegration_campaign34_mt.json`, `tests/test_cointegration_campaign34_mt.py` — build from scratch following Campaign 33 patterns.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m pip install -r requirements.txt
python -m pytest tests/test_cointegration_campaign33_mt.py -v
python -m pytest tests/ -q
python3 -c "
import json
g=json.load(open('reports/portfolio_gating_mt.json'))['results_by_timeframe']
for tf in ['1h','4h','1d']:
    elig=g[tf].get('eligible_pairs',g[tf].get('feasible_pairs',{}))
    print(tf,'eligible:',len(elig),list(elig.keys()) if isinstance(elig,dict) else elig)
"
```
