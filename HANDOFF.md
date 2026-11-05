# HANDOFF (SINGLE DURABLE) — 2026-11-05T08:48:13Z

## JUST COMPLETED (VERIFIED, REAL DATA, FAIL-CLOSED) — DO NOT REDO
- **PRIORITY 5 COMPLETE (A+B+C).** All required artifacts written to `reports/` with `real_data_only=true, fabricated_data=false, fail_closed=true, no_threshold_weakening=true`.
  - **A1** `reports/real_feed_inventory_20261105T084255Z.json`: honest inventory of real cached data NOW (`data/cache` named 1h metas) — **11 assets** (ADA,AVAX,BNB,BTC,DOT,ETH,LINK,LTC,POL,SOL,XRP) × **5112 bars**, **2026-04-01 00:00:00+00:00..2026-10-30 23:00:00+00:00**, `1h`, Binance spot klines via `www.binance.com`, per-asset provenance verified. Family support: spot single-venue strategies supported (limits noted); pairs data present but edge PROVEN BLOCKED; cross-exchange dual-venue/funding-basis-carry/real IV-term-structure = `blocked_no_real_feed`.
  - **A2** `reports/real_feed_unblock_plan_20261105T084447Z.json`: concrete unblock plan per blocked family — required real feed/CSV schemas (columns, alignment, frequency, provenance), observed blocked routes (single-venue only; `fapi.binance.com HTTP 451` per prior evidence; no cached real funding/basis/IV), `data_status=blocked_no_real_feed` where true, validation plan if unblocked. No fake workarounds/proxies-as-real-feeds.
  - **B** `reports/spot_alt_signal_costed_oos_20261105T084619Z.json`: **genuinely different** real-spot family `cross_sectional_risk_adjusted_return_rank` (11-asset cross-sectional rank of trailing 7d return / 14d realized vol; long top 25%/short bottom 25%, market-neutral gross 1; `MIN_CROSS=6` fail-closed) on **real cached 1h only** (5112 bars, 11 assets). Rolling WF **720/168** (30d/7d), cost grid **0–40 bps** combos, benchmark **equal-weight B&H (1/N) same 11 assets/WF/costs**, pre-stated `oos_edge_proven` rule. **RESULT (honest, fail-closed): `oos_edge_proven=false`.** OOS net negative and under EW B&H across all 10 slices (0bps OOS −0.00453 vs bench +0.00124; 40bps −0.18328 vs −0.00276). Exposure real (4775 active bars, 1520 turnover events; BTC/ETH/SOL/BNB participation reported). **No edge claimed; no in-sample tuning.**
  - **C** `reports/strategy_edge_registry_20261105T084647Z.json` (supersedes `reports/strategy_edge_registry_20261105T081456Z.json`): adds B + real-feed inventory/unblock status; blocked families unchanged/honest.
- **Tests (this session):** `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages /home/runner/work/_temp/kilo-home/.local/bin/pytest -q` → **832 passed, 1 skipped, 3563 warnings, 0 failed** (42.41s, full `tests/`). *(Env note: deps installed to user site; PYTHONPATH required. Prior registry recorded 832/1 in its env.)*

## CORE TRUTH (NO PROVEN EDGE; BLOCKED FEEDS HONEST) — DO NOT RE-LITIGATE
- **Pairs cointegration: PROVEN BLOCKED** (fail-closed, 165/165 diagnostic-blocked, 0 breaches) on current real cached universe/window. **Do NOT re-scan/re-audit pairs; do NOT weaken gates** unless a genuinely NEW real dataset is added.
- **Momentum (0/11), mean_reversion (0/11), cross_sectional_risk_adjusted_return_rank (fail-closed): NO PROVEN NET-OF-COST OOS EDGE** on real cached spot 1h 2026-04-01..2026-10-30 (rolling 30d/7d, 0–40bps, vs stated benchmarks). Treat as beta-like/unproven; **do not claim edge; do not in-sample tune and present as edge**.
- **Cross-exchange (dual-venue same-asset), funding/basis/carry, term_structure/real IV-vol surface: BLOCKED_NO_REAL_FEED.** Honest only. **No fabricated candles/IV/funding/basis/dual-venue feeds. No proxies labeled as real feeds** (spot-vol ≠ IV surface; spot-derived ≠ real funding/basis).

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (HEAVY, BINDING)
**PRIORITY 6 — HEAVY REAL-DATA CAMPAIGN #2 (NO REHASH) + FEED UNBLOCK EXECUTION (IF REAL DATA PROVIDED).** Every session leaves **>=2 new concrete artifacts in `reports/`**. No investigation-only. Real data only. Never fabricate. No threshold weakening. Do not re-litigate pairs. Commit nothing unless explicitly asked.

### Required Deliverable A — `reports/spot_breakout_volfilter_costed_oos_<UTC>.json` (HEAVY, REAL SPOT ONLY, GENUINELY DIFFERENT)
Execute a **new, pre-stated** real-spot signal family different from momentum/mean_reversion/cross-sectional rank: e.g. **Donchian/channel breakout with a volatility-regime filter** (enter on N-bar high/low breakout only when realized vol in a specified band; exit on channel mid or stop; long/short or long-flat — state choice) **OR** an equally distinct, pre-specified variant. Use **only real cached 1h** (`data/cache/*_2026-04-01_2026-10-30_1h.pkl`, 11 assets, 5112 bars). **No new external feeds, no gate weakening, no proxies as new feed types.**
- Rigor: cost grid (>= {0,5,10,20} bps combos), rolling WF (explicit train/test/step, e.g. 720/168), IS/OOS, benchmark (asset B&H and/or EW B&H as appropriate — state), exposure/trade counts, **pre-stated `oos_edge_proven` rule**, per-asset (BTC,ETH,SOL,BNB) + aggregate over 11.
- `oos_edge_proven=false` is a valid, required fail-closed outcome — report honestly. **Do not tune parameters in-sample to manufacture edge.**

### Required Deliverable B — `reports/real_feed_unblock_status_<UTC>.json` (+ ingest artifacts ONLY if real feeds added)
1) Re-check `data/cache`/repo for **any newly added real feeds** (funding, basis/spot-perp, dual-venue, real IV). If **none added**: produce an honest status artifact confirming still `blocked_no_real_feed` per family, referencing `reports/real_feed_inventory_20261105T084255Z.json` + `reports/real_feed_unblock_plan_20261105T084447Z.json` and the exact schemas still required.
2) **If and only if genuinely new real feed files are present with provenance**: ingest and run the **smallest fail-closed validation** for that family (net-of-cost/fees stated; no fabrication), producing `reports/<family>_real_validation_<UTC>.json`. **Do not fake feeds.**

### Required Deliverable C — supersede registry: `reports/strategy_edge_registry_<UTC>.json`
Update with Deliverable A (+ B validation if any). Keep blocked families honest/unchanged unless NEW real feed evidence is added. Rerun full `tests/` (record exact command/env note — deps may require `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages` and user-site pytest) and record counts. `supersedes` the 20261105T084647Z registry.

## BOTTLENECK REMOVAL / RULES (BINDING)
- **Real data only.** No fabricated candles/IV/funding/basis/dual-venue feeds.
- **No threshold weakening.** No gate relaxation to manufacture an edge.
- **No proxies labeled as real feeds.**
- **Pairs blocked** — do not re-scan/re-audit without a genuinely NEW real dataset.
- **No investigation-only sessions. Every session leaves >=2 concrete artifacts in `reports/`.** This session requires A+B+C (>=3).
- **Env note (remove test bottleneck):** in this runner deps live at `/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages` and pytest at `/home/runner/work/_temp/kilo-home/.local/bin/pytest`; run with `PYTHONPATH=.../site-packages .../pytest -q`.
- Commit nothing unless explicitly asked.

## KEY ARTIFACTS (CANONICAL)
- `reports/strategy_edge_registry_20261105T084647Z.json` (LATEST consolidated; supersede next session)
- `reports/spot_alt_signal_costed_oos_20261105T084619Z.json` (P5B, `oos_edge_proven=false`, do not redo)
- `reports/real_feed_inventory_20261105T084255Z.json` (P5A1)
- `reports/real_feed_unblock_plan_20261105T084447Z.json` (P5A2)
- `reports/momentum_mr_costed_oos_20261105T081323Z.json` (P4, 0/11 & 0/11)
- `reports/pairs_failclosed_audit_20261105T075431Z.json` (PASS fail-closed, do not redo)
- `reports/funding_basis_blocked_20261105T075839Z.json`
- `reports/cross_exchange_real_market.json` (dual-venue blocked / single-venue only)
- `reports/portfolio_real.json`
