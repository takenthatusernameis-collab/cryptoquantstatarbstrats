# DURABLE HANDOFF (2026-10-30T12:48:14Z) — SINGLE MANDATORY NEXT TASK: RELENTLESS REAL-DATA PORTFOLIO HARDENING & EXPANSION

## REPO NAME PRIORITIZATION (DRIVES ALL DECISIONS)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **INFERRED MANDATE:** Continuously validate crypto statistical-arbitrage strategies on **REAL market data** (public Binance spot, no API keys, no fabricated candles/IV/funding/basis). **Coasting is forbidden. Heavy validation must never stop.** The repo name is the mandate: stat arb strategies must be proven on real data, not assumed.
- **PRIORITY:** Every action must serve stat arb validation on real data. If uncertain, do the heavier real-data validation.

## VERIFIED GREEN STATE (DO NOT REGRESS) — re-confirmed 2026-10-30T12:47:20Z
- **Branch:** `main` (clean)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **526 passed, 1 skipped**
- **Lint (authoritative scope):** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed**
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files**
- **Data access:** Public Binance reachable; `DataLoader.load_binance_data()` works. **NEVER substitute synthetic/fabricated data for real candles/IV/funding.**
- **Deliverables present:** `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py` all exist and pass.

## BOTTLENECKS / BLOCKERS — NONE REMAIN (ALL REMOVED)
- All known issues resolved. Working tree clean and green.
- **No open blockers.** If any new inefficiency appears, remove it immediately before adding features.

## CAMPAIGN STATUS
Portfolio construction (12 pairs across 6 symbols, train=1000/test=200, N_SPLITS=12, regime-adaptive multi-signal meta-selector, correlation/CVaR-aware risk controls, per-asset correlation exposure cap enforced, CVaR allocation cap enforced, circuit breaker tested, funding/basis exhaustively attempted with provenance, cost-stress slices, regime-conditioned performance) is implemented, validated on real Binance data, and covered by network-independent tests. **The mandate requires relentless continuation — extend, stress-test, and harden on real data without diminishing effort. Do not stop early.**

## MANDATORY HEAVY CAMPAIGN (HIGHEST PRIORITY - DO NOT DEFER)
You must push this further with maximum intensity. No stopping early. Future agents must not be able to avoid this work: every deliverable below must exist, be JSON-serializable, and pass verification before the campaign is considered complete.

### REQUIRED DELIVERABLES (ALL MUST EXIST AND BE JSON-SERIALIZABLE)
1. **Extended portfolio validation** - Expand universe further where real data exists (additional BNB/USDT-quoted pairs, others) while preserving all pairs with sufficient history. Do not fabricate missing data. Update artifacts and tests if schema changes.
2. **Deeper walk-forward** - Keep rigor high: train=1000/test=200, **>= 12 splits** where feasible. Document IS/OOS stability, degradation, regime-splits.
3. **Stronger regime-adaptive meta-selector** - Harden using multiple real regime signals (vol, trend/mean-reversion from real data). Validate OOS. Must remain fully real-data driven. Document signals used.
4. **Robust portfolio risk controls** - Strengthen controls (tighter caps where justified, correlation-aware limits, CVaR-based sizing), circuit breaker logic tested on real history. Keep deterministic and testable. Enforce caps (no asset gross exposure > correlation cap etc).
5. **Real funding/basis integration** - Exhaustively attempt real public Binance funding rates and spot/futures basis from public endpoints (multiple hosts). If retrieved, incorporate into portfolio costs/tilts where sensible; if not, document exhaustive attempts with timestamps/hosts and reasoning. **NEVER fabricate.**
6. **Execution realism** - Extend with volume-aware/slippage/cost realism using real data characteristics where possible; document assumptions.
7. **Comprehensive reporting** - Enrich `reports/portfolio_real.json` with per-asset contribution, turnover, leverage, correlation stability, tail metrics (VaR/CVaR/CDaR), regime-conditioned performance, and cost-stress slices. All must be present and schema-valid.
8. **Stress tests** - Add network-independent stress tests for portfolio logic, risk controls, meta-selector, and artifact schema. Expand coverage.
9. **Documentation** - Update `README.md` with hardened findings, concrete numbers from real data, and explicit notes about data provenance (real-only).

### SUCCESS CRITERIA (ALL MUST PASS)
- [ ] Universe extended using only real data where available
- [ ] Walk-forward >= 12 splits with full IS/OOS reporting
- [ ] Hardened regime-adaptive meta-selector validated OOS
- [ ] Strengthened portfolio risk controls implemented and tested
- [ ] Real funding/basis attempts exhaustive and documented (or integrated if successful)
- [ ] Enriched `reports/portfolio_real.json` with all required metrics
- [ ] Expanded network-independent tests passing
- [ ] `README.md` updated with hardened portfolio findings
- [ ] `PYTHONPATH=. python -m pytest tests/ -q` → >= 526 passed, 0 new failures (maintain/improve count)
- [ ] `python -m ruff check backtest/ strategies/ utils/ tests/` → clean
- [ ] `python -m mypy backtest/ strategies/ utils/` → clean

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-10-30T12:47:20Z)

**OBJECTIVE:** Relentlessly harden and expand the multi-asset crypto stat arb portfolio on **REAL Binance data**. Repo `cryptoquantstatarbstrats` demands maximum heavy validation. **Do not coast. Do not stop early. Remove bottlenecks.**

**CONTEXT:**
- Repo: `cryptoquantstatarbstrats`
- State: GREEN (tests/lint/types clean). Prior portfolio campaign substantially complete; artifacts and tests present and passing.
- Mandate: Extend validation aggressively with real data only; never fabricate.

**REQUIRED ACTIONS (EXECUTE IN ORDER, HEAVY):**
1. **Audit** - Review `examples/run_portfolio_real.py`, `reports/portfolio_real.json`, `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`, `backtest/engine.py` (walk_forward_portfolio), `utils/portfolio_risk.py`, `utils/regime.py`. Identify gaps and bottlenecks.
2. **Remove bottlenecks** - Confirm `pytest`/ruff/mypy are green; clear any new inefficiencies immediately before adding features.
3. **Expand universe** - Try to add real pairs (e.g. additional BNB/USDT-quoted pairs) using `DataLoader.load_binance_data()`; only include pairs with sufficient overlapping real history. Update artifacts.
4. **Harden walk-forward** - Run >=12 splits (train=1000/test=200). Include full IS/OOS series and stability metrics.
5. **Strengthen meta-selector & risk** - Multi-signal regime detection, correlation-aware/cVaR-aware limits, circuit breaker with real-history testing. Ensure hard enforcement.
6. **Real funding/basis** - Exhaustive attempts to fetch funding/basis from public endpoints; integrate if valid, else document comprehensively.
7. **Enrich artifact** - Update `reports/portfolio_real.json` with all required metrics (per-asset contribution, turnover, leverage/gross/net exposure, correlation matrix/stability context, VaR/CVaR/CDaR, regime-conditioned, cost-stress). Keep JSON-serializable.
8. **Tests & docs** - Expand network-independent tests; update README with hardened findings and concrete real-data numbers.
9. **Verify** - pytest/ruff/mypy all green; no regressions. Regenerate artifact with real data only.

**HARD CONSTRAINTS:**
- **NO FABRICATED DATA.** Omit/document if unavailable. Never fabricate candles/IV/funding/basis.
- **REAL DATA ONLY.** All inputs from real public sources.
- **PRESERVE GREEN.** Never break tests/lint/types.
- **HEAVY WORK MANDATE.** Substantial hardening required. Complete fully.
- **REMOVE BOTTLENECKS.** Fix any inefficiencies blocking progress.

**START IMMEDIATELY. EXECUTE THE FULL CAMPAIGN.**
