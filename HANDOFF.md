# DURABLE HANDOFF (2026-10-30T13:42:23Z) — SINGLE MANDATORY NEXT TASK: CRYPTO STAT ARB REAL-DATA MAXIMUM HARDENING

## REPO NAME PRIORITIZATION (NON-NEGOTIABLE)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **INFERRED MANDATE:** Continuously validate crypto statistical-arbitrage strategies on **REAL market data only** (public Binance spot, no API keys, no fabricated candles/IV/funding/basis).
- **PRIORITY:** The repository name IS the directive. Every action must serve real-data stat arb validation. Coasting is forbidden. Heavy validation must never stop. If uncertain, choose the heavier real-data validation path.

## VERIFIED GREEN STATE (DO NOT REGRESS) — re-confirmed 2026-10-30T13:42:23Z
- **Branch:** `main` (clean working tree)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **526 passed, 1 skipped**
- **Lint (authoritative scope):** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed**
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files**
- **Data access:** Public Binance reachable via `DataLoader.load_binance_data()`. **REAL DATA ONLY. NEVER FABRICATE.**
- **Key deliverables present:** `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`

## BOTTLENECKS / BLOCKERS — NONE (ELIMINATE IMMEDIATELY IF THEY APPEAR)
- No known blockers. If any inefficiency emerges (slow paths, redundant work, unclear schemas), **remove it before adding features**. Do not work around bottlenecks.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-10-30T13:42:23Z)

**OBJECTIVE:** Relentlessly harden and expand the multi-asset crypto stat arb portfolio on **REAL Binance data**. This repo demands maximum intensity. **Do not coast. Do not stop early. Future agents must not be able to avoid this work.**

**MANDATORY SEQUENCE (EXECUTE IN ORDER):**

1. **AUDIT (HEAVY)**
   - Review `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`, `backtest/engine.py` (walk_forward_portfolio), `utils/portfolio_risk.py`, `utils/regime.py`.
   - Identify concrete gaps vs the requirements below. Fix bottlenecks immediately.

2. **VERIFY GREEN (NON-NEGOTIABLE)**
   - Run `PYTHONPATH=. python -m pytest tests/ -q`, `python -m ruff check backtest/ strategies/ utils/ tests/`, `python -m mypy backtest/ strategies/ utils/`.
   - **Preserve green.** If anything breaks, fix before proceeding.

3. **EXPAND UNIVERSE (REAL-ONLY)**
   - Attempt to add real pairs (prioritize additional BNB/USDT-quoted pairs and others with sufficient history) using only `DataLoader.load_binance_data()`.
   - Only include pairs with adequate overlapping real history. **Omit and document exclusions** if insufficient/unstable.
   - Update artifacts/tests if schema changes.

4. **HARDEN WALK-FORWARD (RIGOROUS)**
   - Enforce >= **12 splits**, train=1000/test=200 where feasible.
   - Produce full IS/OOS series, stability metrics, degradation analysis, and regime-splits. Make them inspectable in the enriched artifact.

5. **STRENGTHEN META-SELECTOR & RISK CONTROLS (REAL-DRIVEN)**
   - Harden regime-adaptive multi-signal meta-selector using **multiple real regime signals** (vol, trend/mean-reversion) derived from real data. Validate OOS.
   - Strengthen correlation-aware and CVaR-aware limits, enforce hard caps (e.g. no asset gross exposure > correlation cap), and test circuit breaker logic on real history.
   - Keep deterministic and fully testable.

6. **EXHAUSTIVE REAL FUNDING/BASIS (NO FABRICATION)**
   - Attempt real public Binance funding rates and spot/futures basis from **multiple public endpoints/hosts** with timestamps of attempts.
   - If valid and sensible, integrate into costs/tilts with provenance. If not retrievable after exhaustive attempts, **document comprehensively with hosts/timestamps/reasoning**. **Never fabricate.**

7. **EXECUTION REALISM (GROUNDED)**
   - Extend with volume-aware/slippage/cost realism using real data characteristics where possible. Explicitly document assumptions.

8. **ENRICH ARTIFACT (COMPLETE & VALID)**
   - Update `reports/portfolio_real.json` to include (all JSON-serializable): **per-asset contribution**, **turnover**, **leverage/gross/net exposure**, **correlation matrix + correlation stability context**, **tail metrics (VaR/CVaR/CDaR)**, **regime-conditioned performance**, **cost-stress slices**, **funding/basis provenance**, **universe changes + exclusions with rationale**, **walk-forward IS/OOS per split + stability/degradation**.
   - Schema must remain valid and backward compatible or tests updated accordingly.

9. **EXPAND TESTS & DOCS (HARDEN COVERAGE)**
   - Add **network-independent** stress tests for portfolio logic, risk controls, meta-selector, artifact schema, and edge cases.
   - Update `README.md` with hardened findings, **concrete numbers from real data**, explicit **real-data-only provenance**, and a clear summary of coverage.

10. **VERIFY & DELIVER (ZERO REGRESSIONS)**
   - Regenerate `reports/portfolio_real.json` using **real data only**.
   - Run full verification: `PYTHONPATH=. python -m pytest tests/ -q` (>= 526 passed, 0 new failures), `python -m ruff check backtest/ strategies/ utils/ tests/` (clean), `python -m mypy backtest/ strategies/ utils/` (clean).
   - Ensure all required deliverables exist and are JSON-serializable.

**HARD CONSTRAINTS:**
- **REAL DATA ONLY.** No synthetic/fabricated candles/IV/funding/basis.
- **NO SHORTCUTS.** Omit and document if unavailable after exhaustive attempts.
- **PRESERVE GREEN STATE.** Never introduce regressions.
- **HEAVY WORK MANDATE.** Substantial hardening required. Complete the full campaign.
- **REMOVE BOTTLENECKS.** Eliminate any inefficiencies blocking progress immediately.

**CAMPAIGN COMPLETE ONLY WHEN:**
- `reports/portfolio_real.json` enriched with **every** metric above
- `tests/test_portfolio_real.py` (and related tests) cover new logic with **network-independent** tests
- `README.md` documents hardened findings with **concrete real-data numbers** and explicit provenance
- `PYTHONPATH=. python -m pytest tests/ -q` → >= 526 passed, 0 new failures
- `python -m ruff check backtest/ strategies/ utils/ tests/` → clean
- `python -m mypy backtest/ strategies/ utils/` → clean

**START IMMEDIATELY. EXECUTE THE FULL CAMPAIGN WITHOUT EARLY STOP.**
