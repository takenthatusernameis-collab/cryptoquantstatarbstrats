# SINGLE DURABLE HANDOFF | 2026-11-01T05:15:05Z | INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-11-01T05:15:05Z)
- Branch: `main`, working tree clean (latest commits: 79be9ee, 4617928 checkpoints).
- `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py:47`. Causality tested; cointegration diagnostics schema tests pass (10/10). Ruff clean.
- `reports/portfolio_real.json` exists (767399 bytes), computed 2026-10-31T17:36:18Z, real_data_only=true, fabricated_data=false.
- From current artifact diagnostics (17 pairs total): **ALL 17 pairs fail `all_pass`**.
- **POL/BTC** passes EG (`p<0.001`), Johansen (rank>=1), spread MR, HL bounds (107.7, in range), leg stationarity tests pass, but **rolling_stable_ok=False** (`frac_significant_0_05~0.049`, only ~9/184 windows pass out of 184 windows of 720 bars with step 24). Marked `blocked_or_insufficient_data` with `blocked_routes` containing `rolling_stability` failure + provenance (empty blocked_routes bottleneck was fixed in code).
- All other 16 pairs fail multiple gates (EG mostly false).
- **BOTTLENECK:** Artifact was generated with old code path? The code now auto-blocks failing pairs with full `blocked_routes` and provenance (per HANDOFF/history), and current POL/BTC already shows blocked_routes populated. But need to **regenerate** to ensure consistency with latest code/state.
- **PRIMARY TARGET:** POL/BTC rolling stability regime-dependence — only pair close to passing.

## IMMEDIATE INITIAL TASK (START HERE — NO DEVIATION)
**OBJECTIVE:** Close the cointegration rigor loop on real data. For every pair, either (a) pass ALL 7 enriched gates on real Binance data, or (b) be honestly marked `blocked_or_insufficient_data` with full provenance. Do not weaken thresholds. Do not fabricate.

**MANDATORY FIRST ACTIONS (EXECUTE IN ORDER, NO SKIPPING):**
1. **Regenerate `reports/portfolio_real.json` with honest blocking.** Run `python -u examples/run_portfolio_real.py`. Confirm every pair with `all_pass=False` has `status: "blocked_or_insufficient_data"`, non-empty `blocked_routes[]`, detailed `rationale` with full provenance (`source`, `real_data_only`, `fabricated_data:false`, `computed_at`). POL/BTC must remain blocked until proven stable. **Empty `blocked_routes` on a failing pair is a blocker itself.**
2. **Deep dive POL/BTC regime-dependence.** Load full POL/BTC from real Binance via `data.loader.DataLoader.load_binance_data`. Analyze the 9 passing windows (indices ~7,64,65,114,119,120,121,147,182). Check hedge ratio stability, vol regimes, ADF/KPSS of spread per regime, structural breaks. Determine if regime-dependent or fundamentally unstable.
3. **Test window sensitivity rigorously.** Try alternative `window`/`step` for `rolling_cointegration_stability` (e.g., 400,500,600,800,1000; steps 12,24) only to diagnose. **Do NOT change the pass criterion (>=60% significant at 5%) without ironclad evidence + tests.**
4. **Decide honestly.** If fundamental instability with no regime passes strict bar → mark blocked with full provenance. If regime-dependent and tradeable only in specific regimes → design **causal regime filter (trailing-only, no lookahead)**, prove with tests, ensure strategy only enters in those regimes. Otherwise block.
5. **Sweep remaining 16 pairs.** Diagnose each failing pair; fix if possible with real data only, else block honestly with provenance.
6. **Verify green.** Run all verification commands. All tests must remain green (>=555 passed, 0 failures). Ruff clean. mypy clean.

## EXECUTION PLAN
### 1) REGENERATE ARTIFACT (HIGHEST PRIORITY)
- `python -u examples/run_portfolio_real.py`
- Validate schema: every failing pair has non-empty `blocked_routes`, provenance complete.

### 2) POL/BTC DEEP DIVE
- Files: `utils/cointegration.py`, `strategies/pairs_trading.py`, `data/loader.py`, `examples/run_portfolio_real.py`
- Focus on rolling stability across regimes; hedge ratio stability critical.

### 3) SYSTEMATIC PAIR SWEEP
- Diagnose root causes per pair; honest blocking preferred over weakening gates.

### 4) CAUSALITY & ENFORCEMENT
- Enriched gates remain trailing-only/cached causally. Fail-closed default. No lookahead.

### 5) QUALITY GATES
- Lint/tests/schema must pass.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — isolated tests only with explicit `fabricated_data: true` marker
- **NO SHORTCUTS / NO FABRICATION**
- **PRESERVE GREEN** — >=555 passed, 0 new failures
- **HEAVY MANDATE** — complete full campaign, no coasting
- **COINTEGRATION IS LAW**
- **CAUSAL ONLY** — no lookahead (trailing data only)
- **UNBUFFERED** — use `python -u` for long runs
- **HONEST BLOCKING** — if cannot pass all gates, mark `blocked_or_insufficient_data` with provenance
- **NO EMPTY blocked_routes** on failing pair
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests

## VERIFICATION COMMANDS (MUST RUN)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_strategies.py -v
python -m pytest tests/ -q  # >=555 passed, 0 failures
python -u examples/run_portfolio_real.py  # refresh reports/portfolio_real.json
```

## BOTTLENECK REMOVAL
- Focus singular: cointegration rigor.
- Code now auto-blocks failing pairs with provenance (empty blocked_routes fixed). Artifact needs regeneration.
- POL/BTC is the only pair close to passing — deep dive required.
- If regime filter needed, it must be causal and tested. Otherwise block honestly.

**START NOW. Regenerate artifact with honest blocking, then attack POL/BTC rolling stability first. Heavy work required. No coasting.**
