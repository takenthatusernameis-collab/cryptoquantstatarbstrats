# DURABLE HANDOFF (2026-10-30T08:58:12Z) — SINGLE MANDATORY NEXT TASK: RELENTLESS REAL-DATA PORTFOLIO HARDENING & AGGRESSIVE EXPANSION

## REPO NAME PRIORITIZATION (DRIVES ALL DECISIONS)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **INFERRED MANDATE:** Continuously validate crypto statistical-arbitrage strategies on **REAL market data** (public Binance spot, no API keys, no fabricated candles/IV/funding). **Coasting is forbidden. Heavy validation must never stop.**

## VERIFIED GREEN STATE (DO NOT REGRESS) — confirmed 2026-10-30T08:58:12Z
- **Branch:** `main` (clean, up to date with `origin/main`)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **516 passed, 1 skipped** (portfolio tests added; all passing)
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed**
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files**
- **Data access:** Public Binance reachable; `DataLoader.load_binance_data()` works. **NEVER substitute synthetic/fabricated data for real candles/IV/funding.**
- **Deliverables present:** `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py` all exist.

## BOTTLENECKS / BLOCKERS
- **NONE ACTIVE.** Working tree clean. Remove any discovered inefficiencies immediately.

## CAMPAIGN STATUS: IN-PROGRESS / REQUIRES AGGRESSIVE HARDENING
Portfolio construction is implemented and validated. The mandate requires **relentless continuation** - extend, stress-test, and harden on real data without diminishing effort.

## MANDATORY HEAVY CAMPAIGN (HIGHEST PRIORITY - DO NOT DEFER)
You must push this further with maximum intensity. No stopping early.

### REQUIRED DELIVERABLES (ALL MUST EXIST AND BE JSON-SERIALIZABLE)
1. **Extended portfolio validation** - Expand universe further where real data exists (add BTC/BNB, ETH/BNB, SOL/BNB, others) while preserving all pairs with sufficient history. Do not fabricate missing data.
2. **Deeper walk-forward** - Increase rigor: train=1000/test=200, **>= 10 splits** (or maximum feasible with real data). Document IS/OOS stability, degradation, regime-splits.
3. **Stronger regime-adaptive meta-selector** - Harden meta-selector using multiple real regime signals (vol, trend/mean-reversion regime from real data). Validate OOS. Must remain fully real-data driven.
4. **Robust portfolio risk controls** - Strengthen controls (tighter caps, correlation-aware limits, CVaR-based sizing), add circuit breaker logic tested on real history. Keep deterministic and testable.
5. **Real funding/basis integration** - Aggressively attempt real public Binance funding rates and spot/futures basis from public endpoints. If retrieved, incorporate into portfolio costs/tilts where sensible; if not, document exhaustive attempts with timestamps/hosts. **NEVER fabricate.**
6. **Execution realism** - Extend with volume-aware/slippage/cost realism using real data characteristics where possible; document assumptions.
7. **Comprehensive reporting** - Enrich `reports/portfolio_real.json` with per-asset contribution, turnover, leverage, correlation stability, tail metrics (VaR/CVaR/CDaR), regime-conditioned performance, and cost-stress slices.
8. **Stress tests** - Add network-independent stress tests for portfolio logic, risk controls, meta-selector, and artifact schema. Expand coverage.
9. **Documentation** - Update `README.md` with hardened findings, concrete numbers from real data, and explicit notes about data provenance (real-only).

### SUCCESS CRITERIA (ALL MUST PASS)
- [ ] Universe extended using only real data where available
- [ ] Walk-forward >= 10 splits with full IS/OOS reporting
- [ ] Hardened regime-adaptive meta-selector validated OOS
- [ ] Strengthened portfolio risk controls implemented and tested
- [ ] Real funding/basis attempts exhaustive and documented (or integrated if successful)
- [ ] Enriched `reports/portfolio_real.json` with all required metrics
- [ ] Expanded network-independent tests passing
- [ ] `README.md` updated with hardened portfolio findings
- [ ] `PYTHONPATH=. python -m pytest tests/ -q` → >= 516 passed, 0 new failures
- [ ] `python -m ruff check backtest/ strategies/ utils/ tests/` → clean
- [ ] `python -m mypy backtest/ strategies/ utils/` → clean

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-10-30T08:58:12Z)

**OBJECTIVE:** Relentlessly harden and expand multi-asset crypto stat arb portfolio on **REAL Binance data**. Repo name `cryptoquantstatarbstrats` demands maximum heavy validation. **Do not coast. Do not stop early. Remove bottlenecks.**

**CONTEXT:**
- Repo: `cryptoquantstatarbstrats`
- State: GREEN (tests/lint/mypy clean). Portfolio campaign complete with artifacts/tests present.
- Mandate: Extend validation aggressively with real data only; never fabricate.

**REQUIRED ACTIONS (EXECUTE IN ORDER, HEAVY):**
1. **Audit** - Review `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `backtest/engine.py` (walk_forward_portfolio), `utils/portfolio_risk.py`, `utils/regime.py`. Identify gaps and bottlenecks.
2. **Expand universe** - Try to add real pairs (e.g. BTC/BNB, ETH/BNB, SOL/BNB) using `DataLoader.load_binance_data()`; only include pairs with sufficient overlapping real history. Update artifacts.
3. **Harden walk-forward** - Run >=10 splits (train=1000/test=200). Include full IS/OOS series and stability metrics.
4. **Strengthen meta-selector & risk** - Multi-signal regime detection, correlation-aware/cVaR-aware limits, circuit breaker with real-history testing.
5. **Real funding/basis** - Exhaustive attempts to fetch funding/basis from public endpoints; integrate if valid, else document.
6. **Enrich artifact** - Update `reports/portfolio_real.json` with contributions, turnover, tail metrics, regime-conditioned, cost-stress.
7. **Tests & docs** - Expand network-independent tests; update README.
8. **Verify** - pytest/ruff/mypy all green.

**HARD CONSTRAINTS:**
- **NO FABRICATED DATA.** Omit/document if unavailable. Never fabricate candles/IV/funding/basis.
- **REAL DATA ONLY.** All inputs from real public sources.
- **PRESERVE GREEN.** Never break tests/lint/types.
- **HEAVY WORK MANDATE.** Substantial hardening required. Complete fully.
- **REMOVE BOTTLENECKS.** Fix any inefficiencies blocking progress.

**START IMMEDIATELY. EXECUTE THE FULL CAMPAIGN.**
