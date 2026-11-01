# SINGLE DURABLE HANDOFF | 2026-11-01T08:31:09Z | INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-11-01T08:31:09Z)
- Branch: `main`, working tree clean. Up to date with `origin/main`.
- `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py:47`. Enriched gates enforced strictly.
- `reports/portfolio_real.json` exists (~664KB) with all 17 pairs marked `blocked_or_insufficient_data`. **Gates dicts are empty for every pair** — the detailed per-pair diagnostics (EG/Johansen/rolling_stability etc.) referenced in the prior handoff are **not persisted on disk** and must be recomputed from real data.
- `reports/.portfolio_real_checkpoint.json` is **0 bytes** (empty). No `reports/portfolio_real_regen.log` exists.
- **REGEN IS NOT RUNNING.** No `run_portfolio_real.py` process in `ps aux`. **BOTTLENECK REMOVED: do not wait for a regen that is not running.** Do not block on full portfolio regeneration. Use targeted fast diagnostics instead (see IMMEDIATE INITIAL TASK).
- POL/BTC status on disk: `blocked_or_insufficient_data` with empty gates (must be recomputed/confirmed).

## BOTTLENECKS REMOVED
1. **Regen not running** — resolved by not waiting. Do not attempt to resume/interrupt `run_portfolio_real.py`. Instead run a fast targeted cointegration diagnostic sweep over the 17 pairs on real Binance 1h candles and write per-pair provenance. Full portfolio/bootstrap can be revisited only after the cointegration rigor loop is closed per pair.
2. **Empty gates / lost diagnostics** — current artifact lost detailed per-pair gate values. Recompute via `utils/cointegration.py` + `strategies/pairs_trading.py` gates and persist non-empty `blocked_routes[]` with full rationale for every pair.

## IMMEDIATE INITIAL TASK (START HERE — NO DEVIATION)
**OBJECTIVE:** Close the cointegration rigor loop. For every pair: pass ALL enriched gates on real data OR be honestly blocked with full provenance. No threshold weakening without ironclad evidence+tests. No fabrication. No coasting.

**MANDATORY FIRST ACTIONS (IN ORDER):**
1. **Recompute per-pair diagnostics on real data** — Run a targeted sweep over all 17 pairs in `reports/portfolio_real.json` (`BTC/ETH, ETH/SOL, BTC/SOL, ADA/ETH, XRP/BTC, BNB/ETH, BTC/BNB, SOL/BNB, ADA/BTC, XRP/ETH, BNB/BTC, DOT/BTC, DOT/ETH, POL/BTC, AVAX/BTC, LINK/BTC, LTC/BTC`) using `DataLoader.load_binance_data()` / `www.binance.com` 1h candles (2026-04-01 to 2026-10-30). Persist full gates (`eg_pass`, `johansen_pass`, `spread_mr_pass`, `hl_bounds_pass`, `leg_stationarity_ok`, `rolling_stable_ok`, `all_pass`) + `blocked_routes[]` + rationale + provenance per pair. Artifact: `reports/cointegration_diagnostics_real.json` (or update `reports/portfolio_real.json` in place preserving schema). Do NOT use the slow full portfolio/bootstrap path.
2. **POL/BTC deep dive (highest ROI)** — Confirm whether POL/BTC passes EG (p<0.001), Johansen (rank>=1), leg stationarity, half-life bounds, spread mean reversion, and fails only `rolling_stability` (`frac_significant_0_05~0.049`, ~9/184 windows at p<0.05, window=720 step=24). Analyze passing vs failing windows: hedge ratio stability, vol regime, correlation, ADF/KPSS of spread per regime. Passing window start bars: 168, 1536, 1560, 2736, 2856, 2880, 2904, 3528, 4368.
3. **Decide POL/BTC fate** —
   - If regime-filterable with a **trailing-only, causal, no-lookahead** filter: design it, add to strategy with tests proving no lookahead, verify it only allows trading in passing regimes.
   - If fundamentally/temporally unstable: keep `blocked_or_insufficient_data` with full provenance explaining why. Do NOT weaken `rolling_stability` threshold.
4. **Sweep remaining 16 pairs** — Quick diagnosis; honest blocking is correct if gates fail. Record non-empty `blocked_routes[]` with rationale for each.
5. **Verify** — Run tests (`pytest tests/ -q` >=555 passed, 0 failures), `ruff check` clean, schema tests pass.

## FOCUS CAMPAIGN (HEAVY WORK REQUIRED — NON-OPTIONAL)
The future agent must not avoid this. Execute in order; each step produces a checkable artifact.

### Campaign 1: Cointegration diagnostics recompute (real data)
- Files: `utils/cointegration.py`, `strategies/pairs_trading.py`, `data/loader.py`
- Deliverable: per-pair gate values + `blocked_routes[]` + provenance for all 17 pairs, persisted to disk.
- Gate: `all_pass` must be `True` to trade; otherwise `blocked_or_insufficient_data` with non-empty `blocked_routes`.

### Campaign 2: POL/BTC regime analysis + causal filter (if viable)
- Files: `strategies/pairs_trading.py`, `utils/cointegration.py`
- Analyze hedge ratio stability in passing vs failing windows, vol regimes, correlation structure, ADF/KPSS of spread per regime.
- Question: regime-dependent (tradeable with causal filter) or temporally unstable (unfit)?
- If viable: trailing-only causal regime filter + tests proving no lookahead + integration with enriched gates.

### Campaign 3: Bottleneck removal / iteration speed
- If any step blocks > one session on expensive compute: write a fast targeted script (reduce bootstrap, skip multi-timeframe, cache) OR narrow scope to cointegration diagnostics only. Preserve schema. Parallelize/cache where possible.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests
- **PRESERVE GREEN** — >=555 passed, 0 failures
- **CAUSAL ONLY** — no lookahead
- **HONEST BLOCKING** — if cannot pass all gates, mark `blocked_or_insufficient_data` with full provenance, non-empty `blocked_routes`
- **HEAVY MANDATE** — no coasting, do the work

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_strategies.py -v
python -m pytest tests/ -q  # >=555 passed, 0 failures
```

**START NOW.** Recompute per-pair diagnostics on real data first. POL/BTC regime analysis is next. Do not wait on a regen that is not running.
