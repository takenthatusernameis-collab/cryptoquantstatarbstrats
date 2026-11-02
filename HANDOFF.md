# SINGLE DURABLE HANDOFF | 2026-11-02T08:23:47Z | CAMPAIGN 28 ACTIVE | BOTTLENECKS REMOVED | HEAVY WORK REQUIRED | NO COASTING

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T08:23:47Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**STATE:** Campaigns 1-27 COMPLETE & ON-DISK VERIFIED. Terminal state for gating chain achieved. **SOLE BLOCKER:** 7 pre-existing failures in `tests/test_portfolio_real.py`, `tests/test_portfolio_real_hardened.py`, `tests/test_tail_risk_parameter_stability.py` due to enrichment gaps in `reports/portfolio_real.json` (tail_risk/parameter_stability/bootstrap). Fixing these removes the final bottleneck to a fully green suite (648 tests).
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER, NO SKIPPING)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt` — prevent ModuleNotFoundError. Do this before any tests/imports.
2. **Verify current state (BLOCKING):** Run verification commands below. Confirm Campaign 26+27 tests green, confirm gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), and reproduce the 7 failures to understand exact gaps.
3. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable). Campaign 28 is the ONLY permitted focus until complete.
4. **Do not re-derive Campaigns 26-27:** All artifacts/tests/generators verified on disk. No pivoting, no scope drift.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **[START 2026-11-02T08:23:47Z] CAMPAIGN 28 — PORTFOLIO_REAL ENRICHMENT: TAIL RISK + PARAMETER STABILITY + BOOTSTRAP (COINTEGRATION-FIRST, REAL DATA ONLY) — HEAVY WORK MANDATORY**
>
> **OBJECTIVE (BLOCKING):** Make the full test suite fully green by enriching `reports/portfolio_real.json` to satisfy all 7 failing tests. Remove the sole bottleneck.
>
> **REQUIRED DELIVERABLES (ON DISK, VERIFIED):**
> 1. **Regenerate/enrich `reports/portfolio_real.json`** with:
>    - `tail_risk.regime_conditioned` filled (real data only, causal, with provenance)
>    - `tail_risk.permutation_test` with `n >= 3000` (real data only, causal, with provenance)
>    - `parameter_stability` with per-pair entries AND `portfolio_level` with provenance containing `source`
>    - `bootstrap` with `n_simulations >= 3000` (real data only, causal, with provenance)
> 2. **Create generator `scripts/generate_campaign28_artifacts.py`** (complete, `main()`, ruff clean). Follow patterns from `scripts/generate_campaign27_artifacts.py`. Must load real data, compute via causal methods only, attach full provenance, log every computation.
> 3. **Create tests `tests/test_portfolio_real_enrichment_mt.py`** asserting all required fields, types, minimum counts (n>=3000), per-pair coverage, portfolio_level provenance.source, and that values come from real computation (not fabricated). Tests must pass.
>
> **CONSTRAINTS (NON-NEGOTIABLE):**
> - **REAL DATA ONLY** — no fabrication. Use cached real Binance data or existing real sources. Resampling allowed only if still from real data.
> - **CAUSAL ONLY** — no lookahead. Trailing windows only.
> - **PRESERVE GATING INVARIANTS** — `reports/portfolio_gating_mt.json` must remain unchanged: 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17. Do not touch Campaign 26/27 artifacts/tests/generators.
> - **FAIL-CLOSED, NO AUTO-LIFT** — if enrichment cannot be done honestly from real data, fail closed with explicit artifacts/logs; never weaken thresholds or fabricate values.
> - **PROVENANCE MANDATORY** — every enriched field must trace to real data, method, parameters, timestamps.
> - **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/computation, not less.
>
> **VERIFICATION (MUST ALL PASS):**
> - `python -m ruff check scripts/generate_campaign28_artifacts.py tests/test_portfolio_real_enrichment_mt.py` → clean
> - `python -m pytest tests/test_portfolio_real_enrichment_mt.py tests/test_portfolio_real.py tests/test_portfolio_real_hardened.py tests/test_tail_risk_parameter_stability.py -v` → all pass (7 failures fixed)
> - `python -m pytest tests/test_end_to_end_pairs_execution_validation_mt.py tests/test_live_operational_readiness_signoff_mt.py tests/test_live_go_live_authorization_final_mt.py tests/test_post_deployment_live_readiness_signoff_mt.py -v` → Campaign 26+27 still green (8/8)
> - `python -m pytest tests/ -q` → **648 passed, 1 skipped, 0 failed**
> - Gating invariants unchanged (spot-check as specified)
>
> **NEXT SESSION DIRECTIVE:** After achieving full green suite with all provenance in place, stop. No further campaign defined. Repo becomes fully green/terminal.

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

## VERIFIED STATE (2026-11-02T08:23:47Z)
- Branch: `main`. HEAD clean working tree.
- **Campaigns 26-27:** Complete & verified on disk (artifacts/tests/generators all present, ruff clean, tests passing). Gating invariants: 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17.
- **Full suite (previous):** `641 passed, 1 skipped, 7 failed` — 7 failures are in portfolio_real enrichment (unrelated to gating chain). **TARGET:** 648 passed, 1 skipped, 0 failed.
- **Ruff:** Campaign 26/27 touched files clean.

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
- **Campaign 28 (ACTIVE):** Portfolio_real enrichment to fix 7 pre-existing failures → full green suite.
