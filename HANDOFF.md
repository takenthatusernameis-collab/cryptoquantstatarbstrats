# Durable Handoff (2026-10-30T07:58:06Z) — SINGLE MANDATORY NEXT TASK: BUILD MULTI-ASSET PORTFOLIO CONSTRUCTION (REAL DATA, HEAVY)

## Repo name prioritization (drives everything)
- **REPO:** cryptoquantstatarbstrats — Crypto Quant Stat Arb Strategies
- **CORE MISSION (inferred):** Validate crypto statistical-arbitrage on REAL market data (public Binance spot candles, no API key, no fabricated data). The repo name demands continuous heavy real-market validation. Do not coast.

## Verified green state (do not regress)
- Branch: main, clean, up to date
- Tests: `PYTHONPATH=. python -m pytest tests/ -q` -> 516 passed, 1 skipped
- Lint: `python -m ruff check backtest/ strategies/ utils/ tests/` -> All checks passed
- Types: `python -m mypy backtest/ strategies/ utils/` -> Success: no issues found in 31 source files
- Network-independent tests added; real-data fetching works (www.binance.com accessible). Never substitute fabricated data for real candles.
- Prior campaigns complete: OOS, wider universe (ADA/ETH, XRP/BTC, BNB/ETH), longer walk-forward (train=1000/test=200, 6 splits), execution realism (2,192 fills), regime/cost-stress, paper trading, Monte Carlo.

## Bottlenecks removed / status
- None active. Working tree clean. Focus is forward momentum on portfolio construction.

## MANDATORY HEAVY CAMPAIGN (highest priority, do NOT defer)
No portfolio artifact exists yet. Create the full multi-asset portfolio construction system with real-data validation.

### Required deliverables (all must exist and be JSON-serializable)
1. **Portfolio module/example** - Create `examples/run_portfolio_real.py` following existing patterns (DataLoader.load_binance_data, BacktestEngine, strategies).
2. **Real-data portfolio artifact** - Produce `reports/portfolio_real.json` with: equity curve, per-pair contributions, portfolio Sharpe/Calmar/max drawdown, correlation matrix, risk metrics (VaR/CVaR), leverage/exposure stats. Use real Binance spot 1h candles from 2026-04-01 onward (extend to include wider universe: BTC/ETH, ETH/SOL, BTC/SOL, ADA/ETH, XRP/BTC, BNB/ETH).
3. **Portfolio risk management** - Implement portfolio-level controls (max gross exposure, per-pair caps, drawdown circuit breaker). Add to engine or as wrapper in example; keep consistent with existing codebase style.
4. **Walk-forward portfolio** - Run walk-forward portfolio validation (train=1000/test=200, 6+ splits) on wider universe; report OOS/IS stability in artifact.
5. **Funding/basis extension** - If feasible with real public data (e.g., Binance funding rates via public endpoints), extend to funding-rate-aware carry/basis; otherwise document attempts and use only real available data. NO fabricated IV/candles.
6. **Regime-adaptive meta-selector** - Build meta-selector switching between pairs/mean-reversion/momentum based on detected regime, validated OOS on real data.
7. **Longer-horizon data** - Fetch earlier than 2026-04-01 if possible from public Binance history to widen IS window.
8. **Tests & docs** - Add network-independent tests for new portfolio artifacts/logic. Update README with new findings/artifacts.

### Success criteria (must all pass)
- [ ] `examples/run_portfolio_real.py` exists and follows repo patterns
- [ ] `reports/portfolio_real.json` exists (JSON-serializable, real data only)
- [ ] Portfolio walk-forward results included in reports
- [ ] Regime-adaptive meta-selector implemented and validated OOS
- [ ] Network-independent tests added for new artifacts pass
- [ ] README updated to document portfolio construction findings
- [ ] `PYTHONPATH=. python -m pytest tests/ -q` passes (>=516 passed, 0 new failures)
- [ ] `python -m ruff check backtest/ strategies/ utils/ tests/` clean
- [ ] `python -m mypy backtest/ strategies/ utils/` clean

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-10-30T07:58:06Z)

**OBJECTIVE:** Build multi-asset portfolio construction for crypto stat arb on REAL Binance data. This is the mandated next campaign per repo name.

**CONTEXT:**
- Repo: cryptoquantstatarbstrats (Crypto Quant Stat Arb Strategies)
- State: GREEN (516 passed, 1 skipped; ruff/mypy clean). All prior campaigns complete.
- Gap: No `examples/run_portfolio_real.py`, no `reports/portfolio_real.json`. Must create both.
- Data: Use public Binance spot 1h via DataLoader.load_binance_data() (no API key). Extend window to 2026-04-01 to 2026-10-30 and earlier if available. Wider universe: BTC/ETH, ETH/SOL, BTC/SOL, ADA/ETH, XRP/BTC, BNB/ETH.

**REQUIRED ACTIONS (heavy work, do not stop early):**
1. Study existing patterns: `examples/run_cost_sensitivity_real_portfolio.py`, `examples/run_pairs_real_wider_universe_fast.py`, `backtest/engine.py` (run_portfolio), `strategies/pairs_trading.py`. Follow exact style.
2. Create `examples/run_portfolio_real.py` that constructs combined portfolio from top-ranked pair strategies (or optimized weights), applies portfolio risk controls (max gross exposure, per-pair caps, drawdown circuit breaker), runs walk-forward portfolio validation (train=1000/test=200, 6+ splits), adds regime-adaptive meta-selector logic, attempts funding/basis with real public data if possible.
3. Generate `reports/portfolio_real.json` with equity curve, per-pair contributions, Sharpe/Calmar/max drawdown, correlation matrix, risk metrics, walk-forward results. All from real data only.
4. Add network-independent tests in `tests/` for portfolio artifact schema/logic.
5. Update `README.md` with portfolio construction section.
6. Verify green: pytest, ruff, mypy. Fix any issues.

**CONSTRAINTS:**
- NO fabricated data/IV/candles. If real data unavailable for a feature, omit or document attempts - never fabricate.
- Keep changes minimal and consistent with codebase.
- If tests hang/fail due to env, fix or isolate; never revert green main.
- Follow existing patterns strictly.
- This is heavy work - do not coast. Complete all deliverables.

**START IMMEDIATELY.**
