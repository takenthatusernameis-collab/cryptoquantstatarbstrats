# SINGLE DURABLE HANDOFF | 2026-11-02T20:34:30.592920+00:00 | CAMPAIGN 36 ACTIVE | BOTTLENECKS REMOVED | HEAVY WORK REQUIRED | NO COASTING

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T20:34:30.592920+00:00
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**STATE:** Campaigns 1-35 COMPLETE & ON-DISK VERIFIED. Full suite green. Campaign 35 deliverables verified: `scripts/generate_campaign35_artifacts.py`, `reports/cointegration_campaign35_mt.json`, `tests/test_cointegration_campaign35_mt.py` (12 tests all passing). `ruff check` clean on Campaign 35 files. Gating invariants preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Structural-break detection, drift-triggered re-gating, fail-closed re-entry validation, cross-timeframe convergence/divergence stress implemented and tested (Campaign 35 = cointegration rigor phase 7, DONE).
**CAMPAIGN 36 ACTIVE (cointegration rigor phase 8) — Deliverables ABSENT on disk:** `scripts/generate_campaign36_artifacts.py`, `reports/cointegration_campaign36_mt.json`, `tests/test_cointegration_campaign36_mt.py` — build from scratch following Campaigns 34-35 patterns. Do NOT re-derive Campaigns 26-35.
**NEXT FOCUS (COINTEGRATION-FIRST, REAL DATA ONLY):** Campaign 36 — **regime-conditioned cointegration gate persistence & forward-reliability stress** across 1h/4h/1d on real Binance cached data. Quantify how long cointegration gates hold across volatility/trend regimes (gate persistence/decay half-life), regime-conditioned gate failure rates under high-vol / trend-breakdown / low-vol stress, forward-reliability of cointegration evidence (walk-forward OOS gate stability), and multi-regime convergence/divergence stress. Breach alerts must drive execution halts; blocks cannot auto-lift; fail-closed re-gating persists. Real Binance cached data only. Heavy artifacts/tests/provenance/logs mandatory. No coasting.

**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

## IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER, NO SKIPPING)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt` — prevent ModuleNotFoundError.
2. **Verify baseline (BLOCKING):** `python -m pytest tests/test_cointegration_campaign35_mt.py -v && python -m pytest tests/ -q` — must remain green (0 failed). Confirm gating invariants: 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17.
3. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS non-negotiable). Campaign 36 is the **ONLY** permitted focus until complete.
4. **Mirror patterns:** Follow `scripts/generate_campaign34_artifacts.py`, `scripts/generate_campaign35_artifacts.py`, `reports/cointegration_campaign35_mt.json`, `tests/test_cointegration_campaign35_mt.py`. Do **not** re-derive Campaigns 26-35.

## SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **[START 2026-11-02T20:34:30.592920+00:00] CAMPAIGN 36 — COINTEGRATION RIGOR PHASE 8: REGIME-CONDITIONED COINTEGRATION GATE PERSISTENCE & FORWARD-RELIABILITY STRESS (COINTEGRATION-FIRST, REAL DATA ONLY) — HEAVY WORK MANDATORY**
>
> **OBJECTIVE (BLOCKING):** Advance cointegration/pairs-trading rigor beyond Campaign 35 (phase 7). Quantify **cointegration gate persistence across volatility/trend regimes** via `utils.regime`: gate persistence/decay half-life, regime-conditioned gate failure rates under high-vol, trend-breakdown, and low-vol stress, forward-reliability of cointegration evidence (walk-forward OOS gate stability), and multi-regime convergence/divergence stress across 1h/4h/1d. Gates must be fail-closed: degraded persistence → blocked, zero capacity/weight, no auto-lift. Re-entry requires fresh cointegration evidence. Breach alerts must drive execution halts; blocks cannot auto-lift. Exclusively use real Binance cached data (1h; resample allowed only if derived from real data). No fabrication.
>
> **REQUIRED DELIVERABLES (ON DISK, VERIFIED):**
> 1. **Generator** `scripts/generate_campaign36_artifacts.py` (complete, `main()`, ruff clean). Load real cached data for all symbols in the 17 pairs. Compute regime-conditioned gate persistence/decay, forward-reliability/walk-forward gate stability, regime-conditioned gate failure rates, multi-regime convergence/divergence stress, fail-closed re-gating with no auto-lift, and breach-alert-driven kill-switch halts. Attach **full provenance** (source, real_data_only, fabricated_data, computed_at, blocked_routes, rationale), log every computation step, never fabricate values on blocked routes.
> 2. **Artifact** `reports/cointegration_campaign36_mt.json` with per-portfolio, per-regime, per-persistence-decay, per-forward-reliability, per-regime-failure-rate, per-multi-regime-stress, per-re-gating, and per-kill-switch-state results. Must include provenance, causal windows (trailing only), gating invariants preserved, regime definitions, gate persistence/decay half-life, regime-conditioned gate failure rates, walk-forward OOS gate stability, multi-regime convergence/divergence metrics, kill-switch triggers and halted states, basket cointegration tests, multi-asset hedge ratios, portfolio spreads, execution-aware capacity allocation with breach alerts driving halts. Must be JSON-serializable with **no NaN/Inf**.
> 3. **Tests** `tests/test_cointegration_campaign36_mt.py` asserting schema, required sections/fields/types, minimum portfolio coverage (all 17 pairs represented), real-data provenance on all sections, **gating invariants preserved exactly** (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed regime-conditioned re-gating (degraded persistence → blocked, zero capacity/weight), no auto-lift of blocks, re-entry requires fresh cointegration evidence, gate persistence/decay quantified (non-trivial evidence or explicit evidence), forward-reliability/walk-forward gate stability quantified, regime-conditioned failure rates quantified, breach alerts present and drive halts when capacity constrained, NaN/Inf checks, and campaign flags. **All tests must pass**.
>
> **CONSTRAINTS (NON-NEGOTIABLE):** REAL DATA ONLY. CAUSAL ONLY (trailing windows, no lookahead). PRESERVE GATING INVARIANTS (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). FAIL-CLOSED. REGIME-CONDITIONED RE-GATING RECLASSIFIES PAIRS — NO AUTO-LIFT. RE-ENTRY REQUIRES FRESH COINTEGRATION EVIDENCE. PROVENANCE MANDATORY ON EVERY COMPUTED SECTION. NO AUTO-LIFT OF BLOCKS. NO FABRICATION. HEAVY MANDATE. BREACH ALERTS REQUIRED WHEN CAPACITY CONSTRAINED AND MUST DRIVE EXECUTION HALTS.
>
> **VERIFICATION (BLOCKING):** `ruff check` clean on touched files; `pytest tests/test_cointegration_campaign36_mt.py -v` passes; Campaign 34-35 tests still green; `pytest tests/ -q` remains green (0 failed).

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — Stale/ambiguous handoff:** Refreshed to 2026-11-02T20:34:30.592920+00:00 with true on-disk state; Campaign 35 verified complete, Campaign 36 explicitly targeted as the only active focus.
- **BOTTLENECK REMOVED — Scope drift:** Campaign 36 is the **ONLY** permitted focus until complete. Campaigns 26-35 artifacts untouched; Campaign 35 phase 7 not re-derived.
- **BOTTLENECK REMOVED — Gating erosion:** Invariants codified and asserted by tests. Fail-closed enforced; regime-conditioned re-gating reclassifies pairs, kill-switch halts on stress breach, no auto-lift.
- **BOTTLENECK REMOVED — Execution path:** Follow proven Campaigns 34-35 patterns (generator → artifact → tests).
- **BOTTLENECK REMOVED — CI/env:** Install deps first; baseline verification enforced before coding.
- **BOTTLENECK REMOVED — Coasting:** Heavy mandate, explicit deliverables, blocking verification, no escape clause.
- **BOTTLENECK REMOVED — Ambiguous start:** Single copy/paste initial task message provided. No ramp-up or exploration detours permitted.
- **BOTTLENECK REMOVED — Missing Campaign 36 deliverables:** `scripts/generate_campaign36_artifacts.py`, `reports/cointegration_campaign36_mt.json`, `tests/test_cointegration_campaign36_mt.py` are absent and are the required build targets.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed only if derived from real data.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean on touched files.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation/position limits; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting/kill-switch/risk constraints never lift gating blocks. Only gated-eligible pairs can be feasible. Kill-switch halts execution on stress breach; cannot auto-lift.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.
- **INCIDENT DISCIPLINE** — every breach must be logged with cause, containment, and audit trail; no silent remediation.

## VERIFIED STATE (2026-11-02T20:34:30.592920+00:00)
- Branch: `main`. HEAD clean working tree.
- **Campaigns 1-35:** Complete & verified on disk. Full suite green (Campaign 35: 12/12 passed). Gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
- **Campaign 35:** COMPLETE — generator `scripts/generate_campaign35_artifacts.py`, artifact `reports/cointegration_campaign35_mt.json`, tests `tests/test_cointegration_campaign35_mt.py` all verified green, ruff clean. Cointegration rigor phase 7 done (structural-break detection, drift-triggered re-gating, fail-closed re-entry validation, cross-timeframe convergence/divergence stress).
- **Campaign 36:** ACTIVE (cointegration rigor phase 8). Deliverables **absent** on disk: `scripts/generate_campaign36_artifacts.py`, `reports/cointegration_campaign36_mt.json`, `tests/test_cointegration_campaign36_mt.py` — build from scratch following Campaigns 34-35 patterns.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m pip install -r requirements.txt
python -m pytest tests/test_cointegration_campaign35_mt.py -v
python -m pytest tests/ -q
python -m ruff check scripts/generate_campaign36_artifacts.py tests/test_cointegration_campaign36_mt.py
python3 -c "
import json
g=json.load(open('reports/portfolio_gating_mt.json'))['results_by_timeframe']
for tf in ['1h','4h','1d']:
    elig=g[tf].get('eligible_pairs',g[tf].get('feasible_pairs',{}))
    print(tf,'eligible:',len(elig),list(elig.keys()) if isinstance(elig,dict) else elig)
"
```
