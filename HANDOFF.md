# SINGLE DURABLE HANDOFF | 2026-11-01T10:17:01Z | INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-11-01T09:30:34Z)
- Branch: `main`, working tree clean. Up to date with `origin/main`.
- `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py:47`. Enriched gates enforced strictly.
- **CAMPAIGN 1 DONE:** `reports/cointegration_diagnostics_real.json` written (2026-11-01T09:08:32Z) via `examples/run_cointegration_diagnostics_real.py`. Real cached 1h Binance candles (2026-04-01 to 2026-10-30, 5112 bars, all 11 symbols) — no network used. All 17 pairs diagnosed with full gates + `blocked_routes[]` + rationale + provenance.
- **POL/BTC concluded (Campaign 2):** NOT regime-filterable with a trailing-only causal filter. `reports/pol_btc_regime_analysis.json` (computed 2026-11-01T09:47:58Z, real cached data, 184 windows, 9 pass, frac 0.0489) — cointegration holds only in 9/184 sparse scattered windows; no robust trailing-causal regime boundary; hedge ratio eccentric; temporally unstable. **Keep `blocked_or_insufficient_data` with full provenance.** Do NOT weaken `rolling_stability`. No causal filter added.
- **All other 16 pairs:** honestly `blocked_or_insufficient_data`. Every one fails `engle_granger` (no cointegration on this window) plus `rolling_stability`; several also fail `johansen`, `spread_mean_reversion`, `hl_bounds`. Non-empty `blocked_routes[]` recorded for each.
- `reports/portfolio_real.json` (~664KB) still has all 17 pairs `blocked_or_insufficient_data` (gates present but stale); the recomputed artifact is `reports/cointegration_diagnostics_real.json`.
- `reports/.portfolio_real_checkpoint.json` is **0 bytes** (empty). No `reports/portfolio_real_regen.log` exists.
- **REGEN IS NOT RUNNING.** No `run_portfolio_real.py` process. Do not wait for a regen that is not running. Do not block on full portfolio regeneration.
- **BOTTLENECK — TEST SUITE SPEED:** `python -m pytest tests/ -q` exceeds a 5-minute block (too slow for one session). Use targeted invocation instead: `python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_strategies.py -q` (102 passed, 0 failures) plus `python -m ruff check ...` (clean).

## BOTTLENECKS REMOVED / MITIGATED
1. **Regen not running** — resolved by not waiting. Do not attempt to resume/interrupt `run_portfolio_real.py`. Use the fast targeted diagnostic sweep (done) instead of full portfolio/bootstrap.
2. **Empty gates / lost diagnostics** — resolved: `reports/cointegration_diagnostics_real.json` now has full per-pair gates + `blocked_routes[]` + rationale + provenance for all 17 pairs on real cached data. Locked in by tests in `tests/test_cointegration_diagnostics_schema.py` (artifact exists, real-data-only, all 17 pairs, full schema, honest-blocking invariant, POL/BTC blocked only on rolling_stability, no pair passes all gates).
3. **Network dependence** — removed: `DataLoader.fetch_with_provenance(use_cache=True)` reads from `data/cache/`. Diagnostics run locally without hitting Binance.
4. **Test-suite slowness** — mitigated: do not run the full suite in one session; run targeted verification commands. If compute becomes blocking, narrow scope to cointegration diagnostics only.

## SINGLE INITIAL TASK MESSAGE (START HERE — NO DEVIATION)
**OBJECTIVE:** Close cointegration rigor loop. Campaigns 1 & 2 complete. Campaign 2 concluded POL/BTC is temporally unstable → keep blocked with provenance. Next: **Campaign 3 — Honest blocking audit + evidence lock-in** — ensure every blocked pair (all 17) carries non-empty `blocked_routes[]` + rationale + provenance in `reports/cointegration_diagnostics_real.json`, add tests locking the no-pass-all-gates invariant and POL/BTC blocked-only-on-rolling-stability-but-kept-blocked conclusion, verify targeted tests + ruff clean. Then expand rigor: re-examine remaining 16 pairs for any near-miss cointegration signal (rolling stability, EG p-values) and document; no threshold weakening. Heavy work, no coasting.

**MANDATORY FIRST ACTIONS (IN ORDER):**
1. **Load the facts** — Read `reports/cointegration_diagnostics_real.json` for POL/BTC in full (gates, rolling_stability details with passing window start bars 168,1536,1560,2736,2856,2880,2904,3528,4368, provenance). Read `strategies/pairs_trading.py` (enriched gates, fail-closed behavior) and `utils/cointegration.py` (rolling/eg/johansen).
2. **POL/BTC deep dive (highest ROI)** — Analyze passing vs failing windows: hedge ratio stability (rolling OLS), spread behavior, volatility/regime, correlation, ADF/KPSS of spread per regime. Quantify differences with numbers and plots/artifacts if useful, but must be reproducible from cached real data. Prove causality for any regime definition (trailing-only, no lookahead).
3. **Decide POL/BTC fate** —
   - If regime-filterable with a **trailing-only, causal, no-lookahead** filter: design it, add to `strategies/pairs_trading.py` with tests proving no lookahead, verify it only allows trading in passing regimes, integrate with enriched gates (or add a new causal gate). Update diagnostics/schema/tests as needed.
   - If fundamentally/temporally unstable: keep `blocked_or_insufficient_data` with full provenance explaining why. Do NOT weaken `rolling_stability` threshold. Document evidence.
4. **Verify** — Run targeted tests (`python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_strategies.py -q` = 102 passed, 0 failures), `python -m ruff check backtest/ strategies/ utils/ tests/ examples/` clean. Preserve green.

## FOCUS CAMPAIGN (HEAVY WORK REQUIRED — NON-OPTIONAL)
The future agent must not avoid this. Execute in order; each step produces a checkable artifact.

### Campaign 1: Cointegration diagnostics recompute (real data) — COMPLETE
- Files: `utils/cointegration.py`, `examples/run_cointegration_diagnostics_real.py`
- Deliverable: `reports/cointegration_diagnostics_real.json` with per-pair gate values + `blocked_routes[]` + provenance for all 17 pairs, persisted to disk. Tests added in `tests/test_cointegration_diagnostics_schema.py`.
- Gate: `all_pass` must be `True` to trade; otherwise `blocked_or_insufficient_data` with non-empty `blocked_routes`.

### Campaign 2: POL/BTC regime analysis + causal filter (if viable) — NEXT (HEAVY)
- Files: `strategies/pairs_trading.py`, `utils/cointegration.py`, `tests/` (new/updated)
- Analyze hedge ratio stability in passing vs failing windows, vol regimes, correlation structure, ADF/KPSS of spread per regime.
- Question: regime-dependent (tradeable with causal filter) or temporally unstable (unfit)?
- If viable: trailing-only causal regime filter + tests proving no lookahead + integration with enriched gates. Must not touch rolling_stability threshold. Must produce evidence artifact (e.g. `reports/pol_btc_regime_analysis.json`).
- If not viable: update rationale/provenance with concrete evidence, keep blocked. No threshold weakening.

### Campaign 3: Bottleneck removal / iteration speed — ONGOING
- Full `pytest tests/` is too slow for one session (>5 min). Keep using targeted test invocation. If any step blocks > one session on expensive compute, write a fast targeted script (reduce bootstrap, skip multi-timeframe, cache) or narrow scope to cointegration diagnostics only. Preserve schema. Parallelize/cache where possible.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests
- **PRESERVE GREEN** — targeted tests 102 passed, 0 failures; ruff clean
- **CAUSAL ONLY** — no lookahead. Any regime filter must be trailing-only
- **HONEST BLOCKING** — if cannot pass all gates, mark `blocked_or_insufficient_data` with full provenance, non-empty `blocked_routes`
- **HEAVY MANDATE** — no coasting, do the work. Future agents must not avoid Campaign 2

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_strategies.py -q  # 102 passed, 0 failures
```

**START NOW.** POL/BTC regime analysis is the next task. Do not wait on a regen that is not running. Prioritize cointegration rigor above all else.
