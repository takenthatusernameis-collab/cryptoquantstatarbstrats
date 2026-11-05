# HANDOFF (SINGLE DURABLE) — 2026-11-05T07:55:00Z

## JUST COMPLETED (VERIFIED, REAL DATA, FAIL-CLOSED)
PRIORITY 2 (end-to-end fail-closed audit) is COMPLETE. Do NOT redo it.
- `scripts/pairs_failclosed_audit.py` (ruff clean)
- `reports/pairs_failclosed_audit_20261105T075431Z.json` — 165/165 pair×TF audited (11 symbols × 55 pairs × 1h/4h/1d, real cached Binance spot 2026-04-01..2026-10-30, `last()` resampling). `n_diagnostic_blocked=165, n_zero_exposure_when_blocked=165, n_breaches_fail_closed=0, overall_pass_fail_closed=true`. Each row asserts `entries==0` whenever `leg_stationarity_ok is False` or `all_pass is False`, with diagnostic gates, blocked_routes, strategy actual exposure (max abs per leg), and full provenance (`real_data_only=true, fabricated_data=false, causal_trailing=true, fail_closed=true, no_threshold_weakening=true`).
- Verification: `pytest tests/test_pairs_real_market.py tests/test_cointegration_diagnostics_schema.py -q` → 28 passed; `ruff` clean on `strategies/pairs_trading.py utils/cointegration.py scripts/pairs_failclosed_audit.py`; `mypy` clean on `strategies/pairs_trading.py utils/cointegration.py`.

## INITIAL TASK MESSAGE (for next agentic session)
CORE PAIRS EDGE IS PROVEN BLOCKED AND FAIL-CLOSED. Do not re-scan pairs, do not weaken gates, do not fabricate data.

## NEXT FOCUS CAMPAIGN — PRIORITY 3 (REAL-DATA EDGE REGISTRY + HEAVY STRATEGY VERIFICATION)
Goal: produce a single consolidated, evidence-backed edge registry across ALL stat-arb strategy families in this repo, using ONLY real/cached data or honest blocked status, and leave >=2 concrete artifacts. This closes open ambiguity and prevents future agents from looping on pairs.

### Deliverable A — `reports/strategy_edge_registry_<UTC>.json`
For each strategy family (pairs/cointegration, cross-exchange, funding/basis/carry, term-structure/vol-surface where present, momentum/mean-reversion if included in repo scope), record:
- `data_status`: `real_verified` | `real_cached_verified` | `blocked_no_real_feed` | `not_applicable` (with exact blocked_routes/hosts/rationale; never fabricate).
- `diagnostic_evidence`: paths to existing real artifacts (e.g. pairs fail-closed audit, leg-stationarity memo, `cross_exchange_real_market.json`, `portfolio_real.json` funding_basis section) with key metrics summarized (not copied wholesale).
- `strategy_honors_fail_closed`: run the relevant real-market example/strategy path against available real cached spot data (BTC/ETH/SOL/ADA/AVAX/BNB/DOT/LINK/LTC/POL/XRP, 2026-04-01..2026-10-30 1h) and record actual entries/exposure/cost-sensitivity outcome; if a native feed is required and unavailable (dual-venue same-asset, fapi/binance futures funding 451 here), record `blocked_no_real_feed` with the exact route and do NOT simulate/fabricate.
- `actionable_next_step`: the smallest real-data-unblocking step (e.g. "provide cached dual-venue same-asset OHLCV CSVs" / "provide real funding-rate CSVs from a permitted source") OR "no viable edge on current real universe/window; deprioritize until new real feed".
- Top-level provenance: `real_data_only, fabricated_data=false, fail_closed=true, no_threshold_weakening=true, computed_at`.

### Deliverable B — per-family verification run(s) producing `reports/*_verification_<UTC>.json`
At minimum: (1) re-verify pairs fail-closed summary is consistent with the audit artifact (no rerun of full scan if already present — read + assert; cheap). (2) run/verify cross-exchange real-market path and confirm its blocked-route/provenance is honest vs available single-venue spot (record outcome). (3) inventory `data/cache` + `reports` for any real funding/basis/IV/term-structure data; if none, emit a `reports/funding_basis_blocked_<UTC>.json` with `blocked_routes` including `fapi.binance.com HTTP 451 (environment)` / any attempted hosts, `real_data_only=true, fabricated_data=false`. (4) run `pytest -q` (full, or the broadest stable subset that completes) and include pass/fail counts in the registry.

### Rules / bottleneck removal
- Real data only. Never fabricate candles/IV/funding/basis/dual-venue feeds. Fail-closed on missing/blocked.
- No threshold weakening. No "investigation-only" sessions — every session must leave >=1 new concrete artifact in `reports/`.
- If a family is blocked by missing real feed, that is a valid, documented outcome — do not spend compute inventing proxies from spot prices as if they were real derivatives/funding data; label any derived proxy explicitly and never present as real feed.
- Commit nothing unless explicitly asked.

## KEY ARTIFACTS (do not recreate)
- `reports/pairs_leg_stationarity_closest_20261105T063013Z.json`
- `reports/pairs_leg_stationarity_impossibility_memo_20261105T065521Z.json`
- `reports/pairs_failclosed_audit_20261105T075431Z.json` (PASS, 165/165 blocked→zero exposure)
- `reports/cross_exchange_real_market.json` (single-venue spot only; native dual-venue blocked)
- `reports/portfolio_real.json` (funding/basis unavailable)
