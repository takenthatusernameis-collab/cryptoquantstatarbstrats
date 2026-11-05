# HANDOFF (SINGLE DURABLE) — 2026-11-05T08:16:02Z

## JUST COMPLETED (VERIFIED, REAL DATA, FAIL-CLOSED) — DO NOT REDO
- **PRIORITY 4 (net-of-cost OOS, real spot): COMPLETE.** Heavy walk-forward IS/OOS + benchmark-relative validation for `momentum` and `mean_reversion` on REAL cached Binance spot 1h (`data/cache/*_2026-04-01_2026-10-30_1h.pkl`, 11 assets, 5112 bars, 2026-04-01..2026-10-30). Rolling WF 30d train / 7d test (720/168 bars), cost grid fee+slippage {0,5,10,20} bps combos (0–40 bps total), vs buy-and-hold on same windows/costs. Strategy defaults honored (no threshold weakening; `use_enriched_gates=True, strict_enriched_gates=True`). Pre-stated rule: `oos_edge_proven=true` IFF all cost slices OOS net mean_return>0 AND all slices beat B&H OOS AND exposure/trades>0 (fail-closed).
  - `reports/momentum_mr_costed_oos_20261105T081323Z.json` (210K): **0/11 momentum, 0/11 mean_reversion proven.** Both have exposure but do not beat B&H across all slices (beta-like on this window, not alpha). No edge claim.
  - `reports/strategy_edge_registry_20261105T081456Z.json` (supersedes `strategy_edge_registry_20261105T080215Z.json`): consolidated truth + `pytest -q` **832 passed, 1 skipped, 0 failed** (3555 warnings, 51.20s, full `tests/`).
  - Provenance (all): `real_data_only=true, fabricated_data=false, fail_closed=true, no_threshold_weakening=true`.

## CORE TRUTH (NO PROVEN EDGE; BLOCKED FEEDS HONEST) — DO NOT RE-LITIGATE
- **Pairs cointegration: PROVEN BLOCKED** (fail-closed, 165/165 diagnostic-blocked, 0 breaches) on current real cached universe/window. **Do NOT re-scan/re-audit pairs; do NOT weaken gates** unless a genuinely NEW real dataset is added.
- **Momentum / mean_reversion: NO PROVEN NET-OF-COST OOS EDGE** (0/11 each) on real cached spot 1h 2026-04-01..2026-10-30 (rolling 30d/7d, 0–40bps, vs B&H). Treat as beta-like/unproven; do not claim edge.
- **Cross-exchange (dual-venue same-asset), funding/basis/carry, term_structure, real IV/vol surface: BLOCKED_NO_REAL_FEED.** Honest only. **No fabricated candles/IV/funding/basis/dual-venue feeds. No proxies labeled as real feeds** (spot-vol ≠ IV surface; spot-derived ≠ real funding/basis).

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (HEAVY, BINDING)
**PRIORITY 5 — UNBLOCK REAL-FEED EDGE FAMILIES (HONEST) + RUN ONE HEAVY REAL-DATA CAMPAIGN.** Every session leaves **>=2 new concrete artifacts in `reports/`**. No investigation-only. Real data only. Never fabricate. No threshold weakening. Do not re-litigate pairs. Commit nothing unless explicitly asked.

### Required Deliverable A — `reports/real_feed_unblock_plan_<UTC>.json` + `reports/real_feed_inventory_<UTC>.json` (HONEST, CONCRETE)
1) **Inventory exactly what real cached data exists NOW** (`data/cache` + metas): symbols, bars, windows, intervals, provenance flags, and which families each can/cannot support. Be explicit.
2) **Per blocked family** (cross-exchange dual-venue, funding/basis/carry, real IV/term structure): list the **specific real feed/CSV schema required** (columns, timestamp alignment, venue/instrument, frequency) to run a fail-closed validation; list **blocked routes** observed (e.g. `fapi.binance.com HTTP 451`, single-venue only); state `data_status=blocked_no_real_feed` where true. No fake “workarounds” that fabricate data.
3) Output both artifacts with `real_data_only=true, fabricated_data=false, fail_closed=true`.

### Required Deliverable B — `reports/spot_alt_signal_costed_oos_<UTC>.json` (HEAVY, REAL SPOT ONLY)
Run a **new, genuinely different** real-spot signal family (NOT a rehash of the same momentum/mean_reversion params) with full net-of-cost WF IS/OOS + benchmark-relative on the same real cached 1h universe (11 assets, 5112 bars). Examples of honest directions to evaluate (pick >=1 and execute fully): volatility-adjusted mean reversion variant with distinct lookback/z logic, breakout/range filter hybrid, or cross-sectional rank on real multi-asset returns — **implemented against real cached spot, no new external feeds required, no gate weakening, no proxies labeled as new feed types**.
- Same rigor: cost grid (>= {0,5,10,20} bps combos), rolling WF (explicit train/test/step), IS/OOS, B&H benchmark, exposure/trade counts, pre-stated `oos_edge_proven` rule, per-asset (BTC,ETH,SOL,BNB + aggregate over 11).
- If `oos_edge_proven=false` (likely), report it **fail-closed/honestly** — that is a valid, required outcome. Do not tune in-sample and present as edge.

### Required Deliverable C — supersede registry: `reports/strategy_edge_registry_<UTC>.json`
Update with Deliverable B results + the unblock/inventory status. Keep all blocked families honest/unchanged unless NEW real feed evidence is added. Rerun `pytest -q` (full `tests/`) and record counts. `supersedes` the 20261105T081456Z registry.

## BOTTLENECK REMOVAL / RULES (BINDING)
- **Real data only.** No fabricated candles/IV/funding/basis/dual-venue feeds.
- **No threshold weakening.** No gate relaxation to manufacture an edge.
- **No proxies labeled as real feeds.**
- **Pairs blocked** — do not re-scan/re-audit without a genuinely NEW real dataset.
- **Every session leaves >=2 concrete artifacts in `reports/`.** This session requires A+B+C (3 artifacts).
- Commit nothing unless explicitly asked.

## KEY ARTIFACTS (CANONICAL)
- `reports/strategy_edge_registry_20261105T081456Z.json` (LATEST consolidated; supersede next session)
- `reports/momentum_mr_costed_oos_20261105T081323Z.json` (P4, 0/11 & 0/11, do not redo)
- `reports/pairs_failclosed_audit_20261105T075431Z.json` (PASS fail-closed, do not redo)
- `reports/funding_basis_blocked_20261105T075839Z.json`
- `reports/cross_exchange_real_market.json` (dual-venue blocked / single-venue only)
- `reports/portfolio_real.json`
