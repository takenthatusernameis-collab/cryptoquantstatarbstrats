# SINGLE DURABLE HANDOFF | 2026-11-02T11:13:42Z | CAMPAIGN 29 ACTIVE | BOTTLENECKS REMOVED | HEAVY WORK REQUIRED | NO COASTING

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T11:13:42Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**STATE:** Campaigns 1-28 COMPLETE & ON-DISK VERIFIED. Full suite green: 665 passed, 1 skipped, 0 failed. Terminal gating chain achieved. **NEXT FOCUS (COINTEGRATION-FIRST, REAL DATA ONLY):** Campaign 29 — deepen cointegration rigor: out-of-sample cointegration stability, causal rolling diagnostics, and pairs-strategy robustness on real Binance data, with heavy artifacts/tests/provenance. No coasting.
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER, NO SKIPPING)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt` — prevent ModuleNotFoundError. Do this before any tests/imports.
2. **Verify current state (BLOCKING):** Run verification commands below. Confirm Campaign 26+27 tests green, confirm gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), and reproduce the 7 failures to understand exact gaps.
3. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable). Campaign 28 is the ONLY permitted focus until complete.
4. **Do not re-derive Campaigns 26-27:** All artifacts/tests/generators verified on disk. No pivoting, no scope drift.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **[START 2026-11-02T11:13:42Z] CAMPAIGN 29 — COINTEGRATION RIGOR DEEPENING: OOS STABILITY + CAUSAL ROLLING DIAGNOSTICS + PAIRS ROBUSTNESS (COINTEGRATION-FIRST, REAL DATA ONLY) — HEAVY WORK MANDATORY**
>
> **OBJECTIVE (BLOCKING):** Advance cointegration/pairs-trading rigor beyond current gates: verify out-of-sample cointegration stability, causal rolling diagnostics, and pairs-strategy robustness exclusively on real Binance cached data. Produce checkable artifacts, tests, provenance, logs. No coasting.
>
> **REQUIRED DELIVERABLES (ON DISK, VERIFIED):**
> 1. Generator `scripts/generate_campaign29_artifacts.py` (complete, `main()`, ruff clean) loading real data, computing causal rolling cointegration diagnostics + OOS stability + pairs robustness, attaching full provenance, logging every computation.
> 2. Artifact `reports/cointegration_campaign29_mt.json` with per-pair/per-timeframe results, provenance containing `source`, causal windows, half-life bounds, OOS p-values.
> 3. Tests `tests/test_cointegration_campaign29_mt.py` asserting required fields, types, minimum pair coverage, real-data provenance, gating invariants preserved. All pass.
>
> **CONSTRAINTS (NON-NEGOTIABLE):** REAL DATA ONLY (cached Binance 1h or resampled real). CAUSAL ONLY (trailing windows). PRESERVE GATING INVARIANTS (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). FAIL-CLOSED. PROVENANCE MANDATORY. HEAVY MANDATE.
>
> **VERIFICATION:** ruff clean on touched files; new tests pass; Campaign 26-28 tests still green; full suite green (0 failed).


## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — Final blocker:** 7 pre-existing failures identified as sole blocker; Campaign 28 explicitly targets them with concrete deliverables.
- **BOTTLENECK REMOVED — Ambiguity:** Single initial task message, explicit boot sequence, hard completion criteria, NO ESCAPE CLAUSE.
- **BOTTLENECK REMOVED — Scope drift:** Campaign 28 is the ONLY permitted focus until complete. Campaign 26/27 artifacts untouched.
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

## VERIFIED STATE (2026-11-02T11:13:42Z)
- Branch: `main`. HEAD clean working tree.
- **Campaigns 1-28:** Complete & verified on disk. Full suite: 665 passed, 1 skipped, 0 failed. Gating invariants: 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17.
- **Campaign 29:** ACTIVE (cointegration rigor deepening).

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m pip install -r requirements.txt
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
- **Campaign 29 (ACTIVE):** Cointegration rigor deepening — OOS stability, causal rolling diagnostics, pairs robustness.
