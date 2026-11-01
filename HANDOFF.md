# SINGLE DURABLE HANDOFF | 2026-11-01T11:28:00Z | INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-11-01T11:28:00Z)
- Branch: `main`, working tree clean. Up to date with `origin/main`.
- `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py:47`. Enriched gates enforced strictly.
- **CAMPAIGN 1 DONE:** `reports/cointegration_diagnostics_real.json` written via `examples/run_cointegration_diagnostics_real.py`. Real cached 1h Binance candles (2026-04-01 to 2026-10-30, 5112 bars, all 11 symbols) — no network used. All 17 pairs diagnosed with full gates + `blocked_routes[]` + rationale + provenance.
- **POL/BTC concluded (Campaign 2):** NOT regime-filterable with a trailing-only causal filter. `reports/pol_btc_regime_analysis.json` (computed 2026-11-01T09:47:58Z, real cached data, 184 windows, 9 pass, frac 0.0489) — cointegration holds only in 9/184 sparse scattered windows; no robust trailing-causal regime boundary; hedge ratio eccentric; temporally unstable. **Keep `blocked_or_insufficient_data` with full provenance.** Do NOT weaken `rolling_stability`. No causal filter added.
- **All other 16 pairs:** honestly `blocked_or_insufficient_data`. Every one fails `engle_granger` plus `rolling_stability`; several also fail `johansen`, `spread_mean_reversion`, `hl_bounds`. Non-empty `blocked_routes[]` recorded for each. Zero pairs pass all gates.
- `reports/portfolio_real.json` (~664KB) still has all 17 pairs `blocked_or_insufficient_data` (gates present but stale); the recomputed artifact is `reports/cointegration_diagnostics_real.json`.
- `reports/.portfolio_real_checkpoint.json` is **0 bytes** (empty). No `reports/portfolio_real_regen.log` exists.
- **REGEN IS NOT RUNNING.** No `run_portfolio_real.py` process. Do not wait for a regen that is not running. Do not block on full portfolio regeneration.
- **BOTTLENECK — TEST SUITE SPEED:** full `pytest tests/` exceeds one session (>5 min block); `tests/test_strategies.py` alone exceeds 120s. Use targeted invocation: `python -m pytest tests/test_cointegration_diagnostics_schema.py -q` = **15 passed, 0 failures in ~1.5s**. `python -m ruff check backtest/ strategies/ utils/ tests/ examples/` = clean.

## BOTTLENECKS REMOVED / MITIGATED
1. **Regen not running** — resolved by not waiting. Do not attempt to resume/interrupt `run_portfolio_real.py`. Use the fast targeted diagnostic sweep instead of full portfolio/bootstrap.
2. **Empty gates / lost diagnostics** — resolved: `reports/cointegration_diagnostics_real.json` now has full per-pair gates + `blocked_routes[]` + rationale + provenance for all 17 pairs on real cached data. Locked in by `tests/test_cointegration_diagnostics_schema.py` (artifact exists, real-data-only, all 17 pairs, full schema, honest-blocking invariant, POL/BTC blocked only on rolling_stability, no pair passes all gates).
3. **Network dependence** — removed: `DataLoader.fetch_with_provenance(use_cache=True)` reads from `data/cache/`. Diagnostics run locally without hitting Binance.
4. **Test-suite slowness** — mitigated: do not run the full suite in one session; run targeted verification commands. If compute blocks, narrow scope to cointegration diagnostics only.

## SINGLE INITIAL TASK MESSAGE (START HERE — NO DEVIATION)
**OBJECTIVE:** Close cointegration rigor loop. Campaigns 1 & 2 complete (POL/BTC temporally unstable → keep blocked with provenance). Next: **Campaign 3 — Honest blocking audit + evidence lock-in + near-miss re-examination** — (a) ensure every blocked pair (all 17) carries non-empty `blocked_routes[]` + rationale + provenance in `reports/cointegration_diagnostics_real.json` and lock it with tests; (b) re-examine the remaining 16 pairs for any near-miss cointegration signal (rolling stability frac_significant, EG p-values, half-life) and document numerically; **no threshold weakening**; (c) POL/BTC deep dive: analyze passing vs failing windows (rolling OLS hedge ratio stability, spread behavior, vol/regime, correlation, ADF/KPSS of spread per regime) to prove causality for any trailing-only regime definition or confirm instability; decide POL/BTC fate — causal trailing-only filter (no lookahead, with tests + gate integration) OR keep blocked with evidence; (d) verify: targeted tests green + ruff clean. Heavy work, no coasting.

**MANDATORY FIRST ACTIONS (IN ORDER):**
1. **Load the facts** — Read `reports/cointegration_diagnostics_real.json` for POL/BTC in full (gates, rolling_stability details with passing window start bars 168,1536,1560,2736,2856,2880,2904,3528,4368, provenance). Read `strategies/pairs_trading.py` (enriched gates, fail-closed behavior) and `utils/cointegration.py` (rolling/eg/johansen/target_schema).
2. **POL/BTC deep dive (highest ROI)** — Analyze passing vs failing windows: hedge ratio stability (rolling OLS), spread behavior, volatility/regime, correlation, ADF/KPSS of spread per regime. Quantify with numbers + reproducible artifacts from cached real data. Prove causality for any regime definition (trailing-only, no lookahead).
3. **Decide POL/BTC fate** —
   - If regime-filterable with a **trailing-only, causal, no-lookahead** filter: design it, add to `strategies/pairs_trading.py` with tests proving no lookahead, verify it only allows trading in passing regimes, integrate with enriched gates (or add a new causal gate). Update diagnostics/schema/tests as needed.
   - If fundamentally/temporally unstable: keep `blocked_or_insufficient_data` with full provenance explaining why. Do NOT weaken `rolling_stability` threshold. Document evidence.
4. **Near-miss re-examination (16 other pairs)** — For each blocked pair, record EG p-value, rolling_stability `frac_significant`, half-life, and whether any gate is a near-miss; document numerically. No threshold weakening.
5. **Verify** — Run `python -m pytest tests/test_cointegration_diagnostics_schema.py -q` (expect green) and `python -m ruff check backtest/ strategies/ utils/ tests/ examples/` (expect clean). Preserve green.

## FOCUS CAMPAIGN (HEAVY WORK REQUIRED — NON-OPTIONAL)
The future agent must not avoid this. Execute in order; each step produces a checkable artifact.

### Campaign 1: Cointegration diagnostics recompute (real data) — COMPLETE
- Files: `utils/cointegration.py`, `examples/run_cointegration_diagnostics_real.py`.
- Deliverable: `reports/cointegration_diagnostics_real.json` with per-pair gate values + `blocked_routes[]` + provenance for all 17 pairs, persisted to disk. Tests in `tests/test_cointegration_diagnostics_schema.py`.
- Gate: `all_pass` must be `True` to trade; otherwise `blocked_or_insufficient_data` with non-empty `blocked_routes`.

### Campaign 2: POL/BTC regime analysis + causal filter (if viable) — COMPLETE (conclusion: unstable, keep blocked)
- Files: `reports/pol_btc_regime_analysis.json`, `strategies/pairs_trading.py`, `tests/`.
- Result: temporally unstable (9/184 windows pass, scattered); keep blocked only on `rolling_stability`; no threshold weakening; no causal filter added.

### Campaign 3: Honest blocking audit + evidence lock-in + near-miss re-examination — NEXT (HEAVY)
- Files: `reports/cointegration_diagnostics_real.json`, `tests/test_cointegration_diagnostics_schema.py`, `strategies/pairs_trading.py`, `utils/cointegration.py`.
- Lock non-empty `blocked_routes[]` + rationale + provenance for all 17 blocked pairs via tests.
- Re-examine 16 other pairs for near-miss cointegration signal; document; no threshold weakening.
- POL/BTC deep dive + fate decision (causal trailing-only filter with no-lookahead tests, OR keep blocked with evidence).
- Verify targeted tests + ruff clean.

### Campaign 4: Bottleneck removal / iteration speed — ONGOING
- Full `pytest tests/` too slow for one session; keep targeted invocation. If any step blocks > one session on expensive compute, write a fast targeted script (reduce bootstrap, skip multi-timeframe, cache) or narrow scope to cointegration diagnostics only. Preserve schema. Parallelize/cache where possible.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests.
- **PRESERVE GREEN** — targeted diagnostics test green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Any regime filter must be trailing-only.
- **HONEST BLOCKING** — if cannot pass all gates, mark `blocked_or_insufficient_data` with full provenance, non-empty `blocked_routes`.
- **HEAVY MANDATE** — no coasting, do the work. Future agents must not avoid Campaign 3.

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/
python -m pytest tests/test_cointegration_diagnostics_schema.py -q  # expect green
```

**START NOW.** POL/BTC regime deep dive and near-miss re-examination are the next tasks. Do not wait on a regen that is not running. Prioritize cointegration rigor above all else.
