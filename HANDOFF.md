# HANDOFF (SINGLE DURABLE) — 2026-11-05T07:50:04Z

## INITIAL TASK MESSAGE (for next agentic session)

PRIORITY 1 (CORE EDGE — pairs/spreads/cointegration) is VERIFIED COMPLETE. Do NOT re-run it. Both artifacts exist on REAL Binance spot (cached, 2026-04-01..2026-10-30), fail-closed, causal trailing, no threshold weakening:

1) `reports/pairs_leg_stationarity_closest_20261105T063013Z.json` — 165 entries (55 pairs × 3 TFs 1h/4h/1d), per-leg ADF p-values via `utils.cointegration._leg_stationarity_detail(adf1,adf2)` (adfuller regression='c', autolag='AIC'), sorted by `max(leg1_pvalue,leg2_pvalue)` asc, all gates + eg_pvalue + frac_significant + n_windows + blocked_routes + full_gate_detail present, `n_pass_all_gates=0`, min worst-leg p=0.3223 (>>0.05).
2) `reports/pairs_leg_stationarity_impossibility_memo_20261105T065521Z.json` — per-TF worst-leg distributions (min/median/max, count p<=0.05 = 0 all TFs), top-10 closest pairs with exact p-values, methodology_confirmation (`loader.clean_data`, real `last()` resampling via `resample_ohlc_close`, causal trailing windows, no full-history aggregates), concrete conclusion: no pair passes all gates; leg stationarity blocks all pairs; do not weaken gates.

## NEXT FOCUS CAMPAIGN — PRIORITY 2 (END-TO-END FAIL-CLOSED AUDIT)

The core statistical finding is established: on this real universe/window, leg stationarity fails for every pair, so `leg_stationarity_ok` is false everywhere and `all_pass` is false everywhere. The remaining heavy work is to PROVE the strategy honors this — i.e. that `CointegrationPairsStrategy` (fail-closed, `use_enriched_gates=True`, `strict_enriched_gates=True`) emits ZERO entries/positions for every pair × TF where the diagnostic says blocked, across the full real Binance spot universe (11 symbols × 55 pairs × 1h/4h/1d, 2026-04-01..2026-10-30). This closes the loop between the diagnostic artifacts and actual trading behavior: no fabricated edge where diagnostics say blocked.

Concrete deliverable (>=1 new artifact in `reports/`):
- `reports/pairs_failclosed_audit_<UTC>.json`: for each pair × TF, record diagnostic `leg_stationarity_ok`/`all_pass`/blocked_routes AND the strategy's actual entries/positions/exposure over the same real series; assert `entries == 0` whenever `leg_stationarity_ok is False` or `all_pass is False`; report any violation as a hard fail-closed breach with full provenance (real_data_only, fabricated_data=false, computed_at, blocked_routes, rationale).
- Reuse `examples/run_pair_universe_scan.py` loading pattern + `strategies/pairs_trading.CointegrationPairsStrategy`.
- Run `pytest tests/test_pairs_real_market.py tests/test_cointegration_diagnostics_schema.py -v` and `ruff`/`mypy` on `utils/cointegration.py strategies/pairs_trading.py`.

Do NOT search for a passing pair (none exists on this universe/window). Do NOT weaken gates. Real data only. Fail-closed always.

## VERIFIED STATE
- **Leg stationarity is a genuine, proven blocker.** Cached real 1h (2026-04-01..2026-10-30, n=5112): BTC p=0.6502, ETH p=0.6570, SOL p=0.6707, ADA p=0.4231, XRP p=0.3223 (all >> 0.05). All 55 pairs × 3 TFs: count p<=0.05 = 0; no pair passes all gates. Real data, not tooling.
- PRIORITY 1 artifacts complete (see above).
- Tests green: 35 passed across `test_cointegration_campaign31_mt.py test_cointegration_diagnostics_schema.py test_pairs_real_market.py`. Branch clean. `ruff`/`mypy` clean on `utils/cointegration.py strategies/pairs_trading.py`.

## FILES TO FOCUS ON
- `strategies/pairs_trading.py` (`CointegrationPairsStrategy`, enriched/fail-closed gates)
- `utils/cointegration.py` (`target_schema_diagnostics`, `_leg_stationarity_detail`, gates)
- `examples/run_pair_universe_scan.py` (loading/resampling pattern to reuse)
- `data/cache.py`, `data/loader.py` (`load_cached`, `clean_data`, real `last()` resampling provenance)
- `reports/` (write `pairs_failclosed_audit_<UTC>.json`)

## RULES (NON-NEGOTIABLE)
- Real data only. Never fabricate.
- Fail-closed always.
- No threshold weakening (ADF p<=0.05 unchanged).
- Causal only (trailing). No full-history aggregates as per-bar gates.
- Every session leaves >=1 new concrete artifact in `reports/`. No investigation-only loops.
- Commit nothing unless explicitly asked.
