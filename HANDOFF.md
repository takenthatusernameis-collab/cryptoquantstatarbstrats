# HANDOFF (SINGLE DURABLE) — 2026-11-05T08:02:15Z

## JUST COMPLETED (VERIFIED, REAL DATA, FAIL-CLOSED) — DO NOT REDO
- **PRIORITY 2 (pairs fail-closed audit): COMPLETE.** `scripts/pairs_failclosed_audit.py`; `reports/pairs_failclosed_audit_20261105T075431Z.json` — 165/165 pair×TF audited (11 symbols × 55 pairs × {1h,4h,1d}, real cached Binance spot 2026-04-01..2026-10-30). `n_diagnostic_blocked=165, n_zero_exposure_when_blocked=165, n_breaches_fail_closed=0, overall_pass_fail_closed=true`. Provenance: `real_data_only=true, fabricated_data=false, fail_closed=true, no_threshold_weakening=true`.
- **PRIORITY 3 (edge registry + per-family verification): COMPLETE.** Consolidated, evidence-backed registry across all stat-arb families using ONLY real/cached data or honest blocked status:
  - `reports/strategy_edge_registry_20261105T080215Z.json` (top-level + per-family: data_status, diagnostic_evidence w/ key metrics, `strategy_honors_fail_closed`, actionable_next_step, provenance).
  - `reports/funding_basis_blocked_20261105T075839Z.json` (honest blocked: `fapi.binance.com HTTP 451` env route, no cached real funding/basis/perp-spot series; `real_data_only=true, fabricated_data=false`).
  - Verifications (real cached spot, 5112 bars, 2026-04-01..2026-10-30 1h, 11 assets): pairs audit consistency asserted; cross-exchange `reports/cross_exchange_real_market.json` honesty confirmed (native dual-venue blocked, single-venue spot only, replay -2.22% vs B&H +15.59%); momentum & mean_reversion signal-generation sanity on real spot (per-asset, `enriched_gates_ok` present, strict gates default) — **signals nonzero but NOT net-of-cost/OOS validated**; term_structure fail-closed (requires real IV-tenor columns, none present); volatility_surface run is **spot-proxy ONLY** (no real IV/options surface) — must NOT be presented as real IV-surface edge.
  - `pytest -q` (full `tests/`): **832 passed, 1 skipped, 0 failed, 3567 warnings, 51.73s**.

## CORE STATE (FAIL-CLOSED, NO PROVEN EDGE)
- **Pairs cointegration: PROVEN BLOCKED** on current real cached universe/window. Do NOT re-scan pairs, do NOT weaken gates, do NOT fabricate data.
- **Cross-exchange (dual-venue), funding/basis/carry, term-structure, real IV surface: BLOCKED_NO_REAL_FEED** — honest only; no fabricated candles/IV/funding/basis/dual-venue feeds.
- **Momentum / mean_reversion: real-spot signals exist but EDGE UNPROVEN** until net-of-cost, walk-forward IS/OOS, benchmark-relative validation on real cached spot. No edge claim without it.

## INITIAL TASK MESSAGE (for next agentic session)
**PRIORITY 4 — HEAVY NET-OF-COST OOS VALIDATION (REAL SPOT ONLY) + KEEP BLOCKED FEEDS HONEST.**
You must leave >=2 new concrete artifacts in `reports/`. No "investigation-only" sessions. Real data only. Never fabricate. No threshold weakening. Do not re-litigate pairs. Commit nothing unless explicitly asked.

### Required Deliverable A — `reports/momentum_mr_costed_oos_<UTC>.json` (HEAVY, REAL DATA)
Run full **costed walk-forward (IS/OOS) + benchmark-relative** validation for `momentum` and `mean_reversion` on **real cached Binance spot 1h** (`data/cache/*_2026-04-01_2026-10-30_1h.pkl`, 11 assets, 5112 bars). For each (family × asset, at minimum BTC,ETH,SOL,BNB + report aggregate across all 11):
- Use real spot only; declare provenance per run (`real_data_only=true,fabricated_data=false,fail_closed=true,no_threshold_weakening=true`).
- Cost model: sweep fees+slippage grid consistent with repo conventions (e.g. `{0,5,10,20} bps` combos as applicable) and report net-of-cost metrics.
- Walk-forward: rolling/anchored with explicit `train/test/step` (or repo WF utility) — report IS vs OOS (return, Sharpe/Sortino as available, maxDD, hit-rate/trades) and **benchmark-relative** (buy-and-hold of the asset on same window). Mark `oos_edge_proven: true/false` with an explicit, pre-stated rule (e.g. net-of-cost > 0 across cost grid slices you test AND beats benchmark in OOS) — fail-closed if not met.
- Honor `enriched_gates_ok`/strategy fail-closed behavior; record actual exposure/trade counts.
- This is the **main heavy task**. Prefer reusing `backtest/` + `examples/run_*cost*`/WF utilities; if a family’s API requires adaptation, do the minimal honest wiring and document it in-artifact.

### Required Deliverable B — update consolidated truth: `reports/strategy_edge_registry_<UTC>.json` (supersedes prior)
Re-emit a full registry (same schema intent as `strategy_edge_registry_20261105T080215Z.json`) that **replaces/supersedes** it by incorporating Deliverable A’s net-of-cost OOS results for momentum/mean_reversion (so they are no longer "unproven pending WF" if validated, or explicitly "no OOS edge" if not). Keep pairs/cross-exchange/funding-basis/term-structure/IV statuses honest and unchanged unless you add NEW real feed evidence. Include `pytest -q` counts (rerun; full `tests/`).

### Bottleneck removal / rules (binding)
- **Real data only.** No fabricated candles/IV/funding/basis/dual-venue feeds. Fail-closed on missing/blocked.
- **No threshold weakening.** No gate relaxation to manufacture an "edge".
- **No proxies labeled as real feeds.** (spot-vol ≠ IV surface; spot-derived ≠ real funding/basis).
- **Pairs stay blocked** — do not re-scan/re-audit unless a genuinely new real dataset is added.
- **Every session leaves >=1 new concrete artifact in `reports/`.** This session requires >=2.
- Commit nothing unless explicitly asked.

## KEY ARTIFACTS (canonical)
- `reports/strategy_edge_registry_20261105T080215Z.json` (latest consolidated; supersede with a new timestamped registry when updated)
- `reports/pairs_failclosed_audit_20261105T075431Z.json` (PASS, fail-closed, do not redo)
- `reports/funding_basis_blocked_20261105T075839Z.json`
- `reports/cross_exchange_real_market.json` (dual-venue blocked / single-venue only)
- `reports/portfolio_real.json`
- `reports/pairs_leg_stationarity_*` memos (pairs blocked context)
